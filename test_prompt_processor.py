#!/usr/bin/env python
"""
Test script for the prompt processor
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('m:/OneDrive/Projects/python/tyov')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vampire_chronicle.settings')
django.setup()

from game.models import VampireCharacter, Memory, Experience, Skill, Resource, Character, Mark, Prompt
from game.prompt_processor import PromptProcessor
from django.contrib.auth.models import User

def test_prompt_processor():
    """Test the prompt processor with the sample prompt."""
    
    # Create a test user and character
    user, created = User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'})
    
    # Create or get test character
    character, created = VampireCharacter.objects.get_or_create(
        user=user,
        name='Test Vampire',
        defaults={
            'origin_description': 'A test vampire for prompt processing',
            'current_prompt': 1,
            'prompt_entry': 'a'
        }
    )
    
    # Create some initial traits for testing
    if created:
        # Create memories
        for i in range(1, 6):
            Memory.objects.create(character=character, order=i)
        
        # Create some skills
        Skill.objects.create(character=character, name='Swordplay', description='Fighting with swords')
        Skill.objects.create(character=character, name='Persuasion', description='Convincing others')
        
        # Create some resources
        Resource.objects.create(character=character, name='Gold Coins', description='A purse of gold')
        Resource.objects.create(character=character, name='Castle', description='A grand castle', is_stationary=True)
        
        # Create some characters
        Character.objects.create(
            vampire=character,
            name='Old Friend',
            description='A friend from mortal days',
            character_type='mortal',
            relationship='friend'
        )
        Character.objects.create(
            vampire=character,
            name='Enemy Vampire',
            description='An ancient foe',
            character_type='immortal',
            relationship='enemy'
        )
    
    # Test the prompt processor with the example prompt
    test_prompt = "In your blood-hunger, you destroy someone close to you. Kill a mortal Character. Create a mortal if none are available. Take the skill Bloodthirsty."
    
    print("=== TESTING PROMPT PROCESSOR ===")
    print(f"Character: {character.name}")
    print(f"Prompt: {test_prompt}")
    print("\n--- BEFORE PROCESSING ---")
    print(f"Skills: {list(character.skills.filter(is_lost=False).values_list('name', flat=True))}")
    print(f"Mortal Characters: {list(character.characters.filter(character_type='mortal', is_dead=False).values_list('name', flat=True))}")
    print(f"Dead Characters: {list(character.characters.filter(is_dead=True).values_list('name', flat=True))}")
    
    # Process the prompt
    processor = PromptProcessor(character, test_prompt)
    actions_taken = processor.process_prompt()
    
    print("\n--- ACTIONS TAKEN ---")
    for action in actions_taken:
        print(f"- {action}")
    
    print("\n--- AFTER PROCESSING ---")
    print(f"Skills: {list(character.skills.filter(is_lost=False).values_list('name', flat=True))}")
    print(f"Mortal Characters: {list(character.characters.filter(character_type='mortal', is_dead=False).values_list('name', flat=True))}")
    print(f"Dead Characters: {list(character.characters.filter(is_dead=True).values_list('name', flat=True))}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == '__main__':
    test_prompt_processor()
