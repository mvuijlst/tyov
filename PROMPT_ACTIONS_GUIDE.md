# Prompt Actions Management Guide

## Overview

The prompt actions system has been successfully migrated from hardcoded Python files to the database. This allows you to easily edit prompt actions through the Django admin interface or management commands.

## Current Status

- **Total prompts**: 278
- **Prompts with actions**: 14 (5.0% complete)
- **Prompts needing actions**: 264

## Available Action Types

Here are the common action types you can use:

### Character Actions
- `kill_mortal` - Kill a mortal character
- `create_mortal` - Create a new mortal character
- `create_immortal` - Create a new immortal character
- `convert_mortal_to_immortal` - Convert a mortal to immortal
- `age_mortals` - All mortal characters die of old age

### Skill Actions
- `add_skill` - Gain a specific skill (with predetermined name)
- `create_skill` - Create a new skill (user-defined name)
- `check_skill` - Check a skill
- `check_skills` - Check multiple skills
- `lose_skill` - Lose a skill
- `create_skill_from_memory` - Create a skill based on a memory

### Resource Actions
- `create_resource` - Create a new resource
- `create_stationary_resource` - Create a new stationary resource
- `lose_resource` - Lose a resource
- `lose_resources` - Lose multiple resources
- `lose_stationary_resources` - Lose all stationary resources

### Memory Actions
- `lose_memory` - Lose a memory
- `create_experience` - Create a new experience

### Mark Actions
- `create_mark` - Create a new mark
- `remove_mark` - Remove a mark

### Special Actions
- `time_passes` - Significant time passes
- `choice` - Present multiple options to the player

## How to Add Actions

### Method 1: Using Management Commands

Add a single action to a prompt:
```bash
python manage.py add_prompt_action 4b --action-type "create_skill" --description "Gain a skill related to the cult"
```

Use `--dry-run` to preview changes:
```bash
python manage.py add_prompt_action 4b --action-type "create_skill" --description "Gain a skill related to the cult" --dry-run
```

Append to existing actions:
```bash
python manage.py add_prompt_action 4b --action-type "create_resource" --description "Gain a cult resource" --append
```

### Method 2: Using Django Admin

1. Start the development server: `python manage.py runserver`
2. Go to: http://127.0.0.1:8000/admin/
3. Navigate to: Game > Prompts
4. Find the prompt you want to edit
5. Click on it to open the edit form
6. Edit the "Actions" JSON field directly

### Method 3: Analyze and Plan

Use the analyze command to see which prompts need actions:
```bash
# Show summary
python manage.py analyze_prompts

# Show only prompts without actions
python manage.py analyze_prompts --show-missing-only --limit 10

# Show prompts with their actions
python manage.py analyze_prompts --show-actions --limit 5
```

## Action JSON Structure

Each action is a JSON object with these common fields:

```json
{
  "type": "action_type",
  "description": "Human-readable description",
  "conditional": "create_if_none_exist",  // Optional
  "user_input_required": true,           // Optional
  "count": 2                            // For check_skills, lose_resources, etc.
}
```

### Examples

**Kill a mortal (with fallback creation):**
```json
{
  "type": "kill_mortal",
  "description": "Kill a mortal character",
  "conditional": "create_if_none_exist"
}
```

**Add a specific skill:**
```json
{
  "type": "add_skill",
  "skill_name": "Bloodthirsty",
  "description": "Gain the skill: Bloodthirsty"
}
```

**Create user-defined skill:**
```json
{
  "type": "create_skill",
  "description": "Create a skill that reflects your feeding system",
  "hint": "Describe your feeding system and what happens to those who die"
}
```

**Check multiple skills:**
```json
{
  "type": "check_skills",
  "count": 2,
  "description": "Check two skills"
}
```

**Complex choice action:**
```json
{
  "type": "choice",
  "description": "Choose your response",
  "options": [
    {
      "choice": "option_a",
      "actions": [
        {
          "type": "add_skill",
          "skill_name": "Determined",
          "description": "Gain the skill: Determined"
        }
      ]
    },
    {
      "choice": "option_b", 
      "actions": [
        {
          "type": "lose_resource",
          "description": "Lose a resource"
        }
      ]
    }
  ]
}
```

## Next Steps

1. **Use the admin interface** to browse and edit existing prompts
2. **Use the analyze command** to identify which prompts need actions
3. **Use the add_prompt_action command** for quick single-action additions
4. **Manually edit JSON** in the admin for complex multi-action prompts

The system will automatically fall back to pattern matching for prompts without actions, so you can gradually add actions to prompts as needed.

## Common Prompt Patterns

Based on the existing prompts, here are common patterns you'll encounter:

- **Prompts that kill characters**: Use `kill_mortal` or `age_mortals`
- **Prompts that create things**: Use `create_skill`, `create_resource`, `create_mark`
- **Prompts about losing things**: Use `lose_stationary_resources`, `lose_skill`, `lose_memory`
- **Prompts about checking abilities**: Use `check_skill` or `check_skills`
- **Prompts with multiple options**: Use the `choice` action type

Start with the most mechanically important prompts (those that clearly state game effects) and work your way through the list.
