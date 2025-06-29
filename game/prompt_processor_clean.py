"""
Prompt mechanics processor for Thousand Year Old Vampire
This module detects required prompt actions and provides an interface for player choices.
"""

import re
from .models import VampireCharacter, Memory, Experience, Skill, Resource, Character, Mark, Diary


class PromptProcessor:
    """Processes prompt text and identifies required mechanical actions."""
    
    def __init__(self, character, prompt_text):
        self.character = character
        self.prompt_text = prompt_text.lower()
        self.required_actions = []
    
    def analyze_prompt(self):
        """Analyze the prompt and return required actions for player choice."""
        self.required_actions = []
        
        # Analyze each type of action
        self._analyze_character_actions()
        self._analyze_skill_actions()
        self._analyze_resource_actions()
        self._analyze_mark_actions()
        self._analyze_memory_actions()
        
        return self.required_actions
    
    def _analyze_character_actions(self):
        """Detect character-related actions needed."""
        # Kill mortal character
        if any(phrase in self.prompt_text for phrase in [
            'kill a mortal character',
            'kill a character',
            'murder someone',
            'destroy someone close to you'
        ]):
            mortal_chars = self.character.characters.filter(character_type='mortal', is_dead=False)
            self.required_actions.append({
                'type': 'kill_mortal',
                'description': 'Kill a mortal character',
                'choices': [{'id': c.id, 'name': c.name, 'description': c.description} for c in mortal_chars] if mortal_chars.exists() else [],
                'allow_create': 'create a mortal if none are available' in self.prompt_text or not mortal_chars.exists()
            })
        
        # Create mortal character
        if any(phrase in self.prompt_text for phrase in [
            'create a mortal',
            'create a new mortal character',
            'create a mortal character'
        ]):
            self.required_actions.append({
                'type': 'create_mortal',
                'description': 'Create a new mortal character',
                'requires_input': True
            })
        
        # Create immortal character
        if any(phrase in self.prompt_text for phrase in [
            'create an immortal',
            'create a new immortal character',
            'create an immortal character'
        ]):
            self.required_actions.append({
                'type': 'create_immortal',
                'description': 'Create a new immortal character',
                'requires_input': True
            })
        
        # Convert mortal to immortal
        if any(phrase in self.prompt_text for phrase in [
            'convert a mortal character into an immortal',
            'turning them into a monster like yourself'
        ]):
            mortal_chars = self.character.characters.filter(character_type='mortal', is_dead=False)
            self.required_actions.append({
                'type': 'convert_mortal',
                'description': 'Convert a mortal character into an immortal',
                'choices': [{'id': c.id, 'name': c.name, 'description': c.description} for c in mortal_chars]
            })
    
    def _analyze_skill_actions(self):
        """Detect skill-related actions needed."""
        # Add specific skills mentioned in prompts
        skill_patterns = [
            r'take the skill ([^.]+?)(?:\.|$)',
            r'gain the skill ([^.]+?)(?:\.|$)',
            r'create a skill ([^.]+?)(?:\.|$)',
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, self.prompt_text, re.IGNORECASE)
            for match in matches:
                skill_name = match.strip().title()
                skill_name = skill_name.replace(' And', ' and')
                self.required_actions.append({
                    'type': 'add_skill',
                    'description': f'Gain the skill: {skill_name}',
                    'skill_name': skill_name,
                    'auto_execute': True
                })
        
        # Check skills
        skill_check_patterns = [
            r'check (\d+) skills',
            r'check (\d+) skill',
        ]
        
        for pattern in skill_check_patterns:
            matches = re.findall(pattern, self.prompt_text, re.IGNORECASE)
            for match in matches:
                count = int(match)
                unchecked_skills = self.character.skills.filter(is_checked=False, is_lost=False)
                self.required_actions.append({
                    'type': 'check_skills',
                    'description': f'Check {count} skill(s)',
                    'count': count,
                    'choices': [{'id': s.id, 'name': s.name, 'description': s.description} for s in unchecked_skills[:count*2]]  # Show more options than needed
                })
        
        # Lose a skill
        if any(phrase in self.prompt_text for phrase in [
            'lose a skill',
            'lose one of your skills'
        ]):
            available_skills = self.character.skills.filter(is_lost=False)
            self.required_actions.append({
                'type': 'lose_skill',
                'description': 'Lose a skill',
                'choices': [{'id': s.id, 'name': s.name, 'description': s.description} for s in available_skills]
            })
    
    def _analyze_resource_actions(self):
        """Detect resource-related actions needed."""
        # Add stationary resources
        if any(phrase in self.prompt_text for phrase in [
            'gain a stationary resource',
            'create a stationary resource'
        ]):
            self.required_actions.append({
                'type': 'create_resource',
                'description': 'Gain a new stationary resource',
                'requires_input': True,
                'is_stationary': True
            })
        
        # Add regular resources
        if any(phrase in self.prompt_text for phrase in [
            'gain a resource',
            'create a resource'
        ]):
            self.required_actions.append({
                'type': 'create_resource',
                'description': 'Gain a new resource',
                'requires_input': True,
                'is_stationary': False
            })
        
        # Lose resources
        resource_loss_patterns = [
            r'lose (\d+) resources',
            r'lose (\d+) resource',
        ]
        
        for pattern in resource_loss_patterns:
            matches = re.findall(pattern, self.prompt_text, re.IGNORECASE)
            for match in matches:
                count = int(match)
                self._add_lose_resource_action(count)
        
        # Lose all stationary resources
        if 'lose all stationary resources' in self.prompt_text:
            stationary_resources = self.character.resources.filter(is_stationary=True, is_lost=False)
            self.required_actions.append({
                'type': 'lose_stationary_resources',
                'description': 'Lose all stationary resources',
                'choices': [{'id': r.id, 'name': r.name, 'description': r.description} for r in stationary_resources],
                'auto_execute': True
            })
    
    def _add_lose_resource_action(self, count):
        """Add action to lose a specific number of resources."""
        available_resources = self.character.resources.filter(is_lost=False, is_stationary=False)
        self.required_actions.append({
            'type': 'lose_resources',
            'description': f'Lose {count} resource(s)',
            'count': count,
            'choices': [{'id': r.id, 'name': r.name, 'description': r.description} for r in available_resources]
        })
    
    def _analyze_mark_actions(self):
        """Detect mark-related actions needed."""
        if any(phrase in self.prompt_text for phrase in [
            'gain a mark',
            'create a mark',
            'take a mark'
        ]):
            self.required_actions.append({
                'type': 'create_mark',
                'description': 'Gain a new mark',
                'requires_input': True
            })
        
        if any(phrase in self.prompt_text for phrase in [
            'remove a mark',
            'you may remove a mark'
        ]):
            existing_marks = self.character.marks.filter(is_removed=False)
            self.required_actions.append({
                'type': 'remove_mark',
                'description': 'Remove a mark',
                'choices': [{'id': m.id, 'description': m.description} for m in existing_marks],
                'optional': 'you may' in self.prompt_text
            })
    
    def _analyze_memory_actions(self):
        """Detect memory-related actions needed."""
        if 'strikeout all mortal characters' in self.prompt_text:
            mortal_chars = self.character.characters.filter(character_type='mortal', is_dead=False)
            self.required_actions.append({
                'type': 'age_mortals',
                'description': 'All mortal characters die of old age',
                'choices': [{'id': c.id, 'name': c.name} for c in mortal_chars],
                'auto_execute': True
            })
        elif any(phrase in self.prompt_text for phrase in [
            'strikeout a memory',
            'lose a memory'
        ]):
            available_memories = self.character.memories.filter(is_lost=False)
            self.required_actions.append({
                'type': 'lose_memory',
                'description': 'Lose a memory',
                'choices': [{'id': m.id, 'title': m.title or f'Memory {m.order}', 'experiences': [e.text[:100] for e in m.experiences.all()]} for m in available_memories]
            })

    def execute_action(self, action_type, choices=None, input_data=None):
        """Execute a specific action based on player choices."""
        actions_taken = []
        
        if action_type == 'kill_mortal':
            if choices and choices.get('character_id'):
                char = Character.objects.get(id=choices['character_id'], vampire=self.character)
                char.is_dead = True
                char.save()
                actions_taken.append(f"Killed mortal character: {char.name}")
            elif choices and choices.get('create_new'):
                # Create a new character to kill
                new_char = Character.objects.create(
                    vampire=self.character,
                    name=choices.get('name', 'Close Friend'),
                    description=choices.get('description', 'Someone you cared about, now lost to your hunger.'),
                    character_type='mortal',
                    relationship='friend',
                    is_dead=True
                )
                actions_taken.append(f"Created and killed mortal character: {new_char.name}")
        
        elif action_type == 'create_mortal':
            char = Character.objects.create(
                vampire=self.character,
                name=input_data.get('name', 'New Mortal'),
                description=input_data.get('description', 'A mortal who has entered your story.'),
                character_type='mortal',
                relationship=input_data.get('relationship', 'neutral')
            )
            actions_taken.append(f"Created mortal character: {char.name}")
        
        elif action_type == 'create_immortal':
            char = Character.objects.create(
                vampire=self.character,
                name=input_data.get('name', 'Ancient Being'),
                description=input_data.get('description', 'An immortal creature whose path has crossed yours.'),
                character_type='immortal',
                relationship=input_data.get('relationship', 'neutral')
            )
            actions_taken.append(f"Created immortal character: {char.name}")
        
        elif action_type == 'convert_mortal':
            if choices and choices.get('character_id'):
                char = Character.objects.get(id=choices['character_id'], vampire=self.character)
                char.character_type = 'immortal'
                char.relationship = 'enemy'  # Usually becomes an enemy
                char.description += " - Turned into a monster like yourself."
                char.save()
                actions_taken.append(f"Converted {char.name} from mortal to immortal")
        
        elif action_type == 'add_skill':
            skill_name = input_data.get('skill_name') if input_data else choices.get('skill_name')
            if skill_name:
                skill, created = Skill.objects.get_or_create(
                    character=self.character,
                    name=skill_name,
                    defaults={'description': input_data.get('description', 'Gained from prompt actions.')}
                )
                if created:
                    actions_taken.append(f"Gained skill: {skill_name}")
        
        elif action_type == 'check_skills':
            skill_ids = choices.get('skill_ids', [])
            for skill_id in skill_ids:
                skill = Skill.objects.get(id=skill_id, character=self.character)
                if not skill.is_checked:
                    skill.is_checked = True
                    skill.save()
                    actions_taken.append(f"Checked skill: {skill.name}")
        
        elif action_type == 'lose_skill':
            if choices and choices.get('skill_id'):
                skill = Skill.objects.get(id=choices['skill_id'], character=self.character)
                skill.is_lost = True
                skill.save()
                actions_taken.append(f"Lost skill: {skill.name}")
        
        elif action_type == 'create_resource':
            resource = Resource.objects.create(
                character=self.character,
                name=input_data.get('name', 'New Resource'),
                description=input_data.get('description', 'Gained from prompt actions.'),
                is_stationary=input_data.get('is_stationary', False)
            )
            resource_type = "stationary resource" if resource.is_stationary else "resource"
            actions_taken.append(f"Gained {resource_type}: {resource.name}")
        
        elif action_type == 'lose_resources':
            resource_ids = choices.get('resource_ids', [])
            for resource_id in resource_ids:
                resource = Resource.objects.get(id=resource_id, character=self.character)
                resource.is_lost = True
                resource.save()
                actions_taken.append(f"Lost resource: {resource.name}")
        
        elif action_type == 'lose_stationary_resources':
            stationary_resources = self.character.resources.filter(is_stationary=True, is_lost=False)
            for resource in stationary_resources:
                resource.is_lost = True
                resource.save()
                actions_taken.append(f"Lost stationary resource: {resource.name}")
        
        elif action_type == 'create_mark':
            mark = Mark.objects.create(
                character=self.character,
                description=input_data.get('description', 'A new mark has appeared on your vampiric form.'),
                how_concealed=input_data.get('how_concealed', 'You must find a way to hide this mark from mortals.')
            )
            actions_taken.append("Gained a new Mark")
        
        elif action_type == 'remove_mark':
            if choices and choices.get('mark_id'):
                mark = Mark.objects.get(id=choices['mark_id'], character=self.character)
                mark.is_removed = True
                mark.save()
                actions_taken.append(f"Removed mark: {mark.description[:50]}")
        
        elif action_type == 'lose_memory':
            if choices and choices.get('memory_id'):
                memory = Memory.objects.get(id=choices['memory_id'], character=self.character)
                memory.is_lost = True
                memory.save()
                actions_taken.append(f"Lost memory: {memory.title or 'Untitled memory'}")
        
        elif action_type == 'age_mortals':
            mortal_chars = self.character.characters.filter(character_type='mortal', is_dead=False)
            for char in mortal_chars:
                char.is_dead = True
                char.save()
                actions_taken.append(f"Mortal character {char.name} died of old age")
        
        return actions_taken
