#!/usr/bin/env python
"""
Test script to verify the PromptProcessor works without AttributeError
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

def test_prompt_processor():
    try:
        # Get a character
        character = VampireCharacter.objects.first()
        if not character:
            print("No character found. Please create a character first.")
            return
        
        # Test prompt that previously caused the error
        prompt_text = "Kill a mortal character. Convert a mortal character into an immortal, turning them into a monster like yourself."
        
        print(f"Testing prompt: {prompt_text}")
        print(f"Character: {character.name}")
        
        # Initialize processor
        processor = PromptProcessor(character, prompt_text)
        
        # Analyze prompt
        required_actions = processor.analyze_prompt()
        print(f"Required actions: {len(required_actions)}")
        
        for i, action in enumerate(required_actions):
            print(f"  {i+1}. {action['type']}: {action['description']}")
        
        # Test execution (this is where the error occurred)
        if required_actions:
            first_action = required_actions[0]
            print(f"\nTesting execution of: {first_action['type']}")
            
            # Execute with empty choices to test the method works
            result = processor.execute_action(first_action['type'], choices={}, input_data={})
            print(f"Execution result: {result}")
        
        print("\n✅ SUCCESS: No AttributeError occurred!")
        
    except AttributeError as e:
        print(f"❌ FAILED: AttributeError still occurs: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"❌ OTHER ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt_processor()
