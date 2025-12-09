from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Workout, SetEntry
from django.shortcuts import get_object_or_404


class WorkoutListView(ListView):
    model = Workout
    template_name = 'workouts/workout_list.html'

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)


class WorkoutDetailView(DetailView):
    model = Workout
    template_name = 'workouts/workout_detail.html'


class WorkoutCreateView(CreateView):
    model = Workout
    fields = ['date', 'day_type', 'notes']
    template_name = 'workouts/workout_form.html'
    success_url = reverse_lazy('workout_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class WorkoutUpdateView(UpdateView):
    model = Workout
    fields = ['date', 'day_type', 'notes']
    template_name = 'workouts/workout_form.html'
    success_url = reverse_lazy('workout_list')


class WorkoutDeleteView(DeleteView):
    model = Workout
    template_name = 'workouts/workout_confirm_delete.html'
    success_url = reverse_lazy('workout_list')

class SetEntryCreateView(CreateView):
    model = SetEntry
    fields = ['exercise', 'weight', 'reps', 'notes']
    template_name = 'workouts/set_form.html'

    def form_valid(self, form):
        workout = get_object_or_404(Workout, id=self.kwargs['workout_id'], user=self.request.user)
        form.instance.workout = workout
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('workout_detail', kwargs={'pk': self.kwargs['workout_id']})


class SetEntryDeleteView(DeleteView):
    model = SetEntry
    template_name = 'workouts/set_confirm_delete.html'

    def get_success_url(self):
        workout_id = self.object.workout.id
        return reverse_lazy('workout_detail', kwargs={'pk': workout_id})
