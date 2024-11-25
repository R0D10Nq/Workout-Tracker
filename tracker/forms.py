from django import forms
from datetime import timedelta
from .models import Exercise, MuscleGroup, WorkoutExercise, Workout, Set


class MuscleGroupForm(forms.ModelForm):
    class Meta:
        model = MuscleGroup
        fields = ['name']


class ExerciseForm(forms.ModelForm):
    muscle_groups = forms.ModelMultipleChoiceField(
        queryset=MuscleGroup.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Exercise
        fields = ['name', 'muscle_groups']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ExerciseForm, self).__init__(*args, **kwargs)
        self.fields['muscle_groups'].queryset = MuscleGroup.objects.filter(user=user)


class WorkoutForm(forms.ModelForm):
    class Meta:
        model = Workout
        fields = ['title', 'start_time', 'duration', 'notes', 'mood']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'duration': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Заметки о тренировке...'}),
            'mood': forms.Select(attrs={'class': 'form-select'})
        }

    def clean_duration(self):
        duration_str = self.cleaned_data.get('duration')
        if not duration_str:
            return None
        try:
            parts = duration_str.split(':')
            if len(parts) == 2:
                minutes, seconds = map(int, parts)
                duration = timedelta(minutes=minutes, seconds=seconds)
            elif len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            else:
                raise ValueError
            return duration
        except ValueError:
            raise forms.ValidationError('Введите продолжительность в формате ЧЧ:ММ:СС или ММ:СС')


class WorkoutExerciseForm(forms.ModelForm):
    class Meta:
        model = WorkoutExercise
        fields = ['exercise']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(WorkoutExerciseForm, self).__init__(*args, **kwargs)
        self.fields['exercise'].queryset = Exercise.objects.filter(user=user)


class SetForm(forms.ModelForm):
    rest_time = forms.DurationField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'ММ:СС'}),
        help_text='Формат: минуты:секунды (например, 01:30 для 1.5 минут)'
    )

    class Meta:
        model = Set
        fields = ['repetitions', 'weight', 'rest_time']
        widgets = {
            'repetitions': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        weight = cleaned_data.get('weight')
        repetitions = cleaned_data.get('repetitions')

        if weight is not None and weight <= 0:
            self.add_error('weight', 'Вес должен быть положительным числом.')
        if repetitions is not None and repetitions <= 0:
            self.add_error('repetitions', 'Количество повторений должно быть положительным числом.')

    def clean_rest_time(self):
        rest_time = self.cleaned_data.get('rest_time')
        if rest_time and isinstance(rest_time, str):
            try:
                minutes, seconds = map(int, rest_time.split(':'))
                from datetime import timedelta
                rest_time = timedelta(minutes=minutes, seconds=seconds)
            except ValueError:
                raise forms.ValidationError('Введите время в формате ММ:СС')
        return rest_time
