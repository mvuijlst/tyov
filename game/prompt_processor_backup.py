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
                    'auto_execute': True  # Specific skill names can be auto-added
                })
        
        # Check skills
        if any(phrase in self.prompt_text for phrase in [
            'check a skill',
            'check two skills',
            'check three skills',
            'check one skill'
        ]):
            count = 1
            if 'check three skills' in self.prompt_text:
                count = 3
            elif 'check two skills' in self.prompt_text:
                count = 2
            
            unchecked_skills = self.character.skills.filter(is_checked=False, is_lost=False)
            self.required_actions.append({
                'type': 'check_skills',
                'description': f'Check {count} skill(s)',
                'count': count,
                'choices': [{'id': s.id, 'name': s.name, 'description': s.description} for s in unchecked_skills]
            })
        
        # Lose skills
        if any(phrase in self.prompt_text for phrase in [
            'lose a skill',
            'strikeout a skill',
            'lose a checked skill',
            'lose an unchecked skill'
        ]):
            available_skills = self.character.skills.filter(is_lost=False)
            self.required_actions.append({
                'type': 'lose_skill',
                'description': 'Lose a skill',
                'choices': [{'id': s.id, 'name': s.name, 'description': s.description, 'is_checked': s.is_checked} for s in available_skills]
            })
    
    def _analyze_resource_actions(self):
        """Detect resource-related actions needed."""
        # Lose resources
        if 'lose three resources' in self.prompt_text:
            self._add_lose_resource_action(3)
        elif 'lose two resources' in self.prompt_text:
            self._add_lose_resource_action(2)
        elif 'lose any stationary resources' in self.prompt_text:
            stationary_resources = self.character.resources.filter(is_stationary=True, is_lost=False)
            self.required_actions.append({
                'type': 'lose_stationary_resources',
                'description': 'Lose all stationary resources',
                'choices': [{'id': r.id, 'name': r.name, 'description': r.description} for r in stationary_resources],
                'auto_execute': True
            })
        elif any(phrase in self.prompt_text for phrase in [
            'lose a resource',
            'destroy a resource'
        ]):
            self._add_lose_resource_action(1)
        
        # Create resources (usually requires player input for naming)
        if any(phrase in self.prompt_text for phrase in [
            'create a resource',
            'gain a resource',
            'take a resource'
        ]):
            self.required_actions.append({
                'type': 'create_resource',
                'description': 'Create a new resource',
                'requires_input': True,
                'is_stationary': 'stationary resource' in self.prompt_text
            })
    
    def _add_lose_resource_action(self, count):
        """Helper to add lose resource action."""
        available_resources = self.character.resources.filter(is_lost=False)
        self.required_actions.append({
            'type': 'lose_resources',
            'description': f'Lose {count} resource(s)',
            'count': count,
            'choices': [{'id': r.id, 'name': r.name, 'description': r.description, 'is_stationary': r.is_stationary} for r in available_resources]
        })
    
    def _analyze_mark_actions(self):
        """Detect mark-related actions needed."""
        if any(phrase in self.prompt_text for phrase in [
            'create a mark',
            'gain a mark',
            'receive a mark'
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
    
    def _process_skill_actions(self):
        """Handle skill creation, checking, and loss."""
        # Add specific skills mentioned in prompts
        skill_patterns = [
            r'take the skill ([^.]+?)(?:\.|$)',
            r'gain the skill ([^.]+?)(?:\.|$)',
            r'create a skill ([^.]+?)(?:\.|$)',
            r'gain a skill ([^.]+?)(?:\.|$)',
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, self.prompt_text, re.IGNORECASE)
            for match in matches:
                skill_name = match.strip().title()
                # Clean up common endings
                skill_name = skill_name.replace(' And', ' and')
                self._add_skill(skill_name)
        
        # Check skills
        if any(phrase in self.prompt_text for phrase in [
            'check a skill',
            'check two skills',
            'check three skills',
            'check one skill'
        ]):
            if 'check three skills' in self.prompt_text:
                self._check_skills(3)
            elif 'check two skills' in self.prompt_text:
                self._check_skills(2)
            else:
                self._check_skills(1)
        
        # Lose skills
        if any(phrase in self.prompt_text for phrase in [
            'lose a skill',
            'strikeout a skill',
            'lose a checked skill',
            'lose an unchecked skill'
        ]):
            self._lose_skill()
    
    def _process_resource_actions(self):
        """Handle resource creation and loss."""
        # Lose resources - check for specific counts first
        if 'lose three resources' in self.prompt_text:
            self._lose_resources(3)
        elif 'lose two resources' in self.prompt_text:
            self._lose_resources(2)
        elif 'lose any stationary resources' in self.prompt_text:
            self._lose_stationary_resources()
        elif any(phrase in self.prompt_text for phrase in [
            'lose a resource',
            'destroy a resource'
        ]):
            self._lose_resources(1)
        
        # Create specific resources mentioned in prompts
        resource_patterns = [
            r'create a resource ([^.]+?)(?:\.|$)',
            r'gain a resource ([^.]+?)(?:\.|$)',
            r'take a resource ([^.]+?)(?:\.|$)',
            r'create a ([^,]+?) resource',
            r'gain a ([^,]+?) resource',
        ]
        
        for pattern in resource_patterns:
            matches = re.findall(pattern, self.prompt_text, re.IGNORECASE)
            for match in matches:
                resource_name = match.strip().title()
                self._add_resource(resource_name)
        
        # Handle specific named resources
        if 'create a stationary resource' in self.prompt_text:
            self._add_stationary_resource("Hidden Shelter")
        
        if 'the secret cabal' in self.prompt_text and 'create a resource' in self.prompt_text:
            self._add_resource("The Secret Cabal")
    
    def _process_mark_actions(self):
        """Handle mark creation and removal."""
        if any(phrase in self.prompt_text for phrase in [
            'create a mark',
            'gain a mark',
            'receive a mark'
        ]):
            self._add_mark()
        
        if any(phrase in self.prompt_text for phrase in [
            'remove a mark',
            'you may remove a mark'
        ]):
            self._remove_mark()
    
    def _process_memory_actions(self):
        """Handle memory operations."""
        if any(phrase in self.prompt_text for phrase in [
            'strikeout a memory',
            'lose a memory',
            'strikeout all mortal characters'
        ]):
            if 'strikeout all mortal characters' in self.prompt_text:
                self._age_mortal_characters()
            else:
                self._lose_memory()
    
    # Helper methods for specific actions
    def _kill_mortal_character(self):
        """Kill a mortal character or create one if none available."""
        mortal_chars = self.character.characters.filter(character_type='mortal', is_dead=False)
        
        if mortal_chars.exists():
            # Kill the first available mortal
            char_to_kill = mortal_chars.first()
            char_to_kill.is_dead = True
            char_to_kill.save()
            self.actions_taken.append(f"Killed mortal character: {char_to_kill.name}")
        else:
            # Create a mortal character to kill
            new_char = Character.objects.create(
                vampire=self.character,
                name="A Close Friend",
                description="Someone you cared about, now lost to your hunger.",
                character_type='mortal',
                relationship='friend',
                is_dead=True
            )
            self.actions_taken.append(f"Created and killed mortal character: {new_char.name}")
    
    def _create_mortal_character(self):
        """Create a new mortal character."""
        char = Character.objects.create(
            vampire=self.character,
            name="New Mortal",
            description="A mortal who has entered your story.",
            character_type='mortal',
            relationship='neutral'
        )
        self.actions_taken.append(f"Created mortal character: {char.name}")
    
    def _create_immortal_character(self):
        """Create a new immortal character."""
        char = Character.objects.create(
            vampire=self.character,
            name="Ancient Being",
            description="An immortal creature whose path has crossed yours.",
            character_type='immortal',
            relationship='neutral'
        )
        self.actions_taken.append(f"Created immortal character: {char.name}")
    
    def _convert_mortal_to_immortal(self):
        """Convert a mortal character to immortal."""
        mortal_chars = self.character.characters.filter(character_type='mortal', is_dead=False)
        
        if mortal_chars.exists():
            char_to_convert = mortal_chars.first()
            char_to_convert.character_type = 'immortal'
            char_to_convert.relationship = 'enemy'  # Usually becomes an enemy
            char_to_convert.description += " - Turned into a monster like yourself."
            char_to_convert.save()
            self.actions_taken.append(f"Converted {char_to_convert.name} from mortal to immortal")
    
    def _add_skill(self, skill_name):
        """Add a new skill."""
        skill, created = Skill.objects.get_or_create(
            character=self.character,
            name=skill_name,
            defaults={'description': f'Gained from prompt actions.'}
        )
        if created:
            self.actions_taken.append(f"Gained skill: {skill_name}")
    
    def _check_skills(self, count):
        """Check a specified number of skills."""
        unchecked_skills = self.character.skills.filter(is_checked=False, is_lost=False)[:count]
        
        checked_count = 0
        for skill in unchecked_skills:
            skill.is_checked = True
            skill.save()
            checked_count += 1
            self.actions_taken.append(f"Checked skill: {skill.name}")
        
        if checked_count < count:
            # If not enough skills to check, lose resources instead
            remaining = count - checked_count
            self._lose_resources(remaining)
    
    def _lose_skill(self):
        """Lose (strike out) a skill."""
        available_skills = self.character.skills.filter(is_lost=False)
        
        if available_skills.exists():
            skill_to_lose = available_skills.first()
            skill_to_lose.is_lost = True
            skill_to_lose.save()
            self.actions_taken.append(f"Lost skill: {skill_to_lose.name}")
    
    def _add_resource(self, resource_name, is_stationary=False):
        """Add a new resource."""
        resource = Resource.objects.create(
            character=self.character,
            name=resource_name,
            description=f'Gained from prompt actions.',
            is_stationary=is_stationary
        )
        resource_type = "stationary resource" if is_stationary else "resource"
        self.actions_taken.append(f"Gained {resource_type}: {resource_name}")
    
    def _add_stationary_resource(self, resource_name):
        """Add a new stationary resource."""
        self._add_resource(resource_name, is_stationary=True)
    
    def _lose_resources(self, count):
        """Lose a specified number of resources."""
        available_resources = self.character.resources.filter(is_lost=False)[:count]
        
        lost_count = 0
        for resource in available_resources:
            resource.is_lost = True
            resource.save()
            lost_count += 1
            self.actions_taken.append(f"Lost resource: {resource.name}")
        
        if lost_count < count:
            # If not enough resources, check skills instead
            remaining = count - lost_count
            self._check_skills(remaining)
    
    def _lose_stationary_resources(self):
        """Lose all stationary resources."""
        stationary_resources = self.character.resources.filter(is_stationary=True, is_lost=False)
        
        for resource in stationary_resources:
            resource.is_lost = True
            resource.save()
            self.actions_taken.append(f"Lost stationary resource: {resource.name}")
    
    def _add_mark(self):
        """Add a new mark."""
        mark = Mark.objects.create(
            character=self.character,
            description="A new mark has appeared on your vampiric form.",
            how_concealed="You must find a way to hide this mark from mortals."
        )
        self.actions_taken.append("Gained a new Mark")
    
    def _remove_mark(self):
        """Remove a mark."""
        existing_marks = self.character.marks.filter(is_removed=False)
        
        if existing_marks.exists():
            mark_to_remove = existing_marks.first()
            mark_to_remove.is_removed = True
            mark_to_remove.save()
            self.actions_taken.append(f"Removed mark: {mark_to_remove.description[:50]}")
    
    def _lose_memory(self):
        """Lose (strike out) a memory."""
        available_memories = self.character.memories.filter(is_lost=False)
        
        if available_memories.exists():
            memory_to_lose = available_memories.first()
            memory_to_lose.is_lost = True
            memory_to_lose.save()
            self.actions_taken.append(f"Lost memory: {memory_to_lose.title or 'Untitled memory'}")
    
    def _age_mortal_characters(self):
        """Age/kill all mortal characters (time passage)."""
        mortal_chars = self.character.characters.filter(character_type='mortal', is_dead=False)
        
        for char in mortal_chars:
            char.is_dead = True
            char.save()
            self.actions_taken.append(f"Mortal character {char.name} died of old age")
    
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
