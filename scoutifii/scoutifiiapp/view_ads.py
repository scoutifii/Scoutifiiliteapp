from __future__ import annotations

from django.http import JsonResponse, HttpResponseNoContent
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_GET
from django.db import transaction
from django.utils.html import escape

from .ad_selector import select_creative
from .models import AdImpression, AdClick

def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

@require_GET
def ad_slot(request, placement_code: str):
    user = request.user if request.user.is_authenticated else None
    ip = _client_ip(request)

    selection = select_creative(placement_code, user=user, ip=ip)
    if not selection:
        return HttpResponseNoContent()

    placement, campaign, creative = selection

    with transaction.atomic():
        impression = AdImpression.objects.create(
            campaign=campaign,
            creative=creative,
            placement=placement,
            user=user,
            ip=ip,
            user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:500],
        )

    if creative.html:
        html = creative.html  # sanitize if creatives are user-provided
    else:
        headline = escape(creative.headline or "")
        img_src = creative.image.url if getattr(creative, "image", None) else ""
        html = (
            f'<a href="/ads/click/{impression.id}/" target="_blank" rel="noopener nofollow">'
            f'  <img src="{img_src}" alt="{headline}" style="max-width:100%;height:auto;" />'
            f'</a>'
        )

    return JsonResponse({"impression_id": impression.id, "html": html})


@require_GET
def ad_click(request, impression_id: int):
    impression = get_object_or_404(AdImpression, id=impression_id)
    AdClick.objects.create(impression=impression)
    return redirect(impression.creative.click_url)
