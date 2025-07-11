# Generated by Django 5.2.3 on 2025-06-26 12:53

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Prompt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField()),
                ('entry', models.CharField(max_length=1)),
                ('text', models.TextField()),
            ],
            options={
                'ordering': ['number', 'entry'],
                'unique_together': {('number', 'entry')},
            },
        ),
        migrations.CreateModel(
            name='VampireCharacter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('current_prompt', models.IntegerField(default=1)),
                ('prompt_entry', models.CharField(default='a', max_length=1)),
                ('game_ended', models.BooleanField(default=False)),
                ('origin_description', models.TextField(help_text='Who were they before becoming a vampire?')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('is_checked', models.BooleanField(default=False)),
                ('is_lost', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='game.vampirecharacter')),
            ],
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('is_stationary', models.BooleanField(default=False)),
                ('is_lost', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resources', to='game.vampirecharacter')),
            ],
        ),
        migrations.CreateModel(
            name='Memory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('order', models.IntegerField()),
                ('is_in_diary', models.BooleanField(default=False)),
                ('is_lost', models.BooleanField(default=False)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='memories', to='game.vampirecharacter')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('character', 'order')},
            },
        ),
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('how_concealed', models.TextField(blank=True, help_text='How does the vampire hide this mark?')),
                ('is_removed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marks', to='game.vampirecharacter')),
            ],
        ),
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt_number', models.IntegerField()),
                ('prompt_entry', models.CharField(max_length=1)),
                ('response', models.TextField()),
                ('dice_roll_d10', models.IntegerField(blank=True, null=True)),
                ('dice_roll_d6', models.IntegerField(blank=True, null=True)),
                ('next_prompt', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('character', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='game.vampirecharacter')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Diary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(help_text='Description of the physical diary', max_length=200)),
                ('is_lost', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('character', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='diary', to='game.vampirecharacter')),
            ],
        ),
        migrations.CreateModel(
            name='Character',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('character_type', models.CharField(choices=[('mortal', 'Mortal'), ('immortal', 'Immortal')], max_length=20)),
                ('relationship', models.CharField(choices=[('friend', 'Friend'), ('enemy', 'Enemy'), ('neutral', 'Neutral'), ('lover', 'Lover'), ('family', 'Family'), ('servant', 'Servant'), ('master', 'Master')], default='neutral', max_length=20)),
                ('is_dead', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('vampire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characters', to='game.vampirecharacter')),
            ],
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('order', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('memory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiences', to='game.memory')),
            ],
            options={
                'ordering': ['order'],
                'unique_together': {('memory', 'order')},
            },
        ),
    ]
