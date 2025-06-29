from django.db import models
from django.contrib.auth.models import User
import json


class VampireCharacter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_prompt = models.IntegerField(default=1)
    prompt_entry = models.CharField(max_length=1, default='a')  # a, b, or c
    game_ended = models.BooleanField(default=False)
    
    # Starting information
    origin_description = models.TextField(help_text="Who were they before becoming a vampire?")
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Memory(models.Model):
    character = models.ForeignKey(VampireCharacter, on_delete=models.CASCADE, related_name='memories')
    title = models.CharField(max_length=200, blank=True)
    order = models.IntegerField()  # 1-5 for the five memory slots
    is_in_diary = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['order']
        unique_together = ['character', 'order']
    
    def __str__(self):
        return f"Memory {self.order}: {self.title[:50]}"


class Experience(models.Model):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='experiences')
    text = models.TextField()
    order = models.IntegerField()  # 1-3 experiences per memory
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['memory', 'order']
    
    def __str__(self):
        return self.text[:100]


class Skill(models.Model):
    character = models.ForeignKey(VampireCharacter, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Optional description of what this skill does or how it's used")
    is_checked = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "✓" if self.is_checked else "○"
        if self.is_lost:
            status = "✗"
        return f"{status} {self.name}"


class Resource(models.Model):
    character = models.ForeignKey(VampireCharacter, on_delete=models.CASCADE, related_name='resources')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_stationary = models.BooleanField(default=False)
    is_lost = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "✗" if self.is_lost else "○"
        return f"{status} {self.name}"


class Character(models.Model):
    CHARACTER_TYPES = [
        ('mortal', 'Mortal'),
        ('immortal', 'Immortal'),
    ]
    
    RELATIONSHIP_TYPES = [
        ('friend', 'Friend'),
        ('enemy', 'Enemy'),
        ('neutral', 'Neutral'),
        ('lover', 'Lover'),
        ('family', 'Family'),
        ('servant', 'Servant'),
        ('master', 'Master'),
    ]
    
    vampire = models.ForeignKey(VampireCharacter, on_delete=models.CASCADE, related_name='characters')
    name = models.CharField(max_length=200)
    description = models.TextField()
    character_type = models.CharField(max_length=20, choices=CHARACTER_TYPES)
    relationship = models.CharField(max_length=20, choices=RELATIONSHIP_TYPES, default='neutral')
    is_dead = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "✗" if self.is_dead else "○"
        return f"{status} {self.name} ({self.character_type})"


class Mark(models.Model):
    character = models.ForeignKey(VampireCharacter, on_delete=models.CASCADE, related_name='marks')
    description = models.TextField()
    how_concealed = models.TextField(blank=True, help_text="How does the vampire hide this mark?")
    is_removed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "✗" if self.is_removed else "○"
        return f"{status} {self.description[:50]}"


class Diary(models.Model):
    character = models.OneToOneField(VampireCharacter, on_delete=models.CASCADE, related_name='diary')
    description = models.CharField(max_length=200, help_text="Description of the physical diary")
    is_lost = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        status = "✗" if self.is_lost else "○"
        return f"{status} Diary: {self.description}"


class GameSession(models.Model):
    character = models.ForeignKey(VampireCharacter, on_delete=models.CASCADE, related_name='sessions')
    prompt_number = models.IntegerField()
    prompt_entry = models.CharField(max_length=1)  # a, b, or c
    response = models.TextField()
    dice_roll_d10 = models.IntegerField(null=True, blank=True)
    dice_roll_d6 = models.IntegerField(null=True, blank=True)
    next_prompt = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Session {self.id}: Prompt {self.prompt_number}{self.prompt_entry}"


class Prompt(models.Model):
    number = models.IntegerField()
    entry = models.CharField(max_length=1)  # a, b, or c
    text = models.TextField()
    actions = models.JSONField(
        default=list, 
        blank=True,
        help_text="JSON array of required mechanical actions for this prompt"
    )
    
    class Meta:
        unique_together = ['number', 'entry']
        ordering = ['number', 'entry']
    
    def __str__(self):
        return f"Prompt {self.number}{self.entry}"
    
    def get_actions(self):
        """Return the actions as a Python list."""
        return self.actions if self.actions else []
    
    @property
    def has_actions(self):
        """Return True if this prompt has any actions defined."""
        return bool(self.actions and len(self.actions) > 0)
