# Thousand Year Old Vampire - Prompt Actions Database Workflow

This document provides a comprehensive workflow for manually coding all prompt actions in the game. Each prompt needs to be analyzed and its mechanical requirements translated into the `PROMPT_ACTIONS` configuration.

## Quick Reference: Action Types

### Character Actions
- `kill_mortal` - Kill a mortal character
- `create_mortal` - Create a new mortal character  
- `create_immortal` - Create a new immortal character
- `convert_mortal_to_immortal` - Convert a mortal to immortal
- `age_mortals` - All mortal characters die of old age

### Skill Actions
- `add_skill` - Gain a specific skill (name provided)
- `create_skill` - Create a new skill (user-defined name/description)
- `check_skill` - Check a single skill
- `check_skills` - Check multiple skills (specify count)
- `lose_skill` - Lose a skill
- `uncheck_skill` - Uncheck a skill
- `create_skill_from_memory` - Create a skill based on a memory

### Resource Actions
- `create_resource` - Create a new resource
- `create_stationary_resource` - Create a new stationary resource
- `lose_resource` - Lose a single resource
- `lose_resources` - Lose multiple resources (specify count)
- `lose_stationary_resources` - Lose all stationary resources
- `convert_resource` - Convert one resource to another

### Mark Actions
- `create_mark` - Create a new mark
- `remove_mark` - Remove a mark

### Memory Actions
- `lose_memory` - Lose a memory
- `lose_memory_slot` - Permanently lose a memory slot
- `modify_memory` - Modify an existing memory
- `create_diary` - Create a diary
- `move_memory_to_diary` - Move a memory to diary

### Special Actions
- `roll_dice` - Roll dice for next prompt (automatic)
- `change_name` - Adopt a new name
- `flee_region` - Flee to a new region
- `time_passes` - Significant time passes
- `choice` - Complex choice with multiple branches

## Workflow Steps

### Step 1: Identify the Prompt
- Find the prompt in `source/Thousand Year Old Vampire_TextOnly.txt`
- Note the prompt ID (e.g., "1a", "9b", "22c")
- Read the full prompt text carefully

### Step 2: Parse Mechanical Instructions
Look for these keywords and phrases in the prompt:

**Character Management:**
- "Kill a mortal Character" → `kill_mortal`
- "Create a mortal if none are available" → `create_mortal` with `conditional: 'create_if_none_exist'`
- "Create an immortal Character" → `create_immortal`
- "Convert a mortal Character into an immortal" → `convert_mortal_to_immortal`
- "Strikeout all mortal Characters" → `age_mortals`

**Skills:**
- "Take the skill [Name]" → `add_skill` with `skill_name`
- "Gain the skill [Name]" → `add_skill` with `skill_name`
- "Create a Skill that reflects..." → `create_skill`
- "Create a Skill based on..." → `create_skill`
- "Check a Skill" → `check_skill`
- "Check [number] Skills" → `check_skills` with `count`
- "Lose a Skill" → `lose_skill`

**Resources:**
- "Create a Resource" → `create_resource`
- "Create a stationary Resource" → `create_stationary_resource`
- "Gain a Resource" → `create_resource`
- "Lose a Resource" → `lose_resource`
- "Lose [number] Resources" → `lose_resources` with `count`
- "Lose any stationary Resources" → `lose_stationary_resources`

**Marks:**
- "Gain a Mark" → `create_mark`
- "Create a Mark" → `create_mark`
- "You may remove a Mark" → `remove_mark` with `optional: true`
- "Remove a Mark" → `remove_mark`

**Memories:**
- "Strikeout a Memory" → `lose_memory`
- "Lose a Memory" → `lose_memory`

### Step 3: Handle Conditionals and Special Cases

**Conditional Creation:**
```python
{
    'type': 'create_mortal',
    'description': 'Create a mortal character',
    'conditional': 'create_if_none_exist',  # Only if no mortals exist
}
```

**Choice-Based Prompts (like 9c):**
```python
{
    'type': 'choice',
    'description': 'Choose your response',
    'options': [
        {
            'choice': 'option1_key',
            'actions': [
                {'type': 'add_skill', 'skill_name': 'Skill Name'},
                # ... more actions
            ]
        },
        {
            'choice': 'option2_key', 
            'actions': [
                {'type': 'check_skills', 'count': 2},
                # ... more actions
            ]
        }
    ]
}
```

**Multiple Requirements:**
```python
[
    {'type': 'check_skill', 'description': 'Check a skill'},
    {'type': 'create_resource', 'description': 'Create a resource'},
    {'type': 'add_skill', 'skill_name': 'Bloodthirsty'},
]
```

### Step 4: Add Helpful Metadata

Add hints and descriptions to help the UI:
```python
{
    'type': 'create_skill',
    'description': 'Create a skill that reflects your feeding system',
    'hint': 'Describe your feeding system and what happens to those who die',
}
```

### Step 5: Test Your Configuration

After adding prompts, test them:
1. Create a test character
2. Navigate to the specific prompt
3. Submit a response
4. Verify that the correct actions are presented
5. Complete the actions and ensure they execute correctly

## Example: Complete Prompt Analysis

**Prompt 9a:** "You develop a system for feeding. What is it? What happens to those who die? Create a Skill that reflects this."

**Analysis:**
- No character actions
- "Create a Skill that reflects this" → `create_skill`
- No resource actions
- No mark actions
- No memory actions

**Configuration:**
```python
"9a": [
    {
        'type': 'create_skill',
        'description': 'Create a skill that reflects your feeding system',
        'hint': 'Describe your feeding system and what happens to those who die',
    }
]
```

## Prompt Processing Priority Order

Process prompts in this order to catch dependencies:

1. **Simple Prompts First:** Start with prompts that have only 1-2 mechanical actions
2. **Character Creation/Destruction:** Prompts that manage characters
3. **Skill Management:** Prompts that add/remove/check skills
4. **Resource Management:** Prompts that handle resources
5. **Complex Choice Prompts:** Prompts with multiple branches
6. **Time/Narrative Prompts:** Prompts that advance time or change status

## Common Patterns by Prompt Series

### Prompt 1 Series (Becoming a Vampire)
- Usually involves killing mortals, gaining dark skills
- Often creates immortal characters (makers)
- May age out mortal characters

### Prompt 2 Series (Hiding/Adaptation)
- Often creates stationary resources (hiding places)
- Skills based on survival and craft
- May involve losing resources to persecution

### Prompt 9 Series (Feeding Systems)
- Create skills related to feeding
- May create resources (profit systems)
- Often involves choice between approaches

### Prompt 10+ Series (Time Passage)
- Often ages mortal characters
- May involve losing memories
- Creates powerful artifacts or supernatural conflicts

## Files to Update

1. **`game/prompt_actions.py`** - Add your prompt configurations to `PROMPT_ACTIONS`
2. **Test each prompt** - Navigate to it in the game and verify behavior
3. **Update as needed** - Refine configurations based on testing

## Getting Started

I recommend starting with these prompts as they're straightforward:

1. **1a** - Kill mortal, gain Bloodthirsty skill (already done)
2. **2a** - Create stationary resource
3. **9a** - Create skill (already done)  
4. **3a** - Create resource and mortal
5. **7a** - Create skill based on vampire maker

Then move on to more complex prompts:
- **1c** - Multiple actions, time passage
- **9c** - Choice-based prompt
- **10a** - Time passage with memory loss

## Notes for Complex Prompts

Some prompts will require special handling:
- **Prompts with "or" conditions** - May need choice actions
- **Prompts referencing other prompts** - May need to check game state
- **Prompts with narrative time jumps** - May need special time passage handling
- **Prompts with dice modifications** - May need special dice logic

Start simple and build up complexity as you get comfortable with the system!
