# Generated by Django 5.1.2 on 2024-11-25 20:04

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MuscleGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('name', 'user')},
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('muscle_groups', models.ManyToManyField(related_name='exercises', to='tracker.musclegroup')),
            ],
            options={
                'unique_together': {('name', 'user')},
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True)),
                ('avatar', models.ImageField(blank=True, upload_to='avatars/')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('duration', models.DurationField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, help_text='Общие заметки о тренировке')),
                ('mood', models.CharField(blank=True, choices=[('great', 'Отличное'), ('good', 'Хорошее'), ('normal', 'Нормальное'), ('tired', 'Уставший'), ('bad', 'Плохое')], help_text='Самочувствие во время тренировки', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WorkoutExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.exercise')),
                ('workout', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.workout')),
            ],
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repetitions', models.PositiveIntegerField()),
                ('weight', models.FloatField()),
                ('rest_time', models.DurationField(blank=True, help_text='Время отдыха после этого подхода', null=True)),
                ('workout_exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tracker.workoutexercise')),
            ],
        ),
        migrations.AddIndex(
            model_name='workout',
            index=models.Index(fields=['user', 'start_time'], name='tracker_wor_user_id_837574_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='workoutexercise',
            unique_together={('workout', 'exercise')},
        ),
    ]
