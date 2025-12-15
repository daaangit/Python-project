from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from workouts.models import Workout, Exercise, SetEntry

class Command(BaseCommand):
    help = "Create demo user and seed workouts/exercises/sets"

    def add_arguments(self, parser):
        parser.add_argument("--email", default="demo@example.com")
        parser.add_argument("--username", default="demo")
        parser.add_argument("--password", default="demo12345")

    def handle(self, *args, **opts):
        User = get_user_model()
        email = opts["email"]
        username = opts["username"]
        password = opts["password"]

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Created user: {username}/{password}"))
        else:
            self.stdout.write(self.style.WARNING(f"User already exists: {username}"))

        exercises_data = [
            ("Bench Press", "Chest", True),
            ("Incline Dumbbell Press", "Chest", True),
            ("Deadlift", "Back", True),
            ("Lat Pulldown", "Back", True),
            ("Squat", "Legs", True),
            ("Lateral Raises", "Shoulders", True),
            ("Old Exercise (archived)", "Other", False),
        ]

        ex_map = {}
        for name, mg, active in exercises_data:
            ex, _ = Exercise.objects.get_or_create(
                user=user,
                name=name,
                defaults={"muscle_group": mg, "is_active": active},
            )
            ex.muscle_group = mg
            ex.is_active = active
            ex.save(update_fields=["muscle_group", "is_active"])
            ex_map[name] = ex

        today = timezone.now().date()
        w1, _ = Workout.objects.get_or_create(user=user, date=today, defaults={"day_type": "Chest_Triceps", "notes": "Demo chest day"})
        w2, _ = Workout.objects.get_or_create(user=user, date=today.replace(day=max(1, today.day-2)), defaults={"day_type": "Back_Biceps", "notes": "Demo back day"})
        w3, _ = Workout.objects.get_or_create(user=user, date=today.replace(day=max(1, today.day-4)), defaults={"day_type": "Legs", "notes": "Demo legs day"})

        demo_sets = [
            (w1, "Bench Press", 80.0, 10, ""),
            (w1, "Bench Press", 80.0, 8, ""),
            (w1, "Incline Dumbbell Press", 30.0, 12, ""),
            (w1, "Lateral Raises", 9.0, 15, ""),

            (w2, "Deadlift", 140.0, 5, ""),
            (w2, "Deadlift", 150.0, 3, ""),
            (w2, "Lat Pulldown", 75.0, 10, ""),

            (w3, "Squat", 120.0, 5, ""),
            (w3, "Squat", 110.0, 8, ""),
        ]

        created_sets = 0
        for workout, ex_name, weight, reps, notes in demo_sets:
            ex = ex_map[ex_name]
            obj, was_created = SetEntry.objects.get_or_create(
                workout=workout,
                exercise=ex,
                weight=weight,
                reps=reps,
                defaults={"notes": notes},
            )
            created_sets += 1 if was_created else 0

        self.stdout.write(self.style.SUCCESS(f"Seed done. Exercises: {len(exercises_data)}, new sets: {created_sets}"))
        self.stdout.write(self.style.SUCCESS("Login: demo / demo12345"))
