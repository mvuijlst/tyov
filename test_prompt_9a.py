#!/usr/bin/env python
"""
Test script to verify Prompt 9a skill creation works correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vampire_chronicle.settings')
django.setup()

from game.models import VampireCharacter, User, Skill
from game.prompt_processor import PromptProcessor

def test_prompt_9a():
    """Test that Prompt 9a correctly identifies the need to create a skill."""
    
    # Create a test user and character
    user, created = User.objects.get_or_create(username='test_9a', defaults={'email': 'test@example.com'})
    character, created = VampireCharacter.objects.get_or_create(
        user=user,
        name='Test Vampire',
        defaults={
            'origin_description': 'A vampire for testing prompt 9a.',
            'current_prompt': 9  # Just use the prompt number without the letter
        }
    )
    
    # Test Prompt 9a text
    prompt_text = "You develop a system for feeding. What is it? What happens to those who die? Create a Skill that reflects this."
    
    # Initialize the processor
    processor = PromptProcessor(character, prompt_text)
    
    # Analyze the prompt
    required_actions = processor.analyze_prompt()
    
    print(f"Prompt text: {prompt_text}")
    print(f"Required actions found: {len(required_actions)}")
    
    for i, action in enumerate(required_actions):
        print(f"  Action {i+1}: {action['type']} - {action['description']}")
        if 'requires_input' in action:
            print(f"    Requires input: {action['requires_input']}")
    
    # Check that a create_skill action was found
    create_skill_actions = [a for a in required_actions if a['type'] == 'create_skill']
    
    if create_skill_actions:
        print("\n✅ SUCCESS: Found create_skill action for Prompt 9a")
        action = create_skill_actions[0]
        print(f"  Description: {action['description']}")
        print(f"  Requires input: {action.get('requires_input', False)}")
        
        # Test execution
        print("\n🧪 Testing skill creation execution:")
        test_input = {
            'name': 'Feeding System',
            'description': 'I have developed an efficient system for feeding on mortals without detection.'
        }
        
        try:
            result = processor.execute_action('create_skill', input_data=test_input)
            print(f"  Execution result: {result}")
            
            # Check if skill was created
            skill = Skill.objects.filter(character=character, name='Feeding System').first()
            if skill:
                print(f"  ✅ Skill created successfully: {skill.name}")
                print(f"  Description: {skill.description}")
            else:
                print("  ❌ Skill was not created in database")
                
        except Exception as e:
            print(f"  ❌ Execution failed: {e}")
        
    else:
        print("\n❌ FAILURE: No create_skill action found for Prompt 9a")
        print("Available actions:")
        for action in required_actions:
            print(f"  - {action['type']}: {action['description']}")

if __name__ == '__main__':
    test_prompt_9a()
