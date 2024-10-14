from django.contrib import admin
from .models import Workout, Exercise, Set, MuscleGroup, WorkoutExercise


@admin.register(MuscleGroup)
class MuscleGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        queryset.delete()

    delete_selected.short_description = 'Удалить выбранные мышечные группы'


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    filter_horizontal = ('muscle_groups',)


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_time', 'duration')
    search_fields = ('user__username',)
    list_filter = ('start_time', 'duration')
    ordering = ('-start_time',)  # Сортировка по дате тренировки (новые сверху)


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('workout', 'exercise')
    search_fields = ('workout__user__username', 'exercise__name')
    list_filter = ('workout', 'exercise')


@admin.register(Set)
class SetAdmin(admin.ModelAdmin):
    list_display = ('workout_exercise', 'repetitions', 'weight')
    search_fields = ('workout_exercise__workout__user__username', 'workout_exercise__exercise__name')
    list_filter = ('workout_exercise',)
