from django.core.management.base import BaseCommand
from apps.education.models import Topic, Question, ExamTemplate

class Command(BaseCommand):
    help = "Seed demo topics, questions and exam templates"

    def handle(self, *args, **options):
        topic, _ = Topic.objects.get_or_create(name="General")

        # Create 25 TF questions
        for i in range(1, 26):
            Question.objects.get_or_create(
                topic=topic,
                type=Question.TYPE_TF,
                text=f"La afirmación #{i} es verdadera?",
                defaults={
                    'difficulty': Question.DIFF_MEDIUM,
                    'correct_answer': 'true' if i % 2 == 0 else 'false',
                }
            )
        # Create 25 SC questions
        for i in range(1, 26):
            Question.objects.get_or_create(
                topic=topic,
                type=Question.TYPE_SC,
                text=f"¿Cuál es la opción correcta #{i}?",
                defaults={
                    'difficulty': Question.DIFF_MEDIUM,
                    'choices': [
                        {'key': 'A', 'text': 'Opción A'},
                        {'key': 'B', 'text': 'Opción B'},
                        {'key': 'C', 'text': 'Opción C'},
                    ],
                    'correct_answer': 'B',
                }
            )

        ExamTemplate.objects.get_or_create(
            name="Examen General 20",
            topic=topic,
            defaults={
                'num_questions': 20,
                'difficulty_mix': {'easy': 30, 'medium': 50, 'hard': 20},
                'is_active': True,
            }
        )

        self.stdout.write(self.style.SUCCESS("Education demo data seeded."))
