# scoutifiiapp/ads.py
from django.utils import timezone
from django.core.cache import cache
from typing import Optional
from .models import Campaign

def _campaigns_for_placement(placement_code):
    now = timezone.now()
    return (
        Campaign.objects
        .filter(
            placement__code=placement_code,
            active=True,
            start_at__lte=now,
            end_at__gte=now,
        )
        .select_related('placement', 'advertiser')
        .prefetch_related('creatives')
    )

def _match_targeting(campaign, request, user_profile=None):
    # Simple targeting by country and profile type; extend as needed
    if campaign.target_country:
        country = request.META.get('GEOIP_COUNTRY_CODE') or getattr(user_profile, 'country_id', '')
        if (country or '').upper() != campaign.target_country.upper():
            return False
    if campaign.target_profile_type and user_profile:
        if (user_profile.profile_type_data or '').lower() != campaign.target_profile_type.lower():
            return False
    return True

def _frequency_cap_key(user_id, placement_code):
    return f"ads:fc:{user_id or 'anon'}:{placement_code}"

def _within_frequency_cap(user_id: Optional[int], placement_code: str, per_hour: int) -> bool:
    key = _frequency_cap_key(user_id, placement_code)
    current = cache.get(key)
    return (current or 0) < per_hour

def _bump_frequency_cap(user_id: Optional[int], placement_code: str, per_hour: int) -> None:
    key = _frequency_cap_key(user_id, placement_code)
    return key

def select_ad(request, placement_code, user_profile=None, freq_cap_per_hour=5, cache_ttl_seconds=60):
    # cache the selection briefly to avoid repeated DB hits
    cache_key = f"ads:sel:{placement_code}:{getattr(user_profile, 'id', 'anon')}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    campaigns = _campaigns_for_placement(placement_code)
    # Filter candidates by targeting
    eligible = []
    for campaign in campaigns:
        if _match_targeting(campaign, request, user_profile=user_profile):
            creatives = list(campaign.creatives.all())
            if creatives:
                eligible.append((campaign, creatives))

    if not eligible:
        cache.set(cache_key, None, cache_ttl_seconds)
        return None

    # Frequency capping (per user per placement per hour)
    user_id = getattr(user_profile, 'id', None)
    fc_key = _frequency_cap_key(user_id, placement_code)
    now = timezone.now()
    return f"{fc_key} {now}"
