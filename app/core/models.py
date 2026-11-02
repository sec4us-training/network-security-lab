from django.db import models


class Host(models.Model):
    """Inventário dos hosts do laboratório."""

    ZONE_CHOICES = [
        ("WAN", "WAN"),
        ("LAN", "LAN"),
        ("DMZ", "DMZ"),
    ]

    name = models.CharField("Nome", max_length=32, unique=True)
    ip = models.GenericIPAddressField("Endereço IP")
    zone = models.CharField("Zona", max_length=3, choices=ZONE_CHOICES)
    role = models.CharField("Função", max_length=128)

    class Meta:
        verbose_name = "Host"
        verbose_name_plural = "Hosts"
        ordering = ["zone", "name"]

    def __str__(self):
        return f"{self.name} ({self.ip})"


class Event(models.Model):
    """Eventos de exemplo, usados para demonstrar leitura do banco."""

    SEVERITY_CHOICES = [
        ("info", "Informativo"),
        ("warning", "Alerta"),
        ("critical", "Crítico"),
    ]

    created = models.DateTimeField("Criado em", auto_now_add=True)
    host = models.ForeignKey(
        Host,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Host",
    )
    severity = models.CharField(
        "Severidade", max_length=10, choices=SEVERITY_CHOICES, default="info"
    )
    message = models.CharField("Mensagem", max_length=255)

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-created", "-id"]

    def __str__(self):
        return f"[{self.severity}] {self.message}"
