from datetime import date
from django.db.models import Count, Q
from django.utils import timezone
from .models import Campaign, AdPlacement, AdImpression, Creative
from typing import Optional

FREQ_CAP_PER_USER_PER_DAY = 5       # max impressions per user per campaign/day
FREQ_CAP_PER_IP_PER_DAY = 10        # max impressions per IP per campaign/day
ASSUMED_ECPM_CENTS = 200            # fallback eCPM for CPM pacing if no pricing model
ASSUMED_CPC_CENTS = 50              # fallback CPC pacing (used to estimate spend)
MIN_ROTATION_PER_CAMPAIGN = 1 


def _campaign_under_daily_budget(campaign: Campaign, today: date) -> bool:
    """
    Very simple pacing:
      - Spend estimate = impressions_today * eCPM/1000 + clicks_today * CPC
      - Must be <= daily_budget_cents (if provided)
    """
    if not getattr(campaign, "daily_budget_cents", None):
        return True

    agg = AdImpression.objects.filter(
        campaign=campaign,
        created_at__date=today,
    ).aggregate(
        imps=Count("id"),
        clicks=Count("clicks"),
    )
    imps = agg["imps"] or 0
    clicks = agg["clicks"] or 0

    # Estimated spend in cents
    est_spend_cents = int(imps * ASSUMED_ECPM_CENTS / 1000) + clicks * ASSUMED_CPC_CENTS
    # Allow at least MIN_ROTATION_PER_CAMPAIGN even if tiny overshoot
    if imps < MIN_ROTATION_PER_CAMPAIGN:
        return True
    return est_spend_cents <= (campaign.daily_budget_cents or 0)


def _pass_frequency_cap(campaign: Campaign, user, ip: Optional[str], today: date) -> bool:
    """
    Enforce per-user and per-IP per campaign per day caps.
    """
    q = Q(campaign=campaign, created_at__date=today)
    if user and user.is_authenticated:
        user_count = AdImpression.objects.filter(q, user=user).count()
        if user_count >= FREQ_CAP_PER_USER_PER_DAY:
            return False
    if ip:
        ip_count = AdImpression.objects.filter(q, ip=ip).count()
        if ip_count >= FREQ_CAP_PER_IP_PER_DAY:
            return False
    return True


def select_creative(
        placement_code: str, 
        user=None, 
        ip: Optional[str] = None
    ) -> Optional[
        tuple[AdPlacement, Campaign, Creative]]:
    """
    Returns (placement, campaign, creative) or None if nothing eligible.
    Applies:
      - active, time window, placement
      - simple targeting
      - daily pacing by impressions/clicks against daily_budget_cents
      - frequency caps by user/IP/day
      - fair rotation via least-impressions-today ordering
    """
    now = timezone.now()
    today = now.date()
    try:
        placement = AdPlacement.objects.get(code=placement_code)
    except AdPlacement.DoesNotExist:
        return None

    qs = Campaign.objects.filter(
        active=True,
        placement=placement,
        start_at__lte=now,
        end_at__gte=now,
    )

    # Optional targeting
    country_code = None
    profile_type = None
    if user and hasattr(user, "profile"):
        prof = getattr(user, "profile").first() if hasattr(user.profile, "first") else None
        if prof:
            # Adjust to your actual field names
            country_code = getattr(getattr(prof, "country_id", None), "code", None) or None
            profile_type = getattr(prof, "profile_type_data", None) or None

    if country_code:
        qs = qs.filter(Q(target_country="") | Q(target_country__isnull=True) | Q(target_country=country_code))
    else:
        qs = qs.filter(Q(target_country="") | Q(target_country__isnull=True))

    if profile_type:
        qs = qs.filter(Q(target_profile_type="") | Q(target_profile_type__isnull=True) | Q(target_profile_type=profile_type))
    else:
        qs = qs.filter(Q(target_profile_type="") | Q(target_profile_type__isnull=True))

    # Fair rotation: prefer fewer impressions today
    qs = qs.annotate(
        today_imps=Count("impressions", filter=Q(impressions__created_at__date=today)),
    ).order_by("today_imps", "id")

    for campaign in qs:
        # Budget pacing
        if not _campaign_under_daily_budget(campaign, today):
            continue
        # Frequency caps
        if not _pass_frequency_cap(campaign, user, ip, today):
            continue
        # Pick a creative at random; you can add weights later
        creative = campaign.creatives.order_by("?").first()
        if creative:
            return placement, campaign, creative
    
    return None
