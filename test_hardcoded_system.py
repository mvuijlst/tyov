#!/usr/bin/env python
"""
Test script to verify the new hardcoded prompt system works for 9a.
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

def test_hardcoded_9a():
    """Test that Prompt 9a uses hardcoded actions instead of pattern matching."""
    
    # Create a test user and character
    user, created = User.objects.get_or_create(username='test_hardcoded', defaults={'email': 'test@example.com'})
    character, created = VampireCharacter.objects.get_or_create(
        user=user,
        name='Test Vampire Hardcoded',
        defaults={
            'origin_description': 'A vampire for testing hardcoded prompt system.',
            'current_prompt': 9
        }
    )
    
    # Test Prompt 9a with hardcoded system
    prompt_text = "You develop a system for feeding. What is it? What happens to those who die? Create a Skill that reflects this."
    prompt_id = "9a"
    
    # Initialize the processor with prompt ID
    processor = PromptProcessor(character, prompt_text, prompt_id=prompt_id)
    
    # Analyze the prompt
    required_actions = processor.analyze_prompt()
    
    print(f"Testing hardcoded system for Prompt {prompt_id}")
    print(f"Prompt text: {prompt_text}")
    print(f"Required actions found: {len(required_actions)}")
    
    for i, action in enumerate(required_actions):
        print(f"  Action {i+1}: {action['type']} - {action['description']}")
        if 'requires_input' in action:
            print(f"    Requires input: {action['requires_input']}")
        if 'hint' in action:
            print(f"    Hint: {action['hint']}")
    
    # Check that a create_skill action was found from hardcoded config
    create_skill_actions = [a for a in required_actions if a['type'] == 'create_skill']
    
    if create_skill_actions:
        print("\n✅ SUCCESS: Hardcoded system working for Prompt 9a")
        action = create_skill_actions[0]
        print(f"  Description: {action['description']}")
        print(f"  Requires input: {action.get('requires_input', False)}")
        print(f"  Hint: {action.get('hint', 'No hint provided')}")
        
        # Test execution
        print("\n🧪 Testing skill creation execution:")
        test_input = {
            'name': 'Efficient Feeding System',
            'description': 'I lure victims to secluded locations and dispose of remains efficiently.'
        }
        
        try:
            result = processor.execute_action('create_skill', input_data=test_input)
            print(f"  Execution result: {result}")
            
            # Check if skill was created
            skill = Skill.objects.filter(character=character, name='Efficient Feeding System').first()
            if skill:
                print(f"  ✅ Skill created successfully: {skill.name}")
                print(f"  Description: {skill.description}")
            else:
                print("  ❌ Skill was not created in database")
                
        except Exception as e:
            print(f"  ❌ Execution failed: {e}")
        
    else:
        print("\n❌ FAILURE: Hardcoded system not working for Prompt 9a")
        print("Available actions:")
        for action in required_actions:
            print(f"  - {action['type']}: {action['description']}")
    
    # Test fallback for unknown prompt
    print(f"\n🔄 Testing fallback system for unknown prompt:")
    unknown_processor = PromptProcessor(character, prompt_text, prompt_id="999z")
    fallback_actions = unknown_processor.analyze_prompt()
    
    print(f"Fallback actions found: {len(fallback_actions)}")
    for i, action in enumerate(fallback_actions):
        print(f"  Fallback Action {i+1}: {action['type']} - {action['description']}")
    
    if fallback_actions:
        print("✅ Fallback system working correctly")
    else:
        print("❌ Fallback system not working")

if __name__ == '__main__':
    test_hardcoded_9a()
