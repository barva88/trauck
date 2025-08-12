from django.shortcuts import render
from .models import Broker
from config.menu_config import MENU_ITEMS

def list_brokers(request):
    show_verified = request.GET.get('verified')
    brokers = Broker.objects.all().order_by('name')
    if show_verified == '1':
        brokers = brokers.filter(is_verified=True)
    elif show_verified == '0':
        brokers = brokers.filter(is_verified=False)
    context = {
        'brokers': brokers,
        'menu_items': MENU_ITEMS,
        'segment': 'brokers',
        'show_verified': show_verified,
    }
    return render(request, 'brokers/list.html', context)