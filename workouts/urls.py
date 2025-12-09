from django.urls import path
from . import views

urlpatterns = [
    path('', views.WorkoutListView.as_view(), name='workout_list'),
    path('workout/<int:pk>/', views.WorkoutDetailView.as_view(), name='workout_detail'),
    path('workout/add/', views.WorkoutCreateView.as_view(), name='workout_add'),
    path('workout/<int:pk>/edit/', views.WorkoutUpdateView.as_view(), name='workout_edit'),
    path('workout/<int:pk>/delete/', views.WorkoutDeleteView.as_view(), name='workout_delete'),

    path('workout/<int:workout_id>/set/add/', views.SetEntryCreateView.as_view(), name='set_add'),
    path('set/<int:pk>/delete/', views.SetEntryDeleteView.as_view(), name='set_delete'),
]
