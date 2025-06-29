"""
Management command to analyze prompts and identify which ones need actions.
"""

from django.core.management.base import BaseCommand
from game.models import Prompt


class Command(BaseCommand):
    help = 'Analyze prompts to identify which ones need actions defined'

    def add_arguments(self, parser):
        parser.add_argument(
            '--show-missing-only',
            action='store_true',
            help='Only show prompts without actions',
        )
        parser.add_argument(
            '--show-actions',
            action='store_true',
            help='Show action details for prompts that have them',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Limit number of results (default: 20, use 0 for all)',
        )

    def handle(self, *args, **options):
        show_missing_only = options['show_missing_only']
        show_actions = options['show_actions']
        limit = options['limit']
        
        prompts = Prompt.objects.all().order_by('number', 'entry')
        
        if show_missing_only:
            prompts = [p for p in prompts if not p.has_actions]
            self.stdout.write(f"Found {len(prompts)} prompts without actions:")
        else:
            self.stdout.write(f"Total prompts in database: {prompts.count()}")
        
        if limit > 0:
            prompts = prompts[:limit]
            
        for prompt in prompts:
            prompt_id = f"{prompt.number}{prompt.entry}"
            action_count = len(prompt.actions) if prompt.actions else 0
            
            if show_missing_only and action_count > 0:
                continue
                
            status = "✓" if action_count > 0 else "○"
            self.stdout.write(f"{status} {prompt_id}: {action_count} actions")
            
            if show_actions and action_count > 0:
                for i, action in enumerate(prompt.actions, 1):
                    action_type = action.get('type', 'unknown')
                    description = action.get('description', '')
                    self.stdout.write(f"    {i}. {action_type}: {description}")
            
            # Show a preview of the prompt text
            text_preview = prompt.text[:80] + "..." if len(prompt.text) > 80 else prompt.text
            self.stdout.write(f"    Text: {text_preview}")
            self.stdout.write("")
        
        # Summary
        total_prompts = Prompt.objects.count()
        prompts_with_actions = Prompt.objects.filter(actions__isnull=False).exclude(actions=[]).count()
        prompts_without_actions = total_prompts - prompts_with_actions
        
        self.stdout.write("="*60)
        self.stdout.write(f"Summary:")
        self.stdout.write(f"  Total prompts: {total_prompts}")
        self.stdout.write(f"  With actions: {prompts_with_actions}")
        self.stdout.write(f"  Without actions: {prompts_without_actions}")
        self.stdout.write(f"  Completion: {(prompts_with_actions/total_prompts)*100:.1f}%")
