from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('muscle_groups/', views.muscle_groups, name='muscle_groups'),
    path('muscle_groups/edit/<int:group_id>/', views.edit_muscle_group, name='edit_muscle_group'),
    path('muscle_groups/delete/<int:group_id>/', views.delete_muscle_group, name='delete_muscle_group'),
    path('exercises/', views.exercises, name='exercises'),
    path('exercises/edit/<int:exercise_id>/', views.edit_exercise, name='edit_exercise'),
    path('exercises/delete/<int:exercise_id>/', views.delete_exercise, name='delete_exercise'),
    path('exercises/reset/', views.reset_exercises, name='reset_exercises'),
    path('start_workout/', views.start_workout, name='start_workout'),
    path('workout_session/<int:workout_id>/', views.workout_session, name='workout_session'),
    path('add_workout_exercise/<int:workout_id>/', views.add_workout_exercise, name='add_workout_exercise'),
    path('add_set_ajax/', views.add_set_ajax, name='add_set_ajax'),
    path('workout_history/', views.workout_history, name='workout_history'),
    path('workout_detail/<int:workout_id>/', views.workout_detail, name='workout_detail'),
    path('progress/', views.progress, name='progress'),
    path('edit_workout/<int:workout_id>/', views.edit_workout, name='edit_workout'),
    path('delete_workout/<int:workout_id>/', views.delete_workout, name='delete_workout'),
    path('calendar/', views.calendar_view, name='calendar_current'),
    path('calendar/<int:year>/<int:month>/', views.calendar_view, name='calendar'),
    path('workout_list/', views.workout_list, name='workout_list'),
]
