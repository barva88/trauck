import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.loads.models import Load
from apps.brokers.models import Broker
from apps.carriers.models import Carrier
from django.contrib.auth import get_user_model
from datetime import date, timedelta
import random

User = get_user_model()
user = User.objects.get(username='barbaro')
brokers = list(Broker.objects.all())
carriers = list(Carrier.objects.all())
origins = ["Miami", "Houston", "Chicago", "Los Angeles", "Atlanta", "Dallas", "Denver", "Seattle", "Phoenix", "New York"]
destinations = ["Orlando", "San Antonio", "Detroit", "San Francisco", "Charlotte", "Austin", "Salt Lake City", "Portland", "Las Vegas", "Boston"]

if brokers and carriers:
    for i in range(1, 51):
        broker = random.choice(brokers)
        carrier = random.choice(carriers)
        origin = random.choice(origins)
        destination = random.choice([d for d in destinations if d != origin])
        Load.objects.create(
            origin=origin,
            destination=destination,
            pickup_date=date.today() + timedelta(days=i),
            delivery_date=date.today() + timedelta(days=i+2),
            status=random.choice(['pending', 'assigned', 'delivered', 'cancelled']),
            carrier=carrier,
            broker=broker,
            rate=1000 + i * 50,
        )
    print("¡50 loads creados para el usuario barbaro!")
else:
    print("Debes crear brokers y carriers antes de crear loads.")