"""
Popula o banco com dados de exemplo do laboratório.

Isto roda automaticamente no primeiro `python manage.py migrate`, atendendo
ao requisito de que o primeiro setup do Django já preencha o DB.
"""
from django.db import migrations


HOSTS = [
    # name,   ip,              zone,  role
    ("EXT01", "203.0.113.10", "WAN", "Cliente externo e testes"),
    ("FW01", "203.0.113.1", "WAN", "Firewall IPTables, NAT e Squid"),
    ("APP01", "10.10.10.10", "LAN", "Aplicação HTTP (Django) e SSH"),
    ("DB01", "10.10.10.20", "LAN", "PostgreSQL e DNS"),
    ("WEB01", "172.16.20.10", "DMZ", "Web pública (Django/Nginx) e SSH"),
]

EVENTS = [
    # host_name, severity,   message
    ("FW01", "info", "IP forwarding habilitado entre WAN, LAN e DMZ."),
    ("FW01", "warning", "Tentativa de acesso WAN -> LAN bloqueada pela política."),
    ("WEB01", "info", "Publicação HTTP via DNAT (FW01:8080 -> WEB01:80)."),
    ("WEB01", "info", "Conexão TCP/5432 estabelecida com DB01."),
    ("APP01", "info", "Aplicação conectada ao PostgreSQL em DB01."),
    ("APP01", "warning", "Saída HTTP direta para a WAN negada; use o Squid."),
    ("DB01", "info", "PostgreSQL aceitando conexões da LAN e da DMZ."),
    ("DB01", "critical", "Varredura de portas detectada na porta 5432."),
    ("EXT01", "info", "curl http://203.0.113.1:8080/ respondeu 200 OK."),
]


def seed(apps, schema_editor):
    Host = apps.get_model("core", "Host")
    Event = apps.get_model("core", "Event")

    hosts = {}
    for name, ip, zone, role in HOSTS:
        host, _ = Host.objects.get_or_create(
            name=name, defaults={"ip": ip, "zone": zone, "role": role}
        )
        hosts[name] = host

    for host_name, severity, message in EVENTS:
        Event.objects.get_or_create(
            host=hosts[host_name], severity=severity, message=message
        )


def unseed(apps, schema_editor):
    Host = apps.get_model("core", "Host")
    Event = apps.get_model("core", "Event")
    Event.objects.all().delete()
    Host.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
