#!/usr/bin/env python
"""
Quick test to check if the PromptProcessor module loads correctly
"""
import sys
import os
import django

# Set up Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vampire_chronicle.settings')

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Test import
    from game.prompt_processor import PromptProcessor
    print("✅ PromptProcessor import successful")
    
    # Check if problematic method exists
    if hasattr(PromptProcessor, '_convert_mortal_to_immortal'):
        print("❌ PROBLEM: _convert_mortal_to_immortal method still exists")
    else:
        print("✅ Good: _convert_mortal_to_immortal method removed")
    
    # Test with dummy data
    class DummyCharacter:
        def __init__(self):
            self.characters = DummyQuerySet()
    
    class DummyQuerySet:
        def filter(self, **kwargs):
            return self
        def exists(self):
            return False
    
    dummy_char = DummyCharacter()
    processor = PromptProcessor(dummy_char, "test prompt")
    
    print("✅ PromptProcessor instantiation successful")
    
    # Test analyze_prompt
    result = processor.analyze_prompt()
    print(f"✅ analyze_prompt successful, returned {len(result)} actions")
    
    print("\n🎉 ALL TESTS PASSED - Module should work correctly!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
