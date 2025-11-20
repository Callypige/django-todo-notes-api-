from django.core.management.base import BaseCommand
from django.db import transaction

from apps.notes.models import Note
from apps.todos.models import Todo, TodoStatus


SEED_NOTES = [
    {
        "title": "Idées pour la réunion produit",
        "content": (
            "Préparer une maquette rapide, lister les risques, regrouper les retours "
            "clients avant vendredi."
        ),
        "todos": [
            {
                "title": "Préparer la maquette",
                "description": "Mockups Figma + scénario pour la démo",
                "status": TodoStatus.IN_PROGRESS,
            },
            {
                "title": "Collecter les retours clients",
                "description": "Synthétiser les tickets Jira les plus récents",
                "status": TodoStatus.PENDING,
            },
        ],
    },
    {
        "title": "Lecture technique",
        "content": "Finir le chapitre sur les permissions DRF et noter les questions.",
        "todos": [
            {
                "title": "Lire le chapitre 7",
                "description": "Focus sur les ViewSets et les routes automatiques",
                "status": TodoStatus.PENDING,
            },
            {
                "title": "Rédiger les questions",
                "description": "Comparer approches RBAC vs ABAC",
                "status": TodoStatus.COMPLETED,
            },
        ],
    },
]

SEED_TODOS_WITHOUT_NOTE = [
    {
        "title": "Nettoyer les tâches obsolètes",
        "description": "Faire un tri dans les TODOs terminés il y a plus de 30 jours",
        "status": TodoStatus.PENDING,
    },
    {
        "title": "Mettre à jour la documentation API",
        "description": "Ajouter la nouvelle action /notes/{id}/get_todos/ au README",
        "status": TodoStatus.IN_PROGRESS,
    },
]


class Command(BaseCommand):
    help = "Crée un jeu de données de démonstration pour les notes et todos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Supprime les données existantes avant de regénérer le jeu d'essai.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options["force"]

        if force:
            Todo.objects.all().delete()
            Note.objects.all().delete()
            self.stdout.write(self.style.WARNING("Anciennes données supprimées."))

        created_notes = 0
        created_todos = 0

        for note_data in SEED_NOTES:
            note, created = Note.objects.get_or_create(
                title=note_data["title"],
                defaults={"content": note_data["content"]},
            )
            if created:
                created_notes += 1
            for todo_data in note_data["todos"]:
                todo_defaults = {
                    "description": todo_data["description"],
                    "status": todo_data["status"],
                    "note": note,
                }
                _, todo_created = Todo.objects.get_or_create(
                    title=todo_data["title"],
                    note=note,
                    defaults=todo_defaults,
                )
                if todo_created:
                    created_todos += 1

        for todo_data in SEED_TODOS_WITHOUT_NOTE:
            todo_defaults = {
                "description": todo_data["description"],
                "status": todo_data["status"],
            }
            _, todo_created = Todo.objects.get_or_create(
                title=todo_data["title"],
                note=None,
                defaults=todo_defaults,
            )
            if todo_created:
                created_todos += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Jeu de données prêt ✅  Notes créées: {created_notes}, "
                f"Todos créés: {created_todos}"
            )
        )
