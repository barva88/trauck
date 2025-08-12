from django.shortcuts import render, get_object_or_404
from .models import Load
from config.menu_config import MENU_ITEMS

def index(request):
    loads = Load.objects.select_related('broker', 'carrier').all().order_by('-pickup_date')
    context = {
        'loads': loads,
        'menu_items': MENU_ITEMS,
        'segment': 'loads',
    }
    return render(request, 'loads/list.html', context)

def detail(request, pk):
    load = get_object_or_404(Load, pk=pk)
    context = {
        'load': load,
        'menu_items': MENU_ITEMS,
        'segment': 'loads',
    }
    return render(request, 'loads/detail.html', context)