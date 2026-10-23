from django.urls import path

from . import api, views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/shorten", api.api_shorten, name="api_shorten"),
    path("api/links/<str:code>", api.api_stats, name="api_stats"),
    path("stats/<str:code>", views.stats, name="stats"),
    path("<str:code>", views.redirect_link, name="redirect"),
]