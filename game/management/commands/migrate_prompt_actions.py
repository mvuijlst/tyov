"""
Management command to migrate prompt actions from hardcoded file to database.
"""

from django.core.management.base import BaseCommand
from game.models import Prompt
from game.prompt_actions import PROMPT_ACTIONS


class Command(BaseCommand):
    help = 'Migrate prompt actions from hardcoded file to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing actions in database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write("Migrating prompt actions from hardcoded file to database...")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
        
        migrated_count = 0
        skipped_count = 0
        created_count = 0
        
        for prompt_id, actions in PROMPT_ACTIONS.items():
            # Parse prompt ID (e.g., "9a" -> number=9, entry="a")
            if not prompt_id:
                continue
                
            try:
                # Extract number and entry from prompt_id
                number_str = ""
                entry = ""
                for i, char in enumerate(prompt_id):
                    if char.isdigit():
                        number_str += char
                    else:
                        entry = prompt_id[i:]
                        break
                
                if not number_str or not entry:
                    self.stdout.write(
                        self.style.ERROR(f"Could not parse prompt ID: {prompt_id}")
                    )
                    continue
                
                number = int(number_str)
                
                # Get or create the prompt
                prompt, created = Prompt.objects.get_or_create(
                    number=number,
                    entry=entry,
                    defaults={'text': f'Placeholder text for prompt {prompt_id}'}
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f"Created new prompt: {prompt}")
                
                # Check if actions already exist
                if prompt.actions and not force:
                    self.stdout.write(f"Skipping {prompt_id} - actions already exist (use --force to overwrite)")
                    skipped_count += 1
                    continue
                
                # Migrate the actions
                if not dry_run:
                    prompt.actions = actions
                    prompt.save()
                    migrated_count += 1
                
                self.stdout.write(f"{'Would migrate' if dry_run else 'Migrated'} {prompt_id}: {len(actions)} actions")
                
                # Show the actions being migrated
                for i, action in enumerate(actions, 1):
                    action_type = action.get('type', 'unknown')
                    description = action.get('description', '')
                    self.stdout.write(f"  {i}. {action_type}: {description}")
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error processing {prompt_id}: {e}")
                )
        
        # Summary
        self.stdout.write("\n" + "="*50)
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f"DRY RUN COMPLETE"))
            self.stdout.write(f"Would create: {created_count} new prompts")
            self.stdout.write(f"Would migrate: {migrated_count} prompt actions")
            self.stdout.write(f"Would skip: {skipped_count} prompts (actions already exist)")
        else:
            self.stdout.write(self.style.SUCCESS(f"MIGRATION COMPLETE"))
            self.stdout.write(f"Created: {created_count} new prompts")
            self.stdout.write(f"Migrated: {migrated_count} prompt actions")
            self.stdout.write(f"Skipped: {skipped_count} prompts (actions already exist)")
        
        self.stdout.write(f"Total prompts processed: {len(PROMPT_ACTIONS)}")
