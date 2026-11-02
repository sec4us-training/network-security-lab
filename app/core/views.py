import socket

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render

from .models import Event, Host


def index(request):
    hosts = list(Host.objects.all())
    events = list(Event.objects.select_related("host")[:15])
    context = {
        "app_role": settings.APP_ROLE,
        "hostname": socket.gethostname(),
        "db_host": settings.DATABASES["default"]["HOST"],
        "db_name": settings.DATABASES["default"]["NAME"],
        "hosts": hosts,
        "events": events,
        "host_count": len(hosts),
        "event_count": Event.objects.count(),
    }
    return render(request, "core/index.html", context)


def healthz(request):
    """Verificação simples de saúde incluindo conectividade com o banco."""
    db_ok = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:  # noqa: BLE001 - lab: reportar qualquer falha de DB
        db_ok = False
    return JsonResponse(
        {
            "status": "ok" if db_ok else "degraded",
            "role": settings.APP_ROLE,
            "database": "up" if db_ok else "down",
        }
    )
