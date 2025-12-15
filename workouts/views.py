from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, F, Max, FloatField
from django.db.models.functions import Cast
from django.db.models.expressions import ExpressionWrapper
from django.db.models.functions import TruncDate
from .models import Workout, SetEntry, Exercise
from django.shortcuts import get_object_or_404, redirect
from collections import OrderedDict
from datetime import date
from django.contrib import messages
from django.db.models.deletion import ProtectedError


class WorkoutListView(LoginRequiredMixin, ListView):
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

class SetEntryCreateView(LoginRequiredMixin, CreateView):
    model = SetEntry
    fields = ['exercise', 'weight', 'reps', 'notes']
    template_name = 'workouts/set_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.workout = get_object_or_404(
            Workout, pk=kwargs["workout_id"], user=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.workout = self.workout
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["workout"] = self.workout
        return ctx

    def get_success_url(self):
        return reverse_lazy('workout_detail', kwargs={'pk': self.workout.id})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["exercise"].queryset = Exercise.objects.filter(
            user=self.request.user, is_active=True
        ).order_by("muscle_group", "name")
        return form



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
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["exercise"].queryset = Exercise.objects.filter(
            user=self.request.user, is_active=True
        ).order_by("muscle_group", "name")
        return form


class ExerciseListView(LoginRequiredMixin, ListView):
    model = Exercise
    template_name = 'workouts/exercise_list.html'
    def get_queryset(self):
        show_archived = self.request.GET.get("archived") == "1"
        qs = Exercise.objects.filter(user=self.request.user)

        if show_archived:
            qs = qs.filter(is_active=False)
        else:
            qs = qs.filter(is_active=True)

        return qs.annotate(used_count=Count("setentry")).order_by("muscle_group", "name")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["show_archived"] = self.request.GET.get("archived") == "1"
        return ctx


class ExerciseCreateView(LoginRequiredMixin, CreateView):
    model = Exercise
    fields = ['name', 'muscle_group']
    template_name = 'workouts/exercise_form.html'
    success_url = reverse_lazy('exercise_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
class ExerciseDeleteView(LoginRequiredMixin, DeleteView):
    model = Exercise
    template_name = "workouts/exercise_confirm_delete.html"
    success_url = reverse_lazy("exercise_list")

    def get_queryset(self):
        return Exercise.objects.filter(user=self.request.user)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                request,
                "Нельзя удалить упражнение: оно используется в подходах. Можно только архивировать."
            )
            return redirect("exercise_list")
    
class ExerciseArchiveView(LoginRequiredMixin, UpdateView):
    model = Exercise
    fields = []
    template_name = "workouts/exercise_confirm_archive.html"
    success_url = reverse_lazy("exercise_list")

    def get_queryset(self):
        return Exercise.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        ex = self.get_object()
        ex.is_active = False
        ex.save(update_fields=["is_active"])
        messages.success(request, f"Упражнение «{ex.name}» архивировано.")
        return redirect("exercise_list")

class ExerciseUnarchiveView(LoginRequiredMixin, UpdateView):
    model = Exercise
    fields = []
    template_name = "workouts/exercise_confirm_unarchive.html"
    success_url = reverse_lazy("exercise_list")

    def get_queryset(self):
        return Exercise.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        ex = self.get_object()
        ex.is_active = True
        ex.save(update_fields=["is_active"])
        messages.success(request, f"Упражнение «{ex.name}» возвращено из архива.")
        return redirect("exercise_list")
    
class ProgressView(LoginRequiredMixin, TemplateView):
    template_name = "workouts/progress.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        sets_qs = (
            SetEntry.objects
            .filter(workout__user=self.request.user)
            .select_related("workout", "exercise")
            .order_by("workout__date")
        )

        volume_expr = ExpressionWrapper(
            Cast(F("weight"), FloatField()) * Cast(F("reps"), FloatField()),
            output_field=FloatField()
        )

        ctx["by_exercise"] = (
            sets_qs
            .values("exercise_id", "exercise__name", "exercise__muscle_group")
            .annotate(
                total_sets=Count("id"),
                max_weight=Max("weight"),
                total_volume=Sum(volume_expr),
            )
            .order_by("exercise__muscle_group", "exercise__name")
        )
        by_day_map = OrderedDict()
        for s in sets_qs:
            d = s.workout.date
            vol = float(s.weight) * int(s.reps)

            if d not in by_day_map:
                by_day_map[d] = {"day": d, "total_volume": 0.0, "total_sets": 0}
            by_day_map[d]["total_volume"] += vol
            by_day_map[d]["total_sets"] += 1

        ctx["by_day"] = list(by_day_map.values())

        return ctx
