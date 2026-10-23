import secrets
import string

from django.db import models
from django.utils import timezone

ALPHABET = string.ascii_letters + string.digits


def generate_code():
    while True:
        code = "".join(secrets.choice(ALPHABET) for _ in range(6))
        if not Link.objects.filter(code=code).exists():
            return code


class Link(models.Model):
    code = models.CharField(max_length=32, unique=True, default=generate_code)
    url = models.URLField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    clicks = models.PositiveIntegerField(default=0)
    last_clicked = models.DateTimeField(null=True, blank=True)

    def is_expired(self):
        return self.expires_at is not None and self.expires_at < timezone.now()

    def __str__(self):
        return f"{self.code} -> {self.url}"