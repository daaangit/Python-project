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
from datetime import date, timedelta
from django.utils import timezone
from django.contrib import messages
from django.db.models.deletion import ProtectedError
import json
from django.utils import timezone


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
        user = self.request.user

        sets_qs = (
            SetEntry.objects
            .filter(workout__user=user)
            .select_related("workout", "exercise")
        )

        by_day_map = OrderedDict()

        for s in sets_qs:
            d = s.workout.date
            vol = float(s.weight) * int(s.reps)

            if d not in by_day_map:
                by_day_map[d] = {
                    "day": d,
                    "total_sets": 0,
                    "total_volume": 0.0,
                }

            by_day_map[d]["total_sets"] += 1
            by_day_map[d]["total_volume"] += vol

        by_day = []
        for d, v in by_day_map.items():
            by_day.append({
                "day": d,
                "total_sets": v["total_sets"],
                "total_volume_tons": round(v["total_volume"] / 1000, 2),
                "avg_volume": round(v["total_volume"] / max(v["total_sets"], 1), 1),
            })

        ctx["by_day"] = by_day
        ctx["by_day_json"] = json.dumps(
            [{"day": x["day"].isoformat(), "total_volume_tons": x["total_volume_tons"]} for x in by_day]
        )

        volume_expr = ExpressionWrapper(
            Cast(F("weight"), FloatField()) * Cast(F("reps"), FloatField()),
            output_field=FloatField()
        )

        ctx["by_exercise"] = (
            sets_qs
            .values("exercise__name", "exercise__muscle_group")
            .annotate(
                total_sets=Count("id"),
                max_weight=Max("weight"),
            )
            .order_by("exercise__muscle_group", "exercise__name")
        )

        exercises = Exercise.objects.filter(user=user, is_active=True).order_by("muscle_group", "name")
        ctx["exercises"] = exercises

        selected_ex_id = self.request.GET.get("exercise")
        if not selected_ex_id and exercises.exists():
            selected_ex_id = str(exercises.first().id)

        ctx["selected_exercise_id"] = selected_ex_id

        chart_points = []

        if selected_ex_id:
            series = (
                sets_qs
                .filter(exercise_id=int(selected_ex_id))
                .values("workout__date")
                .annotate(max_weight=Max("weight"))
                .order_by("workout__date")
            )

            chart_points = [
                {"day": r["workout__date"].isoformat(), "max_weight": float(r["max_weight"])}
                for r in series
            ]

        ctx["exercise_series"] = chart_points
        ctx["exercise_series_json"] = json.dumps(chart_points)
        total_workout_days = len(by_day)
        total_sets_all = sum(x["total_sets"] for x in by_day)
        total_volume_tons_all = sum(x["total_volume_tons"] for x in by_day)

        avg_volume_per_workout = (total_volume_tons_all / total_workout_days) if total_workout_days else 0.0

        ctx["total_workout_days"] = total_workout_days
        ctx["total_sets_all"] = total_sets_all
        ctx["avg_volume_per_workout"] = round(avg_volume_per_workout, 2)
        ctx["total_volume_tons_all"] = round(total_volume_tons_all, 2)

        return ctx

def home_view(request):
    return render(request, 'workouts/home.html')