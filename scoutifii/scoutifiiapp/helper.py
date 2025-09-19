from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _ 
import os
import math
from django.utils import timezone
import user_agents


def validate_image_file_size(value):
    filesize = value.size
    
    if filesize > 1024 * 1024 * 2:    # 2MB
        raise ValidationError(_("The maximum file size that can be uploaded is 2MB"))
    else:
        return value


def validate_video_file_size(value):
    filesize = value.size
    
    if filesize > 1024 * 1024 * 50:    # 50MB
        raise ValidationError(_("The maximum file size that can be uploaded is 50MB"))
    else:
        return value


def validate_image_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.jpg', '.jpeg', '.png']
    if not ext.lower() not in valid_extensions:
        raise ValidationError(
            _('Unsupported file extension. Allowed extensions are: .jpg, .jpeg, .png'), 
            code='invalid_extension')


def validate_video_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv']
    if not ext.lower() not in valid_extensions:
        raise ValidationError(
            _('Unsupported file extension. Allowed extensions are: .mp4, .mov, .avi, .wmv, .flv, .mkv'), 
            code='invalid_extension')


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