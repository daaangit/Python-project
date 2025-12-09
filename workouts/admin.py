from django.contrib import admin
from .models import Exercise, Workout, SetEntry


class SetEntryInline(admin.TabularInline):
    model = SetEntry
    extra = 1


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "day_type")
    list_filter = ("user", "day_type", "date")
    inlines = [SetEntryInline]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "muscle_group")
    list_filter = ("muscle_group",)


@admin.register(SetEntry)
class SetEntryAdmin(admin.ModelAdmin):
    list_display = ("workout", "exercise", "weight", "reps")
    list_filter = ("exercise",)
