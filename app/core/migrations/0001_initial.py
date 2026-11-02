import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Host",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=32, unique=True, verbose_name="Nome")),
                ("ip", models.GenericIPAddressField(verbose_name="Endereço IP")),
                ("zone", models.CharField(choices=[("WAN", "WAN"), ("LAN", "LAN"), ("DMZ", "DMZ")], max_length=3, verbose_name="Zona")),
                ("role", models.CharField(max_length=128, verbose_name="Função")),
            ],
            options={
                "verbose_name": "Host",
                "verbose_name_plural": "Hosts",
                "ordering": ["zone", "name"],
            },
        ),
        migrations.CreateModel(
            name="Event",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True, verbose_name="Criado em")),
                ("severity", models.CharField(choices=[("info", "Informativo"), ("warning", "Alerta"), ("critical", "Crítico")], default="info", max_length=10, verbose_name="Severidade")),
                ("message", models.CharField(max_length=255, verbose_name="Mensagem")),
                ("host", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="events", to="core.host", verbose_name="Host")),
            ],
            options={
                "verbose_name": "Evento",
                "verbose_name_plural": "Eventos",
                "ordering": ["-created", "-id"],
            },
        ),
    ]
