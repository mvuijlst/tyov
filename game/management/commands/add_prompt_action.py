"""
Management command to add actions to specific prompts.
"""

import json
from django.core.management.base import BaseCommand
from game.models import Prompt


class Command(BaseCommand):
    help = 'Add actions to a specific prompt'

    def add_arguments(self, parser):
        parser.add_argument(
            'prompt_id',
            type=str,
            help='Prompt ID (e.g., "4a", "5b")',
        )
        parser.add_argument(
            '--action-type',
            type=str,
            required=True,
            help='Action type (e.g., "lose_stationary_resources", "create_skill")',
        )
        parser.add_argument(
            '--description',
            type=str,
            required=True,
            help='Description of the action',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be added without making changes',
        )
        parser.add_argument(
            '--append',
            action='store_true',
            help='Append to existing actions instead of replacing',
        )

    def handle(self, *args, **options):
        prompt_id = options['prompt_id']
        action_type = options['action_type']
        description = options['description']
        dry_run = options['dry_run']
        append = options['append']
        
        # Parse prompt ID
        try:
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
                    self.style.ERROR(f"Invalid prompt ID format: {prompt_id}")
                )
                return
                
            number = int(number_str)
            
        except ValueError:
            self.stdout.write(
                self.style.ERROR(f"Invalid prompt ID: {prompt_id}")
            )
            return
        
        # Get the prompt
        try:
            prompt = Prompt.objects.get(number=number, entry=entry)
        except Prompt.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Prompt {prompt_id} not found in database")
            )
            return
        
        # Create new action
        new_action = {
            'type': action_type,
            'description': description
        }
        
        # Add any additional common parameters based on action type
        if action_type == 'kill_mortal':
            new_action['conditional'] = 'create_if_none_exist'
        elif action_type in ['create_skill', 'create_resource', 'create_mark']:
            new_action['user_input_required'] = True
        elif action_type == 'check_skills':
            new_action['count'] = 1  # Default to 1, can be modified in admin
        
        # Handle existing actions
        if append and prompt.actions:
            updated_actions = prompt.actions + [new_action]
        else:
            updated_actions = [new_action]
        
        # Show what will be done
        self.stdout.write(f"Prompt {prompt_id}:")
        self.stdout.write(f"  Text: {prompt.text[:80]}...")
        self.stdout.write(f"  Current actions: {len(prompt.actions) if prompt.actions else 0}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
        
        self.stdout.write(f"  {'Appending' if append else 'Setting'} action:")
        self.stdout.write(f"    Type: {action_type}")
        self.stdout.write(f"    Description: {description}")
        
        if not dry_run:
            prompt.actions = updated_actions
            prompt.save()
            self.stdout.write(
                self.style.SUCCESS(f"✓ Updated prompt {prompt_id} with {len(updated_actions)} actions")
            )
        else:
            self.stdout.write(f"  Would result in {len(updated_actions)} total actions")
        
        # Show the final JSON structure
        self.stdout.write("\nFinal actions JSON:")
        self.stdout.write(json.dumps(updated_actions, indent=2))
