from django import forms
from .models import (
    VampireCharacter, Experience, Skill, Resource, 
    Character, Mark, Diary
)


class VampireCreationForm(forms.ModelForm):
    class Meta:
        model = VampireCharacter
        fields = ['name', 'origin_description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your vampire\'s name'
            }),
            'origin_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'I am [Name], [parentage/origin], born [where and when]; [key circumstances of their mortal life]. Write in first person as your vampire\'s first memory of their mortal existence.'
            })
        }
        help_texts = {
            'origin_description': 'This becomes your first Experience in Memory 1. Include when/where born, who they were, and their mortal circumstances.'
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe this experience in a single evocative sentence...'
            })
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Skill name (e.g., "Swordplay", "I Do Not Blink The Sand Away")'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional description of what this skill does or how it\'s used'
            })
        }
        help_texts = {
            'description': 'Optional description to help you remember what this skill does or how your vampire uses it.'
        }


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['name', 'description', 'is_stationary']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Resource name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Brief description...'
            }),
            'is_stationary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'description', 'character_type', 'relationship']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Character name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Brief description of this character...'
            }),
            'character_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'relationship': forms.Select(attrs={
                'class': 'form-select'
            })
        }


class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['description', 'how_concealed']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describe the mark (e.g., "Eyes that are blank and white", "A trailing specter")'
            }),
            'how_concealed': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'How do you hide this mark?'
            })
        }


class DiaryForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['description']
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Describe the diary (e.g., "a sturdy, leather-bound book")'
            })
        }
