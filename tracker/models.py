from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class MuscleGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    muscle_groups = models.ManyToManyField(MuscleGroup, blank=True)  # Разрешить пустые

    def __str__(self):
        return self.name


# models.py
class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    title = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True, blank=True)

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
        unique_together = ('workout', 'exercise')  # Предотвращение дублирования

    def __str__(self):
        return f"{self.exercise.name} in {self.workout}"


class Set(models.Model):
    workout_exercise = models.ForeignKey(WorkoutExercise, on_delete=models.CASCADE)
    repetitions = models.PositiveIntegerField()
    weight = models.FloatField()

    def __str__(self):
        return f"{self.repetitions} reps at {self.weight} kg"


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
