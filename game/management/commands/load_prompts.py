from django.core.management.base import BaseCommand
from game.models import Prompt
import re


class Command(BaseCommand):
    help = 'Load game prompts from the Thousand Year Old Vampire text file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='source/Thousand Year Old Vampire_TextOnly.txt',
            help='Path to the game text file'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
            return
        
        # Find the start of the prompts section
        prompts_start = content.find('________________\n\n\nPrompts\n\n')
        if prompts_start == -1:
            # Try alternative format
            prompts_start = content.find('Prompts\n\n\n1a')
            if prompts_start == -1:
                self.stdout.write(
                    self.style.ERROR('Could not find prompts section in the file')
                )
                return
        
        prompts_section = content[prompts_start:]
        
        # Extract prompts using regex
        prompt_pattern = r'(\d+)([abc])\n(.+?)(?=\n\d+[abc]\n|\nAppendix|\n\n\n|\Z)'
        matches = re.findall(prompt_pattern, prompts_section, re.DOTALL)
        
        created_count = 0
        updated_count = 0
        
        for match in matches:
            number = int(match[0])
            entry = match[1]
            text = match[2].strip()
            
            # Clean up the text
            text = re.sub(r'\n+', '\n', text)  # Remove multiple newlines
            text = text.strip()
            
            if text:
                prompt, created = Prompt.objects.get_or_create(
                    number=number,
                    entry=entry,
                    defaults={'text': text}
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'Created prompt {number}{entry}')
                else:
                    if prompt.text != text:
                        prompt.text = text
                        prompt.save()
                        updated_count += 1
                        self.stdout.write(f'Updated prompt {number}{entry}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully processed prompts: {created_count} created, {updated_count} updated'
            )
        )
        
        # Also add some sample prompts if none were found
        if created_count == 0 and updated_count == 0:
            self.create_sample_prompts()
    
    def create_sample_prompts(self):
        """Create some sample prompts for testing"""
        sample_prompts = [
            (1, 'a', 'In your blood-hunger, you destroy someone close to you. Kill a mortal Character. Create a mortal if none are available. Take the skill Bloodthirsty.'),
            (1, 'b', 'You are overcome by panic and maul someone close to you, accidentally turning them into a monster like yourself. Convert a beloved mortal Character into an enemy immortal. Take the Skill Ashamed.'),
            (1, 'c', 'You are captured and enslaved by a wicked and powerful supernatural entity. Create an immortal Character. How do you eventually escape their servitude? Check a Skill and take the Skill Humans are Cattle. Strikeout all mortal Characters, as a hundred years, have passed. Take a Resource you have used for evil while in service to your former master.'),
            (2, 'a', 'Horrified at your new nature, you withdraw from society. Where do you hide? How do you feed? Create a stationary Resource which shelters you'),
            (2, 'b', 'You reinvent your existence around the seclusion of your hiding place. You begin to work in an artful way, changing your living environment. How do you come to appreciate beauty or craft in a new way? Create a Skill based on a Memory.'),
            (2, 'c', 'Your hiding place is destroyed by mortals. What steps had you taken to ensure your survival? What revenge do you wreak upon your persecutors? Degrade a Resource into ruins. Take the Skill Vile Acts.'),
        ]
        
        created_count = 0
        for number, entry, text in sample_prompts:
            prompt, created = Prompt.objects.get_or_create(
                number=number,
                entry=entry,
                defaults={'text': text}
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} sample prompts')
        )
