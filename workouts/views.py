from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, F
from .models import Workout, SetEntry, Exercise
from django.shortcuts import get_object_or_404


class WorkoutListView(ListView):
    model = Workout
    template_name = 'workouts/workout_list.html'

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)



class WorkoutDetailView(LoginRequiredMixin, DetailView):
    model = Workout
    template_name = 'workouts/workout_detail.html'

    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workout = self.object

        sets_qs = workout.sets.select_related('exercise')

        context['unique_exercises'] = (
            sets_qs.values('exercise_id').distinct().count()
        )
        context['total_sets'] = sets_qs.count()
        context["total_volume"] = round(sum(s.weight * s.reps for s in sets_qs), 2)
        return context
    


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
    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)


class WorkoutDeleteView(DeleteView):
    model = Workout
    template_name = 'workouts/workout_confirm_delete.html'
    success_url = reverse_lazy('workout_list')
    def get_queryset(self):
        return Workout.objects.filter(user=self.request.user)

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


class SetEntryDeleteView(LoginRequiredMixin, DeleteView):
    model = SetEntry
    template_name = "workouts/set_confirm_delete.html"

    def get_queryset(self):
        return SetEntry.objects.filter(workout__user=self.request.user)

    def get_success_url(self):
        return reverse("workout_detail", kwargs={"pk": self.object.workout_id})

    
class SetEntryUpdateView(LoginRequiredMixin, UpdateView):
    model = SetEntry
    fields = ["exercise", "weight", "reps", "notes"]
    template_name = "workouts/set_form.html"

    def get_queryset(self):
        return SetEntry.objects.filter(workout__user=self.request.user)

    def get_success_url(self):
        return reverse("workout_detail", kwargs={"pk": self.object.workout_id})

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["workout"] = self.object.workout
        return ctx

class ExerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = 'workouts/exercise_list.html'
    def get_queryset(self):
        return Exercise.objects.filter(user=self.request.user).order_by("muscle_group", "name")

class ExerciseCreateView(LoginRequiredMixin, CreateView):
    model = Exercise
    fields = ['name', 'muscle_group']
    template_name = 'workouts/exercise_form.html'
    success_url = reverse_lazy('exercise_list')
    def dispatch(self, request, *args, **kwargs):
        self.workout = get_object_or_404(Workout, pk=kwargs["workout_id"], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.workout = self.workout
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["workout"] = self.workout
        return ctx