import hmac
import json
import os

from django.db import IntegrityError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .forms import EXPIRY_DELTAS, ShortenForm
from .models import Link


def api_key_ok(request):
    """If SHORTENER_API_KEY is set, require it in the X-API-Key header.
    If it is not set, the API stays open (handy for local development)."""
    expected = os.environ.get("SHORTENER_API_KEY", "")
    if not expected:
        return True
    given = request.headers.get("X-API-Key", "")
    return hmac.compare_digest(given.encode(), expected.encode())


def link_to_dict(request, link):
    return {
        "code": link.code,
        "short_url": request.build_absolute_uri(f"/{link.code}"),
        "url": link.url,
        "clicks": link.clicks,
        "created_at": link.created_at.isoformat(),
        "expires_at": link.expires_at.isoformat() if link.expires_at else None,
        "last_clicked": link.last_clicked.isoformat() if link.last_clicked else None,
        "expired": link.is_expired(),
    }


@csrf_exempt
@require_POST
def api_shorten(request):
    if not api_key_ok(request):
        return JsonResponse({"error": "Missing or invalid API key."}, status=401)

    try:
        payload = json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"error": "JSON body must be an object."}, status=400)

    form = ShortenForm(
        {
            "url": payload.get("url", ""),
            "alias": payload.get("alias", ""),
            "expires": payload.get("expires", ""),
        }
    )
    if not form.is_valid():
        fields = {name: list(errs) for name, errs in form.errors.items()}
        return JsonResponse({"error": "Validation failed.", "fields": fields}, status=400)

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
        return JsonResponse(
            {
                "error": "Validation failed.",
                "fields": {"alias": ["That alias is already taken."]},
            },
            status=409,
        )
    return JsonResponse(link_to_dict(request, link), status=201)


@require_GET
def api_stats(request, code):
    try:
        link = Link.objects.get(code=code)
    except Link.DoesNotExist:
        return JsonResponse({"error": "Link not found."}, status=404)
    return JsonResponse(link_to_dict(request, link))