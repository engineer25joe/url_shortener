from django.contrib import admin

from .models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ("code", "url", "clicks", "created_at", "expires_at")
    search_fields = ("code", "url")
    readonly_fields = ("clicks", "last_clicked", "created_at")