#!/usr/bin/env python
"""
Test script for the interactive prompt processor
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

def test_interactive_prompt_processor():
    """Test the interactive prompt processor."""
    
    # Create a test user and character
    user, created = User.objects.get_or_create(username='testuser2', defaults={'email': 'test2@example.com'})
    
    # Create or get test character
    character, created = VampireCharacter.objects.get_or_create(
        user=user,
        name='Interactive Test Vampire',
        defaults={
            'origin_description': 'A test vampire for interactive prompt processing',
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
            name='Beloved Sister',
            description='Your dear sister from when you were mortal',
            character_type='mortal',
            relationship='family'
        )
    
    # Test the prompt processor with the example prompt
    test_prompt = "In your blood-hunger, you destroy someone close to you. Kill a mortal Character. Create a mortal if none are available. Take the skill Bloodthirsty."
    
    print("=== TESTING INTERACTIVE PROMPT PROCESSOR ===")
    print(f"Character: {character.name}")
    print(f"Prompt: {test_prompt}")
    print("\n--- ANALYZING PROMPT ---")
    
    # Analyze the prompt to get required actions
    processor = PromptProcessor(character, test_prompt)
    required_actions = processor.analyze_prompt()
    
    print(f"Required actions found: {len(required_actions)}")
    for i, action in enumerate(required_actions):
        print(f"{i+1}. {action['type']}: {action['description']}")
        if 'choices' in action and action['choices']:
            print(f"   Available choices: {len(action['choices'])}")
            for choice in action['choices']:
                print(f"   - {choice['name']}: {choice['description']}")
        if action.get('allow_create'):
            print(f"   Can create new: Yes")
        print()
    
    # Test execution of an action (simulating user choice)
    if required_actions:
        print("--- TESTING ACTION EXECUTION ---")
        for action in required_actions:
            if action['type'] == 'kill_mortal':
                # Simulate choosing the first available character
                if action.get('choices'):
                    print(f"Executing: Kill {action['choices'][0]['name']}")
                    result = processor.execute_action('kill_mortal', choices={'character_id': action['choices'][0]['id']})
                    print(f"Result: {result}")
                else:
                    print("Executing: Create and kill new character")
                    result = processor.execute_action('kill_mortal', choices={'create_new': True, 'name': 'Test Friend', 'description': 'A test character'})
                    print(f"Result: {result}")
            elif action['type'] == 'add_skill':
                print(f"Executing: Add skill {action.get('skill_name', 'Unknown')}")
                result = processor.execute_action('add_skill', input_data=action)
                print(f"Result: {result}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == '__main__':
    test_interactive_prompt_processor()
