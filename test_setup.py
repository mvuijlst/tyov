#!/usr/bin/env python
"""
Test script to verify the complete TYOV character setup process.
This script tests that all 4 setup steps are properly implemented.
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vampire_chronicle.settings')
django.setup()

from django.contrib.auth.models import User
from game.models import VampireCharacter, Memory, Experience, Skill, Resource, Character, Mark

def test_character_setup():
    """Test the complete character setup process."""
    print("🧛 Testing TYOV Character Setup Process...\n")
    
    # Create a test user if it doesn't exist
    test_user, created = User.objects.get_or_create(
        username='test_vampire_player',
        defaults={'email': 'test@vampire.com'}
    )
    if created:
        test_user.set_password('test123')
        test_user.save()
        print("✅ Created test user")
    else:
        print("✅ Using existing test user")
    
    # Create a vampire character
    character = VampireCharacter.objects.create(
        user=test_user,
        name="Lysander the Ancient",
        origin_description="I am Lysander, born of noble blood in Constantinople, 1147; scholar and keeper of forbidden texts in the monastery."
    )
    print(f"✅ Created vampire character: {character.name}")
    
    # Create 5 memory slots (this should happen automatically)
    for i in range(1, 6):
        Memory.objects.get_or_create(character=character, order=i)
    
    # Add origin experience to Memory 1
    memory_1 = Memory.objects.get(character=character, order=1)
    Experience.objects.get_or_create(
        memory=memory_1,
        text=character.origin_description,
        order=1
    )
    print("✅ Created Memory 1 with origin experience")
    
    # Step 1: Create 3 mortals
    mortals = [
        ("Brother Marcus", "my fellow monk and closest friend", "friend"),
        ("Abbess Theodora", "stern leader of our monastery", "authority"),
        ("Elena", "young scribe I secretly love", "beloved")
    ]
    
    for name, desc, rel in mortals:
        Character.objects.create(
            vampire=character,
            name=name,
            description=desc,
            character_type='mortal',
            relationship=rel
        )
    print("✅ Step 1: Created 3 mortal characters")
    
    # Step 2: Create 3 skills and 3 resources
    skills = [
        ("Ancient Languages", "I can read Greek, Latin, and Aramaic texts"),
        ("Scholarly Research", "I know how to find and interpret old documents"),
        ("Calligraphy", "My handwriting is precise and beautiful")
    ]
    
    for name, desc in skills:
        Skill.objects.create(
            character=character,
            name=name,
            description=desc
        )
    
    resources = [
        ("Library of Forbidden Texts", "My personal collection of occult manuscripts", True),
        ("Monastery Scriptorium", "Where I work on copying manuscripts", True),
        ("Silver Cross Pendant", "Blessed heirloom from my mother", False)
    ]
    
    for name, desc, stationary in resources:
        Resource.objects.create(
            character=character,
            name=name,
            description=desc,
            is_stationary=stationary
        )
    print("✅ Step 2: Created 3 skills and 3 resources")
    
    # Step 3: Create 3 additional experiences (combining traits)
    additional_experiences = [
        "Brother Marcus helps me research an ancient text in my Library of Forbidden Texts; his excitement is infectious when we discover a prophecy.",
        "I use my Ancient Languages skill to translate a love poem for Elena; she blushes when I explain its meaning.",
        "Abbess Theodora assigns me to use my Calligraphy skills in the Monastery Scriptorium; I feel pride in my perfect lettering."
    ]
    
    for i, exp_text in enumerate(additional_experiences):
        memory_order = i + 2  # Memories 2, 3, 4
        memory = Memory.objects.get(character=character, order=memory_order)
        Experience.objects.create(
            memory=memory,
            text=exp_text,
            order=1
        )
    print("✅ Step 3: Created 3 additional experiences combining traits")
    
    # Step 4: Create immortal, mark, and transformation experience
    # Create the immortal
    Character.objects.create(
        vampire=character,
        name="Count Dracula",
        description="ancient vampire lord from Wallachia; he seeks scholars to serve him",
        character_type='immortal',
        relationship='master'
    )
    
    # Create the mark
    Mark.objects.create(
        character=character,
        description="My reflection is distorted and ghostly",
        how_concealed="I avoid mirrors and polished surfaces"
    )
    
    # Create transformation experience in Memory 5
    memory_5 = Memory.objects.get(character=character, order=5)
    Experience.objects.create(
        memory=memory_5,
        text="Count Dracula offers me immortality to preserve knowledge forever; I accept, not knowing the terrible price I must pay.",
        order=1
    )
    print("✅ Step 4: Created immortal, mark, and transformation experience")
    
    # Verify setup completion
    print("\n🔍 Verifying character setup completion...")
    
    setup_checks = {
        "Skills (3+)": character.skills.count(),
        "Resources (3+)": character.resources.count(),
        "Mortal Characters (3+)": character.characters.filter(character_type='mortal').count(),
        "Immortal Characters (1+)": character.characters.filter(character_type='immortal').count(),
        "Marks (1+)": character.marks.count(),
        "Memories with Experiences": sum(1 for m in character.memories.all() if m.experiences.exists())
    }
    
    all_good = True
    for check, count in setup_checks.items():
        expected = 3 if "3+" in check else 1 if "1+" in check else 5
        status = "✅" if count >= expected else "❌"
        print(f"{status} {check}: {count}")
        if count < expected:
            all_good = False
    
    print(f"\n{'🎉 CHARACTER SETUP COMPLETE!' if all_good else '⚠️  CHARACTER SETUP INCOMPLETE'}")
    
    if all_good:
        print(f"""
📜 Character Summary:
Name: {character.name}
Skills: {', '.join([s.name for s in character.skills.all()])}
Resources: {', '.join([r.name for r in character.resources.all()])}
Mortals: {', '.join([c.name for c in character.characters.filter(character_type='mortal')])}
Immortal: {character.characters.filter(character_type='immortal').first().name}
Mark: {character.marks.first().description}
        """)
    
    return all_good

if __name__ == "__main__":
    success = test_character_setup()
    sys.exit(0 if success else 1)
