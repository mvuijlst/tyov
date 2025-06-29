#!/usr/bin/env python
"""
Quick test script to verify AJAX endpoints are accessible.
Run with: python test_ajax_endpoints.py
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vampire_chronicle.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from game.models import VampireCharacter, Memory

def test_ajax_endpoints():
    print("Testing AJAX endpoints...")
    
    # Create a test client
    client = Client()
    
    # Check if we have any users
    user = User.objects.first()
    if not user:
        print("No users found. Please create a user first.")
        return
    
    # Log in as the user
    client.force_login(user)
    
    # Check if we have any characters
    character = VampireCharacter.objects.filter(user=user).first()
    if not character:
        print("No characters found. Please create a character first.")
        return
    
    print(f"Testing with character: {character.name}")
    
    # Test add_experience endpoint
    memory = character.memories.first()
    if memory:
        response = client.post(f'/characters/{character.id}/add-experience/', {
            'memory_id': memory.id,
            'text': 'Test experience via script'
        })
        print(f"Add experience response status: {response.status_code}")
        if response.status_code == 200:
            print(f"Add experience response: {response.json()}")
    
    # Test add_skill endpoint
    response = client.post(f'/characters/{character.id}/add-skill/', {
        'name': 'Test Skill',
        'description': 'A test skill'
    })
    print(f"Add skill response status: {response.status_code}")
    if response.status_code == 200:
        print(f"Add skill response: {response.json()}")
    
    # Test add_resource endpoint
    response = client.post(f'/characters/{character.id}/add-resource/', {
        'name': 'Test Resource',
        'description': 'A test resource',
        'is_stationary': False
    })
    print(f"Add resource response status: {response.status_code}")
    if response.status_code == 200:
        print(f"Add resource response: {response.json()}")
    
    print("Test completed!")

if __name__ == '__main__':
    test_ajax_endpoints()
