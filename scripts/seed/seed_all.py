"""Seed the DB with fake data for development and testing.
Run with: python manage.py runscript scripts.seed.seed_all (requires django-extensions or use manage.py shell -c)
This script creates:
- Users (admin/dispatchers/drivers)
- Carriers, Brokers, Drivers, Trucks
- Loads and Payments
- Education: Topics, Questions, ExamTemplates, ExamAttempts
- Communications, Messages, Events

It's idempotent-ish: checks for existing demo markers.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker
import random
import uuid

fake = Faker('es_ES')
User = get_user_model()

# Helpers
def get_or_create_user(username, email, password, role='driver'):
    u = User.objects.filter(username=username).first()
    if u:
        return u
    return User.objects.create_superuser(username=username, email=email, password=password) if role=='admin' else User.objects.create_user(username=username,email=email,password=password,role=role)

# 1) Users
print('Creating users...')
admin = get_or_create_user('admin','admin@example.com','admin',role='admin')
dispatcher = get_or_create_user('dispatch1','dispatch1@example.com','dispatch1',role='dispatcher')
for i in range(3):
    get_or_create_user(f'driver{i+1}','driver{i+1}@example.com','driver',role='driver')

# 2) Carriers
from apps.carriers.models import Carrier
carriers = []
for i in range(5):
    c, _ = Carrier.objects.get_or_create(dot_number=f'DOT-{1000+i}', defaults={'name': fake.company(), 'mc_number': f'MC-{2000+i}', 'address': fake.address(), 'phone': fake.phone_number(), 'email': fake.company_email()})
    carriers.append(c)

# 3) Brokers
from apps.brokers.models import Broker
brokers = []
for i in range(4):
    b, _ = Broker.objects.get_or_create(name=f'Broker {i+1}', defaults={'contact': fake.name(), 'phone': fake.phone_number(), 'email': fake.company_email(), 'is_verified': random.choice([True, False])})
    brokers.append(b)

# 4) Drivers & Trucks
from apps.drivers.models import Driver
from apps.trucks.models import Truck
for c in carriers:
    for j in range(2):
        d, _ = Driver.objects.get_or_create(carrier=c, name=fake.name(), defaults={'license_number': str(100000+j), 'phone': fake.phone_number(), 'email': fake.email()})
        t, _ = Truck.objects.get_or_create(carrier=c, plate_number=f'ABC{random.randint(100,999)}', defaults={'vin': str(uuid.uuid4()), 'model': fake.word().title(), 'year': random.randint(2008,2024)})

# 5) Loads
from apps.loads.models import Load
loads = []
for i in range(30):
    broker = random.choice(brokers)
    carrier = random.choice(carriers) if random.random() < 0.8 else None
    origin = fake.city()
    destination = fake.city()
    pickup = timezone.now().date() + timezone.timedelta(days=random.randint(1,30))
    delivery = pickup + timezone.timedelta(days=random.randint(1,5))
    status = random.choice(['pending','assigned','delivered','cancelled'])
    rate = round(random.uniform(500,5000),2)
    l = Load.objects.create(broker=broker, carrier=carrier, origin=origin, destination=destination, pickup_date=pickup, delivery_date=delivery, status=status, rate=rate)
    loads.append(l)

# 6) Payments
from apps.payments.models import Payment
for l in loads:
    if random.random() < 0.7:
        Payment.objects.create(load=l, invoice_number=f'INV-{l.id}-{random.randint(1000,9999)}', amount=l.rate * random.uniform(0.9,1.1), status=random.choice(['pending','paid','rejected']))

# 7) Education
from apps.education.models import Topic, Question, ExamTemplate, ExamAttempt
print('Seeding education...')
# Topics
topics = []
for name in ['Reglas de tránsito','Señales','Mantenimiento','Carga y seguridad']:
    t, _ = Topic.objects.get_or_create(name=name, defaults={'slug': name.lower().replace(' ','-')})
    topics.append(t)

# Questions (at least 20)
for t in topics:
    for i in range(6):
        qtype = random.choice(['TF','SC'])
        if qtype == 'TF':
            Question.objects.create(topic=t, type=qtype, text=fake.sentence(), difficulty=random.choice(['easy','medium','hard']), correct_answer=random.choice(['true','false']))
        else:
            options = []
            keys = ['A','B','C','D']
            correct = random.choice(keys[:3])
            for k in keys[:4]:
                options.append({'key':k,'text':fake.sentence(nb_words=5)})
            Question.objects.create(topic=t, type=qtype, text=fake.sentence(), difficulty=random.choice(['easy','medium','hard']), choices=options, correct_answer=correct)

# Exam templates (3)
for i in range(3):
    et, _ = ExamTemplate.objects.get_or_create(name=f'Examen Demo {i+1}', defaults={'topic': random.choice(topics), 'num_questions': 20, 'difficulty_mix': {'easy':40,'medium':40,'hard':20}})

# Exam attempts (for demo users)
users = list(User.objects.exclude(is_staff=True)[:5])
templates = list(ExamTemplate.objects.all())
for u in users:
    for i in range(3):
        tpl = random.choice(templates)
        items = []
        all_questions = list(tpl.topic.questions.all() if tpl.topic else Question.objects.all())
        chosen = random.sample(all_questions, min(20, len(all_questions)))
        correct_count = 0
        for q in chosen:
            if q.type == 'TF':
                selected = random.choice(['true','false'])
            else:
                selected = random.choice([o['key'] for o in q.choices])
            correct = (str(selected).lower() == str(q.correct_answer).lower())
            items.append({'question_id': q.id, 'type': q.type, 'selected': selected, 'correct': correct, 'correct_answer': q.correct_answer})
            if correct:
                correct_count += 1
        pct = (correct_count / max(1, len(chosen))) * 100
        ExamAttempt.objects.create(user=u, exam_template=tpl, finished_at=timezone.now(), score_pct=round(pct,2), passed=(pct>=70), items=items, credits_spent=random.randint(0,5), status='SUBMITTED')

# 8) Communications
from apps.comms.models import Communication, CommsMessage, CommsEvent
from apps.education.models import ConversationalExamSession
print('Seeding communications...')
for i in range(25):
    u = random.choice([admin, dispatcher] + list(User.objects.filter(role='driver')[:10]))
    comm = Communication.objects.create(
        user=u,
        comm_type=random.choice(['call', 'chat']),
        external_id=f'ext-{i}',
        channel=random.choice(['web', 'phone', 'whatsapp', 'chat']),
        conversation_id=f'conv-{i}',
        agent_id=f'agent-{random.randint(1,5)}',
        language='es',
        started_at=timezone.now() - timezone.timedelta(minutes=random.randint(1, 500)),
        ended_at=timezone.now(),
        duration_seconds=random.randint(30, 3600),
        summary=fake.sentence(nb_words=8),
        tokens=random.randint(0, 2000),
        tokens_input=random.randint(0, 1000),
        tokens_output=random.randint(0, 1000),
        tokens_total=random.randint(0, 2000),
        source='retell',
        metadata={'seeded': True},
    )
    # messages
    for m in range(random.randint(2, 8)):
        CommsMessage.objects.create(
            communication=comm,
            message_id=str(uuid.uuid4()),
            role=random.choice(['user', 'assistant']),
            text=fake.sentence(nb_words=12),
            timestamp=timezone.now() - timezone.timedelta(minutes=random.randint(0, 500)),
        )
    # events
    CommsEvent.objects.create(communication=comm, event_type='seeded_event', payload={'note': 'seed'}, idempotency_key=str(uuid.uuid4()))

# Also create a few ConversationalExamSession entries (separate model)
for i in range(12):
    u = random.choice([admin, dispatcher] + list(User.objects.filter(role='driver')[:10]))
    ConversationalExamSession.objects.create(
        user=u,
        profile=None,
        retell_session_id=str(uuid.uuid4()),
        agent_id=f'agent-{random.randint(1,5)}',
        channel=random.choice(['voice', 'web', 'phone', 'whatsapp']),
        started_at=timezone.now() - timezone.timedelta(minutes=random.randint(10, 5000)),
        ended_at=timezone.now(),
        duration_seconds=random.randint(30, 3600),
        exam_type=random.choice(['practice', 'full']),
        score_total=round(random.uniform(0, 100), 2),
        score_scale=random.choice(['percentage', 'points']),
        strengths=[fake.word() for _ in range(2)],
        weaknesses=[fake.word() for _ in range(2)],
        section_breakdown=[{'section': fake.word(), 'score': random.randint(0, 100)}],
        transcript_url='',
        recording_url='',
        raw_payload={},
        communication_thread_id=f'thread-exam-{i}',
    )

print('Seeding completed.')
