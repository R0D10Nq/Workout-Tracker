from django import forms
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
        fields = ['duration']
        widgets = {
            'duration': forms.HiddenInput(),  # Если поле не должно быть видно
        }


class WorkoutExerciseForm(forms.ModelForm):
    class Meta:
        model = WorkoutExercise
        fields = ['exercise']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(WorkoutExerciseForm, self).__init__(*args, **kwargs)
        self.fields['exercise'].queryset = Exercise.objects.filter(user=user)


class SetForm(forms.ModelForm):
    class Meta:
        model = Set
        fields = ['repetitions', 'weight']
