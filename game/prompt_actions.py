"""
Prompt Actions Configuration for Thousand Year Old Vampire
This file contains the explicit mechanical actions required for each prompt.
"""

# Action type definitions
ACTION_TYPES = {
    # Character actions
    'kill_mortal': 'Kill a mortal character',
    'create_mortal': 'Create a new mortal character', 
    'create_immortal': 'Create a new immortal character',
    'convert_mortal_to_immortal': 'Convert a mortal to immortal',
    'age_mortals': 'All mortal characters die of old age',
    
    # Skill actions
    'add_skill': 'Gain a specific skill',
    'create_skill': 'Create a new skill (user-defined)',
    'check_skill': 'Check a skill',
    'check_skills': 'Check multiple skills',
    'lose_skill': 'Lose a skill',
    'uncheck_skill': 'Uncheck a skill',
    'create_skill_from_memory': 'Create a skill based on a memory',
    
    # Resource actions
    'create_resource': 'Create a new resource',
    'create_stationary_resource': 'Create a new stationary resource',
    'lose_resource': 'Lose a resource',
    'lose_resources': 'Lose multiple resources',
    'lose_stationary_resources': 'Lose all stationary resources',
    'convert_resource': 'Convert one resource to another',
    
    # Mark actions
    'create_mark': 'Create a new mark',
    'remove_mark': 'Remove a mark',
    
    # Memory actions
    'lose_memory': 'Lose a memory',
    'lose_memory_slot': 'Permanently lose a memory slot',
    'create_experience': 'Create a new experience (automatic)',
    'modify_memory': 'Modify an existing memory',
    'create_diary': 'Create a diary',
    'move_memory_to_diary': 'Move a memory to diary',
    
    # Special actions
    'roll_dice': 'Roll dice for next prompt',
    'change_name': 'Adopt a new name',
    'flee_region': 'Flee to a new region',
    'time_passes': 'Significant time passes',
}

# Prompt actions database
# Each prompt is keyed by its ID (e.g., "1a", "1b", etc.)
# Each entry contains a list of required actions
PROMPT_ACTIONS = {
    "1a": [
        {
            'type': 'kill_mortal',
            'description': 'Kill a mortal character',
            'conditional': 'create_if_none_exist',  # Create a mortal if none exist
        },
        {
            'type': 'add_skill',
            'skill_name': 'Bloodthirsty',
            'description': 'Gain the skill: Bloodthirsty',
        }
    ],
    
    "1b": [
        {
            'type': 'convert_mortal_to_immortal',
            'description': 'Convert a beloved mortal into an enemy immortal',
            'relationship_change': 'enemy',
        },
        {
            'type': 'add_skill',
            'skill_name': 'Ashamed',
            'description': 'Gain the skill: Ashamed',
        }
    ],
    
    "1c": [
        {
            'type': 'create_immortal',
            'description': 'Create a wicked and powerful supernatural entity',
            'relationship': 'master',
        },
        {
            'type': 'check_skill',
            'description': 'Check a skill (how you escape)',
        },
        {
            'type': 'add_skill',
            'skill_name': 'Humans are Cattle',
            'description': 'Gain the skill: Humans are Cattle',
        },
        {
            'type': 'age_mortals',
            'description': 'All mortal characters die (100 years pass)',
        },
        {
            'type': 'create_resource',
            'description': 'Gain a resource used for evil while in service',
        }
    ],
    
    "2a": [
        {
            'type': 'create_stationary_resource',
            'description': 'Create a stationary resource that shelters you',
        }
    ],
    
    "2b": [
        {
            'type': 'create_skill_from_memory',
            'description': 'Create a skill based on a memory',
        }
    ],
    
    "2c": [
        {
            'type': 'lose_stationary_resources',
            'description': 'Your hiding place is destroyed',
            'note': 'Degrade a resource into ruins',
        },
        {
            'type': 'add_skill',
            'skill_name': 'Vile Acts',
            'description': 'Gain the skill: Vile Acts',
        }
    ],
    
    "3a": [
        {
            'type': 'create_resource',
            'description': 'Create a resource representing their assistance',
        },
        {
            'type': 'create_mortal',
            'description': 'Create a mortal character',
            'conditional': 'create_if_none_exist',
        }
    ],
    
    "3b": [
        {
            'type': 'add_skill',
            'skill_name': 'Humans are Tools',
            'description': 'Gain the skill: Humans are Tools',
        }
    ],
    
    "3c": [
        {
            'type': 'convert_character_to_resource',
            'description': 'Convert the character to a resource',
        },
        {
            'type': 'check_skill',
            'description': 'Check a skill',
        }
    ],
    
    # ... Continue with more prompts
    
    "9a": [
        {
            'type': 'create_skill',
            'description': 'Create a skill that reflects your feeding system',
            'hint': 'Describe your feeding system and what happens to those who die',
        }
    ],
    
    "9b": [
        {
            'type': 'check_skill',
            'description': 'Check a skill',
        },
        {
            'type': 'create_resource',
            'description': 'Create a resource (financial profit system)',
        }
    ],
    
    "9c": [
        {
            'type': 'choice',
            'description': 'Choose your response to being usurped',
            'options': [
                {
                    'choice': 'crawl_back',
                    'actions': [
                        {
                            'type': 'add_skill',
                            'skill_name': 'Belly on the Ground',
                            'description': 'Gain the skill: Belly on the Ground',
                        }
                    ]
                },
                {
                    'choice': 'build_new_system',
                    'actions': [
                        {
                            'type': 'check_skills',
                            'count': 2,
                            'description': 'Check two skills',
                        },
                        {
                            'type': 'create_resource',
                            'description': 'Gain one resource',
                        }
                    ]
                }
            ]
        }
    ],
    
    # Example of more complex prompts...
    "10a": [
        {
            'type': 'time_passes',
            'description': 'A century passes unconsciously',
        },
        {
            'type': 'lose_memory',
            'description': 'Strike out a memory',
        },
        {
            'type': 'age_mortals',
            'description': 'Strike out all mortal characters',
        }
    ],
    
    # Add more prompts here...
}

# Helper functions for conditional logic
def should_create_mortal_if_none_exist(character):
    """Check if we should create a mortal character when none exist."""
    return not character.characters.filter(character_type='mortal', is_dead=False).exists()

def get_available_mortals(character):
    """Get available mortal characters for actions."""
    return character.characters.filter(character_type='mortal', is_dead=False)

def get_available_skills(character, checked_only=False, unchecked_only=False):
    """Get available skills for actions."""
    skills = character.skills.filter(is_lost=False)
    if checked_only:
        skills = skills.filter(is_checked=True)
    elif unchecked_only:
        skills = skills.filter(is_checked=False)
    return skills

def get_available_resources(character, stationary_only=False):
    """Get available resources for actions."""
    resources = character.resources.filter(is_lost=False)
    if stationary_only:
        resources = resources.filter(is_stationary=True)
    return resources
