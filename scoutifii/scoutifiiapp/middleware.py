from scoutifiiapp.models import ActivityLog
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class CustomActivityLog(MiddlewareMixin, LoginRequiredMixin):
	def process_request(self, request):
		try:
			if not request.META['PATH_INFO'].startswith('/media') and request.user.is_authenticated:
				activity = ActivityLog()
				activity.activity = f"request - {request.user}"
				activity.user_id = request.user.pk
				activity.username = request.user.username
				activity.ip_address = request.META['REMOTE_ADDR']
				activity.url = request.META['PATH_INFO']
				activity.user_agent = request.META['HTTP_USER_AGENT']
				activity.created_at = datetime.now()
				activity.save()
		except Exception as e:
			raise e

		return None