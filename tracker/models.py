from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class MuscleGroup(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField(max_length=100)
    muscle_groups = models.ManyToManyField(MuscleGroup, related_name='exercises')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['name', 'user']

    def __str__(self):
        return self.name


# models.py
class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Общие заметки о тренировке")
    mood = models.CharField(
        max_length=20,
        choices=[
            ('great', 'Отличное'),
            ('good', 'Хорошее'),
            ('normal', 'Нормальное'),
            ('tired', 'Уставший'),
            ('bad', 'Плохое')
        ],
        blank=True,
        help_text="Самочувствие во время тренировки"
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', 'start_time']),
        ]

    def __str__(self):
        return self.title or f"Тренировка от {self.start_time}"


class WorkoutExercise(models.Model):
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('workout', 'exercise')

    def __str__(self):
        return f"{self.exercise.name} в {self.workout}"


class Set(models.Model):
    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE)
    repetitions = models.PositiveIntegerField()
    weight = models.FloatField()
    rest_time = models.DurationField(
        null=True, 
        blank=True,
        help_text="Время отдыха после этого подхода"
    )

    def __str__(self):
        base = f"{self.repetitions} повторений с весом {self.weight} кг"
        if self.rest_time:
            return f"{base} (отдых: {self.rest_time})"
        return base


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
