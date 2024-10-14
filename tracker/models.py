from django.db import models
from django.contrib.auth.models import User


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


class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    start_time = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'start_time']),
        ]


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
