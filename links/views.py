from django.db import IntegrityError
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .forms import EXPIRY_DELTAS, ShortenForm
from .models import Link


def home(request):
    form = ShortenForm(request.POST or None)
    short_url = None
    new_code = None

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        link = Link(url=data["url"])
        if data["alias"]:
            link.code = data["alias"]
        delta = EXPIRY_DELTAS.get(data["expires"])
        if delta:
            link.expires_at = timezone.now() + delta
        try:
            link.save()
        except IntegrityError:
            form.add_error("alias", "That alias is already taken.")
        else:
            short_url = request.build_absolute_uri(f"/{link.code}")
            new_code = link.code
            form = ShortenForm()

    recent = Link.objects.order_by("-created_at")[:10]
    return render(
        request,
        "links/home.html",
        {"form": form, "short_url": short_url, "new_code": new_code, "recent": recent},
    )


def redirect_link(request, code):
    link = get_object_or_404(Link, code=code)
    if link.is_expired():
        return HttpResponse("This link has expired.", status=410)
    Link.objects.filter(pk=link.pk).update(
        clicks=F("clicks") + 1,
        last_clicked=timezone.now(),
    )
    return HttpResponseRedirect(link.url)


def stats(request, code):
    link = get_object_or_404(Link, code=code)
    return render(
        request,
        "links/stats.html",
        {
            "link": link,
            "short_url": request.build_absolute_uri(f"/{link.code}"),
            "expired": link.is_expired(),
        },
    )