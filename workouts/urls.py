from django.urls import path
from .views import (
    WorkoutListView,
    WorkoutDetailView,
    WorkoutCreateView,
    WorkoutUpdateView,
    WorkoutDeleteView,
    SetEntryCreateView,
    SetEntryDeleteView,
    SetEntryUpdateView,
    ExerciseListView,
    ExerciseCreateView,
    ExerciseDeleteView,
    ExerciseArchiveView,
    ExerciseUnarchiveView,
    ProgressView,   
)

urlpatterns = [
    path('', WorkoutListView.as_view(), name='workout_list'),
    path('workout/<int:pk>/', WorkoutDetailView.as_view(), name='workout_detail'),
    path('workout/add/', WorkoutCreateView.as_view(), name='workout_add'),
    path('workout/<int:pk>/edit/', WorkoutUpdateView.as_view(), name='workout_edit'),
    path('workout/<int:pk>/delete/', WorkoutDeleteView.as_view(), name='workout_delete'),

    path('workout/<int:workout_id>/set/add/', SetEntryCreateView.as_view(), name='set_add'),
    path('set/<int:pk>/delete/', SetEntryDeleteView.as_view(), name='set_delete'),

    path('exercises/', ExerciseListView.as_view(), name='exercise_list'),
    path('exercises/add/', ExerciseCreateView.as_view(), name='exercise_add'),
    path("set/<int:pk>/edit/", SetEntryUpdateView.as_view(), name="set_edit"),
    path("progress/", ProgressView.as_view(), name="progress"),
    path("exercises/<int:pk>/delete/", ExerciseDeleteView.as_view(),name="exercise_delete"),
    path("exercises/<int:pk>/archive/", ExerciseArchiveView.as_view(), name="exercise_archive"),
    path("exercises/<int:pk>/delete/", ExerciseDeleteView.as_view(), name="exercise_delete"),
    path("exercises/<int:pk>/unarchive/", ExerciseUnarchiveView.as_view(), name="exercise_unarchive"),


]
