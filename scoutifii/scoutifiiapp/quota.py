from datetime import date
from django.db.models import F
from django.utils.timezone import now
from scoutifiiapp.models import UsageQuota, Subscription


# def check_and_increment_upload_quota(user, max_uploads: int, bytes_size: int, max_bytes: int):
#     today = date.today()
#     quota, _ = UsageQuota.objects.get_or_create(user=user, period_start=today)
#     if quota.uploads >= max_uploads or quota.bytes_uploaded + bytes_size > max_bytes:
#         return False
#     UsageQuota.objects.filter(pk=quota.pk).update(
#         uploads=F("uploads") + 1,
#         bytes_uploaded=F("bytes_uploaded") + bytes_size,
#     )
#     return True


def get_user_daily_limits(user):
    sub = (Subscription.objects
           .select_related("plan")
           .filter(user=user, active=True, current_period_start__lte=now().date(),
                   current_period_end__gte=now().date())
           .first())
    if not sub:
        # fallback to a Free plan definition or defaults
        return {
            "max_uploads": 20,
            "max_bytes": 1 * 1024 * 1024 * 1024,  # 1 GiB
            "soft_limit": False,
        }
    plan = sub.plan
    return {
        "max_uploads": plan.max_uploads_per_day or 0,
        "max_bytes": plan.max_bytes_per_day or 0,
        "soft_limit": plan.soft_limit,
    }

def check_and_increment_upload_quota(user, bytes_size: int):
    limits = get_user_daily_limits(user)
    max_uploads = limits["max_uploads"]
    max_bytes = limits["max_bytes"]
    today = date.today()
    quota, _ = UsageQuota.objects.get_or_create(user=user, period_start=today)
    # hard limit
    if not limits["soft_limit"]:
        if (max_uploads and quota.uploads >= max_uploads) or \
           (max_bytes and quota.bytes_uploaded + bytes_size > max_bytes):
            return False

    # increment
    UsageQuota.objects.filter(pk=quota.pk).update(
        uploads=F("uploads") + 1,
        bytes_uploaded=F("bytes_uploaded") + bytes_size,
    )
    return True

