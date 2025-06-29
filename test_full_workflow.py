#!/usr/bin/env python
"""
Test script to simulate the exact workflow that was causing the AttributeError
"""
import os
import sys
import django

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vampire_chronicle.settings')
django.setup()

from game.models import VampireCharacter
from game.prompt_processor import PromptProcessor

def test_full_workflow():
    try:
        # Get a character
        character = VampireCharacter.objects.first()
        if not character:
            print("No character found. Please create a character first.")
            return
        
        print(f"Testing with character: {character.name}")
        
        # Test the exact prompt that was causing issues
        prompt_text = "Kill a mortal character and convert a mortal character into an immortal, turning them into a monster like yourself."
        
        print(f"Prompt: {prompt_text}")
        
        # Step 1: Analyze prompt (this is called from play_game view)
        processor = PromptProcessor(character, prompt_text)
        required_actions = processor.analyze_prompt()
        
        print(f"\nAnalysis found {len(required_actions)} required actions:")
        for i, action in enumerate(required_actions):
            print(f"  {i+1}. {action['type']}: {action['description']}")
            if 'choices' in action:
                print(f"     Choices available: {len(action['choices'])}")
        
        # Step 2: Simulate user making choices and execution
        print("\nSimulating action execution...")
        
        for action in required_actions:
            if action.get('auto_execute', False):
                print(f"Auto-executing: {action['type']}")
                result = processor.execute_action(action['type'], input_data=action)
                print(f"  Result: {result}")
            else:
                print(f"Manual action (would show UI): {action['type']}")
                # Simulate executing with empty choices (what was causing the error)
                result = processor.execute_action(action['type'], choices={}, input_data={})
                print(f"  Result with no choices: {result}")
        
        print("\n✅ SUCCESS: Full workflow completed without errors!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_workflow()
