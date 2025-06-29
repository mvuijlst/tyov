from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse
import random
import json

from .models import (
    VampireCharacter, Memory, Experience, Skill, Resource, 
    Character, Mark, Diary, GameSession, Prompt
)
from .forms import (
    VampireCreationForm, ExperienceForm, SkillForm, ResourceForm,
    CharacterForm, MarkForm, DiaryForm
)


def home(request):
    """Home page with game introduction."""
    return render(request, 'game/home.html')


def register(request):
    """User registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to Thousand Year Old Vampire!')
            return redirect('character_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def character_list(request):
    """List all characters for the current user."""
    characters = VampireCharacter.objects.filter(user=request.user)
    return render(request, 'game/character_list.html', {'characters': characters})


@login_required
def create_character(request):
    """Create a new vampire character."""
    if request.method == 'POST':
        form = VampireCreationForm(request.POST)
        if form.is_valid():
            character = form.save(commit=False)
            character.user = request.user
            character.save()
            
            # Create initial 5 memory slots
            for i in range(1, 6):
                Memory.objects.create(character=character, order=i)
            
            # Create the first experience in Memory 1 from the origin description
            memory_1 = Memory.objects.get(character=character, order=1)
            Experience.objects.create(
                memory=memory_1,
                text=character.origin_description,
                order=1
            )
            
            messages.success(request, f'Created vampire character: {character.name}')
            return redirect('setup_character', character_id=character.id)
    else:
        form = VampireCreationForm()
    
    return render(request, 'game/create_character.html', {'form': form})


@login_required
def character_detail(request, character_id):
    """Show character sheet and current state."""
    character = get_object_or_404(VampireCharacter, id=character_id, user=request.user)
    
    context = {
        'character': character,
        'memories': character.memories.all(),
        'skills': character.skills.filter(is_lost=False),
        'resources': character.resources.filter(is_lost=False),
        'characters': character.characters.filter(is_dead=False),
        'marks': character.marks.filter(is_removed=False),
        'diary': getattr(character, 'diary', None),
        'recent_sessions': character.sessions.all()[:5],
    }
    
    return render(request, 'game/character_detail.html', context)


@login_required
def play_game(request, character_id):
    """Main game interface for playing through prompts."""
    character = get_object_or_404(VampireCharacter, id=character_id, user=request.user)
    
    # Check if character setup is complete
    try:
        setup_complete = (
            character.skills.count() >= 3 and 
            character.resources.count() >= 3 and
            character.characters.filter(character_type='immortal').exists() and
            character.marks.exists() and
            character.memories.get(order=5).experiences.exists()
        )
    except Memory.DoesNotExist:
        setup_complete = False
    
    if not setup_complete:
        messages.warning(request, 'Please complete character setup before beginning the game.')
        return redirect('setup_character', character_id=character.id)
    
    if character.game_ended:
        messages.info(request, 'This character\'s story has ended.')
        return redirect('character_detail', character_id=character.id)
    
    # Get current prompt
    try:
        current_prompt = Prompt.objects.get(
            number=character.current_prompt,
            entry=character.prompt_entry
        )
    except Prompt.DoesNotExist:
        messages.error(request, 'Prompt not found. The game may not be fully loaded.')
        return redirect('character_detail', character_id=character.id)
    
    # Handle returning from action selection
    if request.GET.get('actions_completed'):
        response = request.session.get('pending_response', '')
        if response.strip():
            # Process completed actions and continue with dice rolling
            pass  # Logic will continue below
        else:
            messages.error(request, 'Session expired. Please submit your response again.')
            return redirect('play_game', character_id=character.id)
    elif request.method == 'POST':
        response = request.POST.get('response', '')
    else:
        response = ''
    
    if response.strip():
        
        # Create an experience for this prompt response
        # Find an available memory slot or create new memory if needed
        available_memory = None
        for memory in character.memories.filter(is_lost=False).order_by('order'):
            if memory.experiences.count() < 3:
                available_memory = memory
                break
        
        if not available_memory:
            # Need to create a new memory, which means losing an old one
            oldest_memory = character.memories.filter(is_lost=False).order_by('order').first()
            if oldest_memory:
                oldest_memory.is_lost = True
                oldest_memory.save()
                messages.info(request, f"Lost memory: {oldest_memory.title or 'Untitled'}")
            
            # Reuse the memory slot
            available_memory = oldest_memory
            available_memory.is_lost = False
            available_memory.title = f"Prompt {character.current_prompt}{character.prompt_entry}"
            available_memory.save()
            
            # Clear old experiences
            available_memory.experiences.all().delete()
        
        # Add the new experience
        experience_order = available_memory.experiences.count() + 1
        Experience.objects.create(
            memory=available_memory,
            text=response,
            order=experience_order
        )
        
        # Roll dice for next prompt
        d10 = random.randint(1, 10)
        d6 = random.randint(1, 6)
        movement = d10 - d6
        
        next_prompt_num = character.current_prompt + movement
        next_prompt_num = max(1, next_prompt_num)  # Can't go below prompt 1
        
        # Save session
        session = GameSession.objects.create(
            character=character,
            prompt_number=character.current_prompt,
            prompt_entry=character.prompt_entry,
            response=response,
            dice_roll_d10=d10,
            dice_roll_d6=d6,
            next_prompt=next_prompt_num
        )
        
        # Update character's current prompt
        character.current_prompt = next_prompt_num
        character.prompt_entry = 'a'  # Always start with 'a' when moving to new prompt
        
        # Check if we've been to this prompt before
        previous_sessions = GameSession.objects.filter(
            character=character,
            prompt_number=next_prompt_num
        ).count()
        
        if previous_sessions == 1:
            character.prompt_entry = 'b'
        elif previous_sessions >= 2:
            character.prompt_entry = 'c'
            
        character.save()
        
        # Create success message
        messages.success(request, f'Rolled {d10} - {d6} = {movement}. Moving to prompt {next_prompt_num}.')
        return redirect('play_game', character_id=character.id)
    
    context = {
        'character': character,
        'prompt': current_prompt,
        'memories': character.memories.all(),
        'skills': character.skills.filter(is_lost=False),
        'resources': character.resources.filter(is_lost=False),
        'characters': character.characters.filter(is_dead=False),
        'marks': character.marks.filter(is_removed=False),
    }
    
    return render(request, 'game/play.html', context)


@login_required
@require_http_methods(["POST"])
def add_experience(request, character_id):
    """Add a new experience to a memory via AJAX."""
    character = get_object_or_404(VampireCharacter, id=character_id, user=request.user)
    
    memory_id = request.POST.get('memory_id')
    text = request.POST.get('text', '').strip()
    
    if not text:
        return JsonResponse({'success': False, 'error': 'Experience text is required'})
    
    try:
        memory = Memory.objects.get(id=memory_id, character=character)
        
        # Check if memory has space (max 3 experiences)
        experience_count = memory.experiences.count()
        if experience_count >= 3:
            return JsonResponse({'success': False, 'error': 'Memory is full (max 3 experiences)'})
        
        experience = Experience.objects.create(
            memory=memory,
            text=text,
            order=experience_count + 1
        )
        
        return JsonResponse({
            'success': True,
            'experience': {
                'id': experience.id,
                'text': experience.text,
                'order': experience.order
            }
        })
        
    except Memory.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Memory not found'})


@login_required
@require_http_methods(["POST"])
def add_skill(request, character_id):
    """Add a new skill via AJAX."""
    character = get_object_or_404(VampireCharacter, id=character_id, user=request.user)
    
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    
    if not name:
        return JsonResponse({'success': False, 'error': 'Skill name is required'})
    
    skill = Skill.objects.create(character=character, name=name, description=description)
    
    return JsonResponse({
        'success': True,
        'skill': {
            'id': skill.id,
            'name': skill.name,
            'description': skill.description,
            'is_checked': skill.is_checked
        }
    })


@login_required
@require_http_methods(["POST"])
def toggle_skill(request, character_id, skill_id):
    """Toggle a skill's checked status."""
    character = get_object_or_404(VampireCharacter, id=character_id, user=request.user)
    skill = get_object_or_404(Skill, id=skill_id, character=character)
    
    if not skill.is_checked:  # Can only check once
        skill.is_checked = True
        skill.save()
        return JsonResponse({'success': True, 'checked': True})
    
    return JsonResponse({'success': False, 'error': 'Skill already checked'})


@login_required
@require_http_methods(["POST"])
def add_resource(request, character_id):
    """Add a new resource via AJAX."""
    character = get_object_or_404(VampireCharacter, id=character_id, user=request.user)
    
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    is_stationary = request.POST.get('is_stationary') == 'on'
    
    if not name:
        return JsonResponse({'success': False, 'error': 'Resource name is required'})
    
    resource = Resource.objects.create(
        character=character,
        name=name,
        description=description,
        is_stationary=is_stationary
    )
    
    return JsonResponse({
        'success': True,
        'resource': {
            'id': resource.id,
            'name': resource.name,
            'description': resource.description,
            'is_stationary': resource.is_stationary
        }
    })


@login_required
@require_http_methods(["POST"])
def add_character(request, character_id):
    """Add a new character via AJAX."""
    vampire = get_object_or_404(VampireCharacter, id=character_id, user=request.user)
    
    name = request.POST.get('name', '').strip()
    description = request.POST.get('description', '').strip()
    character_type = request.POST.get('character_type', 'mortal')
    relationship = request.POST.get('relationship', 'neutral')
    
    if not name:
        return JsonResponse({'success': False, 'error': 'Character name is required'})
    
    character = Character.objects.create(
        vampire=vampire,
        name=name,
        description=description,
        character_type=character_type,
        relationship=relationship
    )
    
    return JsonResponse({
        'success': True,
        'character': {
            'id': character.id,
            'name': character.name,
            'description': character.description,
            'character_type': character.character_type,
            'relationship': character.relationship
        }
    })


@login_required
@require_http_methods(["POST"])
def add_mark(request, character_id):
    """Add a new mark via AJAX."""
    character = get_object_or_404(VampireCharacter, id=character_id, user=request.user)
    
    description = request.POST.get('description', '').strip()
    how_concealed = request.POST.get('how_concealed', '').strip()
    
    if not description:
        return JsonResponse({'success': False, 'error': 'Mark description is required'})
    
    mark = Mark.objects.create(
        character=character,
        description=description,
        how_concealed=how_concealed
    )
    
    return JsonResponse({
        'success': True,
        'mark': {
            'id': mark.id,
            'description': mark.description,
            'how_concealed': mark.how_concealed
        }
    })


@login_required
def dice_roller(request):
    """Simple dice roller for the game."""
    if request.method == 'POST':
        d10 = random.randint(1, 10)
        d6 = random.randint(1, 6)
        result = d10 - d6
        
        return JsonResponse({
            'd10': d10,
            'd6': d6,
            'result': result
        })
    
    return render(request, 'game/dice_roller.html')


@login_required
def setup_character(request, character_id):
    """Multi-step character setup following the game rules."""
    character = get_object_or_404(VampireCharacter, id=character_id, user=request.user)
    
    # Check if character is already set up
    try:
        setup_complete = (
            character.skills.count() >= 3 and 
            character.resources.count() >= 3 and
            character.characters.filter(character_type='immortal').exists() and
            character.marks.exists() and
            character.memories.get(order=5).experiences.exists()
        )
    except Memory.DoesNotExist:
        setup_complete = False
    
    if setup_complete:
        messages.info(request, 'Character setup is already complete.')
        return redirect('character_detail', character_id=character.id)
    
    # Determine current setup step
    step = request.GET.get('step', '1')
    
    context = {
        'character': character,
        'step': step,
        'memories': character.memories.all(),
    }
    
    if request.method == 'POST':
        if step == '1':
            # Step 1: Create 3 mortals
            return handle_setup_step_1(request, character)
        elif step == '2':
            # Step 2: Create 3 skills and 3 resources
            return handle_setup_step_2(request, character)
        elif step == '3':
            # Step 3: Create 3 additional experiences
            return handle_setup_step_3(request, character)
        elif step == '4':
            # Step 4: Create immortal, mark, and final experience
            return handle_setup_step_4(request, character)
    
    return render(request, 'game/setup_character.html', context)


def handle_setup_step_1(request, character):
    """Handle creation of 3 mortal characters."""
    for i in range(3):
        name = request.POST.get(f'mortal_{i}_name', '').strip()
        description = request.POST.get(f'mortal_{i}_description', '').strip()
        relationship = request.POST.get(f'mortal_{i}_relationship', 'neutral')
        
        if name and description:
            Character.objects.create(
                vampire=character,
                name=name,
                description=description,
                character_type='mortal',
                relationship=relationship
            )
    
    return redirect(f"{reverse('setup_character', args=[character.id])}?step=2")


def handle_setup_step_2(request, character):
    """Handle creation of 3 skills and 3 resources."""
    # Create skills
    for i in range(3):
        skill_name = request.POST.get(f'skill_{i}', '').strip()
        skill_description = request.POST.get(f'skill_{i}_description', '').strip()
        if skill_name:
            Skill.objects.create(
                character=character, 
                name=skill_name,
                description=skill_description
            )
    
    # Create resources
    for i in range(3):
        resource_name = request.POST.get(f'resource_{i}_name', '').strip()
        resource_desc = request.POST.get(f'resource_{i}_description', '').strip()
        is_stationary = request.POST.get(f'resource_{i}_stationary') == 'on'
        
        if resource_name:
            Resource.objects.create(
                character=character,
                name=resource_name,
                description=resource_desc,
                is_stationary=is_stationary
            )
    
    return redirect(f"{reverse('setup_character', args=[character.id])}?step=3")


def handle_setup_step_3(request, character):
    """Handle creation of 3 additional experiences combining traits."""
    for i in range(3):
        memory_order = i + 2  # Memories 2, 3, 4
        experience_text = request.POST.get(f'experience_{i}', '').strip()
        
        if experience_text:
            memory = Memory.objects.get(character=character, order=memory_order)
            Experience.objects.create(
                memory=memory,
                text=experience_text,
                order=1
            )
    
    return redirect(f"{reverse('setup_character', args=[character.id])}?step=4")


def handle_setup_step_4(request, character):
    """Handle creation of immortal, mark, and transformation experience."""
    # Create immortal
    immortal_name = request.POST.get('immortal_name', '').strip()
    immortal_desc = request.POST.get('immortal_description', '').strip()
    
    if immortal_name and immortal_desc:
        Character.objects.create(
            vampire=character,
            name=immortal_name,
            description=immortal_desc,
            character_type='immortal',
            relationship='master'
        )
    
    # Create mark
    mark_desc = request.POST.get('mark_description', '').strip()
    mark_concealed = request.POST.get('mark_concealed', '').strip()
    
    if mark_desc:
        Mark.objects.create(
            character=character,
            description=mark_desc,
            how_concealed=mark_concealed
        )
    
    # Create transformation experience in Memory 5
    transformation_exp = request.POST.get('transformation_experience', '').strip()
    if transformation_exp:
        memory_5 = Memory.objects.get(character=character, order=5)
        Experience.objects.create(
            memory=memory_5,
            text=transformation_exp,
            order=1
        )
    
    messages.success(request, 'Character setup complete! Your vampire is ready to begin their dark chronicle.')
    return redirect('character_detail', character_id=character.id)



