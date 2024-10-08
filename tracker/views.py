import calendar
from datetime import datetime

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .filters import ExerciseFilter, MuscleGroupFilter
from .filters import WorkoutFilter
from .forms import WorkoutForm, ExerciseForm, MuscleGroupForm, WorkoutExerciseForm
from .models import Workout, Exercise, MuscleGroup, WorkoutExercise, Set


def home(request):
    if request.user.is_authenticated:
        return redirect('workout_history')
    else:
        return render(request, 'tracker/home.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('workout_history')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
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
    workout = Workout.objects.create(user=request.user)
    return redirect('workout_session', workout_id=workout.id)


@login_required
def workout_session(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    exercises = WorkoutExercise.objects.filter(workout=workout)
    if request.method == 'POST':
        # Обработка завершения тренировки
        workout.duration = timezone.now() - workout.start_time
        workout.save()
        return redirect('workout_history')
    else:
        form = WorkoutExerciseForm(user=request.user)
    return render(request, 'tracker/workout_session.html', {'workout': workout, 'exercises': exercises, 'form': form})


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
    else:
        form = WorkoutExerciseForm(user=request.user)
    return render(request, 'tracker/add_workout_exercise.html', {'form': form, 'workout': workout})


@login_required
def add_set_ajax(request):
    if request.method == 'POST':
        workout_exercise_id = request.POST.get('workout_exercise_id')
        repetitions = request.POST.get('repetitions')
        weight = request.POST.get('weight')
        workout_exercise = get_object_or_404(WorkoutExercise, id=workout_exercise_id, workout__user=request.user)
        set_instance = Set.objects.create(
            workout_exercise=workout_exercise,
            repetitions=repetitions,
            weight=weight
        )
        return JsonResponse({'set_info': f"{set_instance.repetitions} reps at {set_instance.weight} kg"})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def workout_history(request):
    workout_filter = WorkoutFilter(request.GET,
                                   queryset=Workout.objects.filter(user=request.user).order_by('-start_time'))
    paginator = Paginator(workout_filter.qs, 10)  # 10 тренировок на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'tracker/workout_history.html', {'filter': workout_filter, 'page_obj': page_obj})


@login_required
def workout_list(request):
    workouts = Workout.objects.filter(user=request.user).order_by('-start_time')
    return render(request, 'tracker/workout_list.html', {'workouts': workouts})


@login_required
def workout_detail(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    exercises = WorkoutExercise.objects.filter(workout=workout)
    return render(request, 'tracker/workout_detail.html', {'workout': workout, 'exercises': exercises})


@login_required
def progress(request):
    workouts = Workout.objects.filter(user=request.user).order_by('start_time')
    labels = [workout.start_time.strftime('%Y-%m-%d %H:%M') for workout in workouts]
    data = [workout.duration.total_seconds() / 60 if workout.duration else 0 for workout in workouts]
    context = {
        'labels': labels,
        'data': data,
    }
    return render(request, 'tracker/progress.html', context)


@login_required
def edit_workout(request, workout_id):
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
            form.save()
            return redirect('workout_history')
    else:
        form = WorkoutForm(instance=workout)
    return render(request, 'tracker/edit_workout.html', {'form': form, 'workout': workout})


@login_required
def calendar_view(request, year=None, month=None):
    user = request.user
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    year = int(year)
    month = int(month)

    # Получаем все тренировки пользователя в указанном месяце
    workouts = Workout.objects.filter(
        user=user,
        start_time__year=year,
        start_time__month=month
    )

    # Получаем список дней, когда были тренировки
    workout_days = workouts.values_list('start_time__day', flat=True)

    # Создаем объект календаря
    cal = calendar.Calendar(firstweekday=0)  # Неделя начинается с понедельника

    month_days = cal.monthdayscalendar(year, month)

    # Рассчитываем предыдущий и следующий месяцы
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    context = {
        'year': year,
        'month': month,
        'month_days': month_days,
        'workout_days': workout_days,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
        'month_name': MONTH_NAMES.get(month, ''),
        'workouts': workouts,
    }
    return render(request, 'tracker/calendar.html', context)


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


@login_required
def workout_history(request):
    workout_filter = WorkoutFilter(request.GET,
                                   queryset=Workout.objects.filter(user=request.user).order_by('-start_time'))
    return render(request, 'tracker/workout_history.html', {'filter': workout_filter})
