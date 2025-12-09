from django.db import models
from django.contrib.auth.models import User


class Exercise(models.Model):
    MUSCLE_GROUP_CHOICES = [
        ("Chest", "Chest"),
        ("Back", "Back"),
        ("Legs", "Legs"),
        ("Shoulders", "Shoulders"),
        ("Arms", "Arms"),
        ("Core", "Core"),
        ("Other", "Other"),
    ]

    name = models.CharField(max_length=100)
    muscle_group = models.CharField(
        max_length=20,
        choices=MUSCLE_GROUP_CHOICES,
        default="Other",
    )

    def __str__(self):
        return f"{self.name} ({self.muscle_group})"


class Workout(models.Model):
    DAY_TYPE_CHOICES = [
        ("Chest_Triceps", "Chest + Triceps"),
        ("Back_Biceps", "Back + Biceps"),
        ("Legs_Shoulders", "Legs + Shoulders"),
        ("FullBody", "Full Body"),
        ("Other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    day_type = models.CharField(
        max_length=30,
        choices=DAY_TYPE_CHOICES,
        default="Other",
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.user.username} – {self.day_type} – {self.date}"


class SetEntry(models.Model):
    workout = models.ForeignKey(
        Workout,
        on_delete=models.CASCADE,
        related_name="sets",
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    weight = models.FloatField()
    reps = models.PositiveIntegerField()
    notes = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.exercise.name}: {self.weight} x {self.reps}"
