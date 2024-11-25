import calendar
import json
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Max
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.utils import timezone

from .filters import WorkoutFilter, ExerciseFilter, MuscleGroupFilter
from .forms import WorkoutForm, ExerciseForm, MuscleGroupForm, WorkoutExerciseForm
from .models import Exercise, MuscleGroup, WorkoutExercise, Set
from .models import Workout


def home(request):
    if request.user.is_authenticated:
        return redirect('workout_history')
    else:
        return render(request, 'tracker/home.html')


def create_default_exercises(user):
    # Создаем группы мышц
    muscle_groups = {
        'chest': MuscleGroup.objects.create(name='Грудные мышцы', user=user),
        'back': MuscleGroup.objects.create(name='Спина', user=user),
        'legs': MuscleGroup.objects.create(name='Ноги', user=user),
        'shoulders': MuscleGroup.objects.create(name='Плечи', user=user),
        'arms': MuscleGroup.objects.create(name='Руки', user=user),
        'abs': MuscleGroup.objects.create(name='Пресс', user=user),
    }

    # Словарь упражнений: {'название': ['группа_мышц1', 'группа_мышц2']}
    exercises_data = {
        'Жим штанги лежа': ['chest', 'shoulders'],
        'Отжимания от пола': ['chest', 'shoulders', 'arms'],
        'Разведение гантелей лежа': ['chest'],
        
        'Подтягивания': ['back', 'arms'],
        'Тяга штанги в наклоне': ['back'],
        'Гиперэкстензия': ['back'],
        
        'Приседания со штангой': ['legs'],
        'Жим ногами': ['legs'],
        'Выпады с гантелями': ['legs'],
        
        'Жим штанги стоя': ['shoulders'],
        'Разведение гантелей в стороны': ['shoulders'],
        
        'Подъем штанги на бицепс': ['arms'],
        'Французский жим': ['arms'],
        'Молотки': ['arms'],
        
        'Скручивания': ['abs'],
        'Планка': ['abs'],
        'Подъем ног в висе': ['abs'],
    }

    # Создаем упражнения и связываем их с группами мышц
    for exercise_name, muscle_group_keys in exercises_data.items():
        exercise = Exercise.objects.create(name=exercise_name, user=user)
        for key in muscle_group_keys:
            exercise.muscle_groups.add(muscle_groups[key])


def signup(request):
    if request.user.is_authenticated:
        return redirect('workout_history')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_default_exercises(user)  # Создаем упражнения для нового пользователя
            login(request, user)
            messages.success(request, 'Регистрация успешна! Мы добавили список стандартных упражнений.')
            return redirect('workout_history')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def muscle_groups(request):
    muscle_group_filter = MuscleGroupFilter(request.GET, queryset=MuscleGroup.objects.filter(user=request.user))
    if request.method == 'POST':
        form = MuscleGroupForm(request.POST)
        if form.is_valid():
            muscle_group = form.save(commit=False)
            muscle_group.user = request.user
            muscle_group.save()
            return redirect('muscle_groups')
    else:
        form = MuscleGroupForm()
    return render(request, 'tracker/muscle_groups.html', {'filter': muscle_group_filter, 'form': form})


@login_required
def exercises(request):
    exercise_filter = ExerciseFilter(request.GET, queryset=Exercise.objects.filter(user=request.user),
                                     user=request.user)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, user=request.user)
        if form.is_valid():
            exercise = form.save(commit=False)
            exercise.user = request.user
            exercise.save()
            form.save_m2m()
            return redirect('exercises')
    else:
        form = ExerciseForm(user=request.user)
    return render(request, 'tracker/exercises.html', {'filter': exercise_filter, 'form': form})


@login_required
def start_workout(request):
    active_workout = Workout.objects.filter(user=request.user, duration__isnull=True).first()
    if active_workout:
        messages.warning(request, 'Чтобы начать новую тренировку, завершите текущую.')
        return redirect('workout_session', workout_id=active_workout.id)
    workout = Workout.objects.create(user=request.user)
    return redirect('workout_session', workout_id=workout.id)


@login_required
def workout_session(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    workout_exercises = WorkoutExercise.objects.filter(workout=workout)
    if request.method == 'POST':
        # Обработка завершения тренировки
        workout.duration = timezone.now() - workout.start_time
        workout.save()
        return redirect('workout_history')
    else:
        form = WorkoutExerciseForm(user=request.user)
    return render(request, 'tracker/workout_session.html', {
        'workout': workout, 
        'exercises': workout_exercises, 
        'form': form
    })


@login_required
def add_workout_exercise(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        form = WorkoutExerciseForm(request.POST, user=request.user)
        if form.is_valid():
            workout_exercise = form.save(commit=False)
            workout_exercise.workout = workout
            workout_exercise.save()
            return redirect('workout_session', workout_id=workout.id)
    return redirect('workout_session', workout_id=workout.id)


@login_required
def add_set_ajax(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            workout_exercise_id = data.get('workout_exercise_id')
            repetitions = data.get('repetitions')
            weight = data.get('weight')
            workout_exercise = get_object_or_404(WorkoutExercise, id=workout_exercise_id, workout__user=request.user)
            set_instance = Set.objects.create(
                workout_exercise=workout_exercise,
                repetitions=repetitions,
                weight=weight
            )
            return JsonResponse({'set_info': f"{set_instance.repetitions} повторений с весом {set_instance.weight} кг"})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def workout_history(request):
    workout_filter = WorkoutFilter(request.GET,
                                   queryset=Workout.objects.filter(user=request.user).order_by('-start_time'))
    workouts = workout_filter.qs.prefetch_related('workoutexercise_set__exercise')
    paginator = Paginator(workouts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'tracker/workout_history.html', {'filter': workout_filter, 'page_obj': page_obj})


@login_required
def workout_list(request):
    workouts = Workout.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'tracker/workout_list.html', {'workouts': workouts})


@login_required
def workout_detail(request, workout_id):
    workout = get_object_or_404(Workout.objects.select_related('user'), id=workout_id, user=request.user)
    exercises = WorkoutExercise.objects.filter(workout=workout).select_related('exercise').prefetch_related('set_set')
    return render(request, 'tracker/workout_detail.html', {'workout': workout, 'exercises': exercises})


@login_required
def progress(request):
    user = request.user

    # Общее время тренировок
    total_duration = Workout.objects.filter(user=user, duration__isnull=False).aggregate(total=Sum('duration'))['total']
    total_minutes = total_duration.total_seconds() / 60 if total_duration else 0

    # Количество тренировок в месяц
    workouts_per_month = Workout.objects.filter(user=user).annotate(month=TruncMonth('start_time')).values(
        'month').annotate(count=Count('id')).order_by('month')

    months = [workout['month'].strftime('%Y-%m') for workout in workouts_per_month]
    workouts_counts = [workout['count'] for workout in workouts_per_month]

    # Прогресс по упражнениям
    exercises = Exercise.objects.filter(user=user)
    exercise_progress = {}
    for exercise in exercises:
        sets = Set.objects.filter(
            workout_exercise__exercise=exercise,
            workout_exercise__workout__user=user
        ).annotate(
            month=TruncMonth('workout_exercise__workout__start_time')
        ).values('month').annotate(
            max_weight=Max('weight'),
            max_reps=Max('repetitions')
        ).order_by('month')

        if sets:
            months_ex = [entry['month'].strftime('%Y-%m') for entry in sets]
            max_weights = [entry['max_weight'] for entry in sets]
            max_reps = [entry['max_reps'] for entry in sets]

            exercise_progress[exercise.name] = {
                'months': months_ex,
                'max_weights': max_weights,
                'max_reps': max_reps,
            }

    context = {
        'total_minutes': total_minutes,
        'months': months,
        'workouts_counts': workouts_counts,
        'exercise_progress': exercise_progress,
        'exercise_count': len(exercise_progress),
    }

    return render(request, 'tracker/progress.html', context)


@login_required
def calendar_view(request, year=None, month=None):
    user = request.user
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    year = int(year)
    month = int(month)

    workouts = Workout.objects.filter(
        user=user,
        start_time__year=year,
        start_time__month=month
    ).prefetch_related('workoutexercise_set__exercise')

    workouts_by_day = {}
    for workout in workouts:
        day = workout.start_time.day
        workouts_by_day.setdefault(day, []).append(workout)

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)

    # Предыдущий и следующий месяцы
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    context = {
        'year': year,
        'month': month,
        'month_days': month_days,
        'workouts_by_day': workouts_by_day,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'month_name': MONTH_NAMES.get(month, ''),
    }
    return render(request, 'tracker/calendar.html', context)


@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
            form.save()
            messages.success(request, 'Тренировка успешно обновлена.')
            return redirect('workout_history')
    else:
        form = WorkoutForm(instance=workout)
    return render(request, 'tracker/edit_workout.html', {'form': form, 'workout': workout})


@login_required
def reset_exercises(request):
    # Удаляем все существующие упражнения и группы мышц пользователя
    Exercise.objects.filter(user=request.user).delete()
    MuscleGroup.objects.filter(user=request.user).delete()
    
    # Создаем стандартный набор заново
    create_default_exercises(request.user)
    
    messages.success(request, 'Упражнения успешно сброшены к стандартному набору!')
    return redirect('exercises')


MONTH_NAMES = {
    1: 'Январь',
    2: 'Февраль',
    3: 'Март',
    4: 'Апрель',
    5: 'Май',
    6: 'Июнь',
    7: 'Июль',
    8: 'Август',
    9: 'Сентябрь',
    10: 'Октябрь',
    11: 'Ноябрь',
    12: 'Декабрь',
}


# --- Редактирование и удаление мышечных групп ---

@login_required
def edit_muscle_group(request, group_id):
    muscle_group = get_object_or_404(MuscleGroup, id=group_id, user=request.user)
    if request.method == 'POST':
        form = MuscleGroupForm(request.POST, instance=muscle_group)
        if form.is_valid():
            form.save()
            return redirect('muscle_groups')
    else:
        form = MuscleGroupForm(instance=muscle_group)
    return render(request, 'tracker/edit_muscle_group.html', {'form': form})


@login_required
def delete_muscle_group(request, group_id):
    muscle_group = get_object_or_404(MuscleGroup, id=group_id, user=request.user)
    if request.method == 'POST':
        muscle_group.delete()
        return redirect('muscle_groups')
    return render(request, 'tracker/delete_muscle_group.html', {'muscle_group': muscle_group})


# --- Редактирование и удаление упражнений ---

@login_required
def edit_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
    if request.method == 'POST':
        form = ExerciseForm(request.POST, instance=exercise, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('exercises')
    else:
        form = ExerciseForm(instance=exercise, user=request.user)
    return render(request, 'tracker/edit_exercise.html', {'form': form})


@login_required
def delete_exercise(request, exercise_id):
    exercise = get_object_or_404(Exercise, id=exercise_id, user=request.user)
    if request.method == 'POST':
        exercise.delete()
        messages.success(request, f'Упражнение "{exercise.name}" было успешно удалено.')
        return redirect('exercises')
    return render(request, 'tracker/delete_exercise.html', {'exercise': exercise})


# --- Редактирование и удаление тренировок ---

@login_required
def delete_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        workout.delete()
        return redirect('workout_history')
    return render(request, 'tracker/delete_workout.html', {'workout': workout})
