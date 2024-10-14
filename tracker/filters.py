import django_filters
from .models import Workout, Exercise, MuscleGroup
from django import forms


class WorkoutFilter(django_filters.FilterSet):
    start_time = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'}),
        label='Дата тренировки'
    )
    duration__gte = django_filters.NumberFilter(field_name='duration', lookup_expr='gte',
                                                label='Минимальная продолжительность (сек)')
    duration__lte = django_filters.NumberFilter(field_name='duration', lookup_expr='lte',
                                                label='Максимальная продолжительность (сек)')
    order = django_filters.OrderingFilter(
        fields=(
            ('start_time', 'start_time'),
            ('duration', 'duration'),
        ),
        field_labels={
            'start_time': 'Дата тренировки',
            'duration': 'Продолжительность',
        },
        label='Сортировать по'
    )

    class Meta:
        model = Workout
        fields = ['start_time', 'duration__gte', 'duration__lte', 'order']


class ExerciseFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Название упражнения')
    muscle_groups = django_filters.ModelMultipleChoiceFilter(
        queryset=MuscleGroup.objects.none(),  # Изначально пустой
        widget=forms.CheckboxSelectMultiple,
        label='Мышечные группы'
    )

    class Meta:
        model = Exercise
        fields = ['name', 'muscle_groups']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExerciseFilter, self).__init__(*args, **kwargs)
        if user:
            self.filters['muscle_groups'].queryset = MuscleGroup.objects.filter(user=user)
        else:
            self.filters['muscle_groups'].queryset = MuscleGroup.objects.none()


class MuscleGroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Название мышечной группы')

    class Meta:
        model = MuscleGroup
        fields = ['name']
