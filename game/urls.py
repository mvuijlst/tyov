from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('characters/', views.character_list, name='character_list'),
    path('characters/create/', views.create_character, name='create_character'),
    path('characters/<int:character_id>/setup/', views.setup_character, name='setup_character'),
    path('characters/<int:character_id>/', views.character_detail, name='character_detail'),
    path('characters/<int:character_id>/play/', views.play_game, name='play_game'),
    path('characters/<int:character_id>/add-experience/', views.add_experience, name='add_experience'),
    path('characters/<int:character_id>/add-skill/', views.add_skill, name='add_skill'),
    path('characters/<int:character_id>/skills/<int:skill_id>/toggle/', views.toggle_skill, name='toggle_skill'),
    path('characters/<int:character_id>/add-resource/', views.add_resource, name='add_resource'),
    path('characters/<int:character_id>/add-character/', views.add_character, name='add_character'),
    path('characters/<int:character_id>/add-mark/', views.add_mark, name='add_mark'),
    path('dice/', views.dice_roller, name='dice_roller'),
]
