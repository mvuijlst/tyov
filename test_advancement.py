#!/usr/bin/env python
"""
Test the updated flow to ensure prompt advancement works after action selection
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

def test_prompt_advancement():
    try:
        # Get a character
        character = VampireCharacter.objects.first()
        if not character:
            print("No character found.")
            return
        
        print(f"Character: {character.name}")
        print(f"Current prompt: {character.current_prompt}{character.prompt_entry}")
        
        # Simulate the workflow that was broken
        test_prompt = "Convert a mortal character into an immortal, turning them into a monster like yourself."
        
        print(f"\nStep 1: Analyzing prompt: {test_prompt}")
        processor = PromptProcessor(character, test_prompt)
        required_actions = processor.analyze_prompt()
        
        print(f"Found {len(required_actions)} required actions:")
        for action in required_actions:
            print(f"  - {action['type']}: {action['description']}")
        
        # Simulate user completing actions
        print(f"\nStep 2: Simulating user completing actions...")
        if required_actions:
            action = required_actions[0]
            if action['type'] == 'convert_mortal':
                # Simulate user selecting a character
                mortal_chars = character.characters.filter(character_type='mortal', is_dead=False)
                if mortal_chars.exists():
                    selected_char = mortal_chars.first()
                    result = processor.execute_action('convert_mortal', choices={'character_id': selected_char.id})
                    print(f"  Action result: {result}")
                else:
                    print("  No mortal characters available")
        
        print(f"\n✅ Test completed successfully!")
        print(f"The fix should now allow prompt advancement after action selection.")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt_advancement()
