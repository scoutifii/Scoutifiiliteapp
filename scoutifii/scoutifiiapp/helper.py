from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _ 
import os
import math
from django.utils import timezone
import user_agents
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import magic

MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50MB
MAX_IMAGE_SIZE = 2 * 1024 * 1024   # 2MB
ALLOWED_IMAGE_EXTS = {'.jpg', '.jpeg', '.png'}
ALLOWED_IMAGE_MIME_PREFIXES = ('image/',)  # generic; or use a
ALLOWED_VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv'}
ALLOWED_VIDEO_MIME_PREFIXES = ('video/',)  # generic; or use a whitelist


def validate_video_file_size(value):
    filesize = getattr(value, 'size', None)
    if filesize is None:
        return value
    if filesize > MAX_VIDEO_SIZE:
        raise ValidationError(_("The maximum file size that can be uploaded is 50MB"))
    return value


def validate_video_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_VIDEO_EXTS:
        raise ValidationError(
            _('Unsupported file extension. Allowed: %(exts)s'),
            code='invalid_extension',
            params={'exts': ', '.join(sorted(ALLOWED_VIDEO_EXTS))}
        )


def validate_video_mime(value):
    # Peek content to detect actual MIME type (prevents spoofing by extension)
    try:
        # value.file may be an InMemoryUploadedFile or TemporaryUploadedFile
        # Read small header; magic.from_buffer does not consume the stream
        fileobj = getattr(value, 'file', value)
        pos = fileobj.tell()
        head = fileobj.read(2048)
        fileobj.seek(pos)
        mime = magic.from_buffer(head, mime=True)  # e.g., 'video/mp4'
    except Exception:
        return  # Fail-open or raise your own error

    if not mime or not mime.startswith(ALLOWED_VIDEO_MIME_PREFIXES):
        raise ValidationError(
			_('Invalid video content type: %(mime)s'), 
			params={'mime': mime or 'unknown'}
		)

def validate_image_file_size(value):
    filesize = value.size
    
    if filesize > MAX_IMAGE_SIZE:    
        raise ValidationError(
			_("The maximum file size that can be uploaded is 2MB")
		)
    else:
        return value


def validate_image_file_extension(value):
	ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
	if not ext.lower() in ALLOWED_IMAGE_EXTS:
		raise ValidationError(_('Unsupported file extension. Allowed: %(exts)s'), 
			code='invalid_extension',
			params={'exts': ', '.join(sorted(ALLOWED_IMAGE_EXTS))} 
		)

def validate_image_mime(value):
	# Peek content to detect actual MIME type (prevents spoofing by extension)
	try:
		# value.file may be an InMemoryUploadedFile or TemporaryUploadedFile
		# Read small header; magic.from_buffer does not consume the stream
		fileobj = getattr(value, 'file', value)
		pos = fileobj.tell()
		head = fileobj.read(2048)
		fileobj.seek(pos)
		mime = magic.from_buffer(head, mime=True)  # e.g., 'image/jpeg'
	except Exception:
		return  # Fail-open or raise your own error

	if not mime or not mime.startswith(ALLOWED_IMAGE_MIME_PREFIXES):
		raise ValidationError(
			_('Invalid image content type: %(mime)s'), 
			params={'mime': mime or 'unknown'}
		)


def timeago(self):
	now = timezone.now()
	diff = now - self.created_at

	if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
		seconds = diff.seconds

		if seconds == 1:
			return str(seconds) +  "s"
		else:
			return str(seconds) + "seconds"
	if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
		minutes = math.floor(diff.seconds/60)

		if minutes == 1:
			return str(minutes) + "m"
		else:
			return str(minutes) + "minutes"

	if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
		hours = math.floor(diff.seconds/3600)

		if hours == 1:
			return str(hours) + "h"
		else:
			return str(hours) + "hours"

    # 1 day to 30 days
	if diff.days >= 1 and diff.days <= 6:
		days = diff.days

		if days == 1:
			return str(days) + "d"
		else:
			return str(days) + "days"

    # 1 week to 4 weeks
	if diff.days >= 7 and diff.days < 31:
		weeks = math.floor(diff.days/7)

		if weeks == 1:
			return str(weeks) + "week"
		else:
			return str(weeks) + "weeks"

    #  1 month to 12 month
	if diff.days >= 31 and diff.days < 365:
		months = math.floor(diff.days/31)

		if months == 1:
			return str(months) + "month"
		else:
			return str(months) + "months"

    #  1 year to unlimited years
	if diff.days >= 365:
		years = math.floor(diff.days/365)

		if years == 1:
			return str(years) + "y"
		else:
			return str(years) + "years"


def parse_user_agent(user_agent_string):
	user_agent = user_agents.parse(user_agent_string)
	device_type = "Desktop"
	if user_agent.is_mobile:
		device_type = "Mobile"
	elif user_agent.is_tablet:
		device_type = "Tablet"

	return {
		'device_type': device_type,
		'browser': user_agent.browser.family,
	}


class VideoStorage(FileSystemStorage):
	def __init__(self, location=None, base_url=None):
		location = location or getattr(settings, 'VIDEOS_ROOT', None)
		base_url = base_url or getattr(settings, 'VIDEOS_URL', None)
		super().__init__(location=location, base_url=base_url)