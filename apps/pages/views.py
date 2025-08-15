# # from django.shortcuts import render
# # from django.http import HttpResponse

# # # Create your views here.

# # def index(request):

# #     # Page from the theme 
# #     return render(request, 'pages/dashboard.html')


# from django.shortcuts import render
# from config.menu_config import MENU_ITEMS

# def index(request):
#     context = {
#         "menu_items": MENU_ITEMS,
#         "segment": "dashboard",
#     }
#     return render(request, "pages/dashboard.html", context)



from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_control
from django.db import connection
from config.menu_config import MENU_ITEMS
from datetime import date

def index(request):
    # KPIs simulados
    kpis = [
        {"label": "Cargas asignadas hoy", "value": 12, "icon": "tim-icons icon-delivery-fast text-info"},
        {"label": "Viajes en curso", "value": 7, "icon": "tim-icons icon-bus-front-12 text-primary"},
        {"label": "Viajes completados este mes", "value": 48, "icon": "tim-icons icon-check-2 text-success"},
        {"label": "Total facturado este mes", "value": "$23,500", "icon": "tim-icons icon-credit-card text-warning"},
        {"label": "Cargas pendientes", "value": 5, "icon": "tim-icons icon-time-alarm text-danger"},
        {"label": "Documentos subidos hoy", "value": 3, "icon": "tim-icons icon-paper text-purple"},
    ]

    # Datos para gráficas
    loads_per_month = {
        "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago"],
        "data": [20, 25, 30, 28, 35, 40, 38, 45],
    }
    revenue_per_month = {
        "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago"],
        "data": [5000, 7000, 8000, 7500, 9000, 11000, 10500, 12000],
    }
    top_drivers = [
        {"name": "Juan Pérez", "trips": 22},
        {"name": "Luis Gómez", "trips": 19},
        {"name": "Carlos Ruiz", "trips": 17},
        {"name": "Ana Torres", "trips": 15},
        {"name": "Pedro Díaz", "trips": 13},
    ]

    # Últimas facturas
    invoices = [
        {"number": "F-1001", "client": "TransLog", "amount": "$1,200", "status": "Pagada", "date": "2025-08-01"},
        {"number": "F-1002", "client": "CargoExpress", "amount": "$2,500", "status": "Pendiente", "date": "2025-08-02"},
        {"number": "F-1003", "client": "Logística MX", "amount": "$900", "status": "Vencida", "date": "2025-08-02"},
        {"number": "F-1004", "client": "FastMove", "amount": "$1,800", "status": "Pagada", "date": "2025-08-03"},
        {"number": "F-1005", "client": "CargaYa", "amount": "$2,100", "status": "Pendiente", "date": "2025-08-03"},
    ]

    # Últimos viajes
    trips = [
        {"id": 201, "origin": "Miami", "destination": "Houston", "date": "2025-08-03", "status": "En curso"},
        {"id": 202, "origin": "Dallas", "destination": "Atlanta", "date": "2025-08-02", "status": "Completado"},
        {"id": 203, "origin": "Chicago", "destination": "Denver", "date": "2025-08-02", "status": "Completado"},
        {"id": 204, "origin": "Phoenix", "destination": "Seattle", "date": "2025-08-01", "status": "En curso"},
        {"id": 205, "origin": "Orlando", "destination": "New York", "date": "2025-08-01", "status": "Pendiente"},
    ]

    # Tareas diarias
    tasks = [
        {"id": 1, "text": "Confirmar asignación de cargas", "done": False},
        {"id": 2, "text": "Revisar documentos subidos", "done": True},
        {"id": 3, "text": "Llamar a clientes con facturas vencidas", "done": False},
        {"id": 4, "text": "Actualizar estado de viajes", "done": False},
    ]

    # Notificaciones
    notifications = [
        {"icon": "tim-icons icon-alert-circle-exc text-danger", "text": "3 cargas sin asignar"},
        {"icon": "tim-icons icon-credit-card text-warning", "text": "2 facturas vencidas"},
        {"icon": "tim-icons icon-settings-gear-63 text-info", "text": "Mantenimiento de camión pendiente"},
    ]

    context = {
        "menu_items": MENU_ITEMS,
        "segment": "dashboard",
        "kpis": kpis,
        "loads_per_month": loads_per_month,
        "revenue_per_month": revenue_per_month,
        "top_drivers": top_drivers,
        "invoices": invoices,
        "trips": trips,
        "tasks": tasks,
        "notifications": notifications,
        "today": date.today(),
    }
    return render(request, "pages/dashboard.html", context)


# Lightweight health and readiness probes
@require_GET
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def healthz(request):
    return JsonResponse({"status": "ok"})


@require_GET
@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def readiness(request):
    # Ensure DB connectivity without running queries
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False
    status = 200 if db_ok else 503
    return JsonResponse({"database": db_ok}, status=status)