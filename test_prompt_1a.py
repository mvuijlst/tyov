#!/usr/bin/env python
"""
Test the fix for Prompt 1A character creation logic
"""
import os
import sys
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vampire_chronicle.settings')
django.setup()

from game.models import VampireCharacter
from game.prompt_processor import PromptProcessor

def test_prompt_1a_logic():
    try:
        # Get a character
        character = VampireCharacter.objects.first()
        if not character:
            print("No character found.")
            return
        
        # Count existing mortal characters
        mortal_count = character.characters.filter(character_type='mortal', is_dead=False).count()
        print(f"Character: {character.name}")
        print(f"Existing mortal characters: {mortal_count}")
        
        # Test Prompt 1A text
        prompt_1a = "In your blood-hunger, you destroy someone close to you. Kill a mortal Character. Create a mortal if none are available. Take the skill Bloodthirsty."
        
        print(f"\nTesting Prompt 1A: {prompt_1a}")
        
        processor = PromptProcessor(character, prompt_1a)
        required_actions = processor.analyze_prompt()
        
        print(f"\nAnalysis results:")
        for action in required_actions:
            print(f"- Action: {action['type']}")
            print(f"  Description: {action['description']}")
            print(f"  Choices available: {len(action.get('choices', []))}")
            print(f"  Allow create: {action.get('allow_create', False)}")
            
            if action['type'] == 'kill_mortal':
                if mortal_count > 0:
                    expected_allow_create = False
                    print(f"  Expected allow_create: {expected_allow_create} (mortals exist)")
                else:
                    expected_allow_create = True
                    print(f"  Expected allow_create: {expected_allow_create} (no mortals exist)")
                
                if action.get('allow_create', False) == expected_allow_create:
                    print("  ✅ CORRECT: allow_create matches expected behavior")
                else:
                    print("  ❌ WRONG: allow_create does not match expected behavior")
        
        print(f"\n✅ Test completed!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt_1a_logic()
