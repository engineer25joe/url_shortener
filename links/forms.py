from datetime import timedelta

from django import forms
from django.core.validators import RegexValidator

from .models import Link

#This is to avoid using of the terms that may lead to system pages instead of the destination link

RESERVED = {"admin", "api", "stats", "shorten", "static", "favicon.ico"}

EXPIRY_CHOICES = [
    ("", "Never"),
    ("1h", "1 hour"),
    ("2h", "2 hours"),
    ("1d", "1 day"),
    ("7d", "7 days"),
    ("30d", "30 days"),
]

EXPIRY_DELTAS = {
    "1h": timedelta(hours=1),
    "2h": timedelta(hours=2),
    "1d": timedelta(days=1),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


class ShortenForm(forms.Form):
    url = forms.URLField(
        max_length=2048,
        assume_scheme="https",
        widget=forms.URLInput(attrs={"placeholder": "https://example.com/long/link"}),
    )
    alias = forms.CharField(
        required=False,
        min_length=3,
        max_length=32,
        validators=[
            RegexValidator(
                r"^[A-Za-z0-9_-]+$",
                "Use only letters, numbers, - or _.",
            )
        ],
        widget=forms.TextInput(attrs={"placeholder": "Custom alias (optional)"}),
    )
    expires = forms.ChoiceField(choices=EXPIRY_CHOICES, required=False)

    def clean_url(self):
        url = self.cleaned_data["url"]
        if not url.lower().startswith(("http://", "https://")):
            raise forms.ValidationError("Only http and https links are allowed.")
        return url

    def clean_alias(self):
        alias = self.cleaned_data["alias"]
        if not alias:
            return alias
        if alias.lower() in RESERVED:
            raise forms.ValidationError("That alias is reserved. Pick another.")
        if Link.objects.filter(code=alias).exists():
            raise forms.ValidationError("That alias is already taken.")
        return alias