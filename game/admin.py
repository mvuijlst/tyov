from django.contrib import admin
from .models import (
    VampireCharacter, Memory, Experience, Skill, Resource,
    Character, Mark, Diary, GameSession, Prompt
)


@admin.register(VampireCharacter)
class VampireCharacterAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'current_prompt', 'prompt_entry', 'game_ended', 'created_at']
    list_filter = ['game_ended', 'created_at', 'user']
    search_fields = ['name', 'user__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ['character', 'order', 'title', 'is_in_diary', 'is_lost']
    list_filter = ['is_in_diary', 'is_lost', 'character']
    ordering = ['character', 'order']


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['memory', 'order', 'text_preview', 'created_at']
    list_filter = ['created_at', 'memory__character']
    search_fields = ['text']
    
    def text_preview(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Text Preview'


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['character', 'name', 'is_checked', 'is_lost', 'created_at']
    list_filter = ['is_checked', 'is_lost', 'created_at']
    search_fields = ['name', 'character__name']


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['character', 'name', 'is_stationary', 'is_lost', 'created_at']
    list_filter = ['is_stationary', 'is_lost', 'created_at']
    search_fields = ['name', 'character__name']


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ['vampire', 'name', 'character_type', 'relationship', 'is_dead', 'created_at']
    list_filter = ['character_type', 'relationship', 'is_dead', 'created_at']
    search_fields = ['name', 'vampire__name']


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ['character', 'description_preview', 'is_removed', 'created_at']
    list_filter = ['is_removed', 'created_at']
    search_fields = ['description', 'character__name']
    
    def description_preview(self, obj):
        return obj.description[:50] + "..." if len(obj.description) > 50 else obj.description
    description_preview.short_description = 'Description Preview'


@admin.register(Diary)
class DiaryAdmin(admin.ModelAdmin):
    list_display = ['character', 'description', 'is_lost', 'created_at']
    list_filter = ['is_lost', 'created_at']
    search_fields = ['description', 'character__name']


@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['character', 'prompt_number', 'prompt_entry', 'dice_rolls', 'next_prompt', 'created_at']
    list_filter = ['prompt_number', 'created_at', 'character']
    search_fields = ['character__name', 'response']
    readonly_fields = ['created_at']
    
    def dice_rolls(self, obj):
        if obj.dice_roll_d10 and obj.dice_roll_d6:
            return f"{obj.dice_roll_d10} - {obj.dice_roll_d6} = {obj.dice_roll_d10 - obj.dice_roll_d6}"
        return "-"
    dice_rolls.short_description = 'Dice Roll'


@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ['prompt_id', 'text_preview', 'action_count', 'has_actions']
    list_filter = ['number', 'entry']
    ordering = ['number', 'entry']
    search_fields = ['text', 'number']
    readonly_fields = ['prompt_id', 'action_preview']
    
    def prompt_id(self, obj):
        return f"{obj.number}{obj.entry}"
    prompt_id.short_description = 'Prompt ID'
    prompt_id.admin_order_field = 'number'
    
    def text_preview(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Text Preview'
    
    def action_count(self, obj):
        return len(obj.actions) if obj.actions else 0
    action_count.short_description = 'Actions'
    
    def has_actions(self, obj):
        return bool(obj.actions and len(obj.actions) > 0)
    has_actions.boolean = True
    has_actions.short_description = 'Has Actions'
    
    def action_preview(self, obj):
        if not obj.actions:
            return "No actions defined"
        
        preview = []
        for i, action in enumerate(obj.actions[:3], 1):  # Show first 3 actions
            action_type = action.get('type', 'unknown')
            description = action.get('description', '')
            preview.append(f"{i}. {action_type}: {description[:50]}")
        
        if len(obj.actions) > 3:
            preview.append(f"... and {len(obj.actions) - 3} more")
        
        return "\n".join(preview)
    action_preview.short_description = 'Action Preview'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('number', 'entry', 'text')
        }),
        ('Actions', {
            'fields': ('actions', 'action_preview'),
            'description': 'JSON array of mechanical actions required for this prompt. '
                          'Use the format: [{"type": "action_type", "description": "description", ...}]'
        })
    )
    
    class Media:
        css = {
            'all': ('admin/css/prompt_admin.css',)
        }
        js = ('admin/js/prompt_admin.js',)
