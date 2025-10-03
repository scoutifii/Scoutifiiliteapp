from django.contrib import admin
from .models import (
	AllLogins, Profile, BrandSetting, Post, Comment, LikePost,
	VideoAggression, VideoAnticipation, VideoBallControl, VideoBallProtection,
    VideoCommandingInDefence, VideoConcentration, VideoCrossing, VideoDribbling,
    VideoFinishing, VideoFlair, VideoFootworkAndDistribution, VideoHeading,
    VideoJumpingReach, VideoPace, VideoPassing, VideoReflexes, VideoSavingOneOnOne,
    VideoSavingPenalties, VideoShooting, VideoSpeed, VideoTackling, VideoTechnique,
    VideoVision, VideoWorkRate, VideoAgility, VideoCloseRangeShotStoppingAbility,
	OffTheBallVideo, VideoPositioning, VideoMarking, FollowersCount,
    VideoCounts, Notification, VideoCharisma, VideoFreeKick,
	Notification, Repost, Plan, Subscription, OverageEvent, UsageQuota,
	Advertiser, AdPlacement, AdClick, Campaign, Creative, AdImpression
)

class AllLoginsAdmin(admin.ModelAdmin):
	list_display = ['user', 'username', 'login_date', 'last_logged_out']
class ProfileAdmin(admin.ModelAdmin):
	list_display = ['user', 'profileimg', 'bio', 'location', 'phone_no', 'country_id', 'created_at']

admin.site.register(AllLogins, AllLoginsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(BrandSetting)
admin.site.register(Post)
admin.site.register(LikePost)
admin.site.register(Comment)
admin.site.register(VideoCounts)
admin.site.register(OffTheBallVideo)
admin.site.register(VideoPositioning)
admin.site.register(VideoMarking)
admin.site.register(VideoAnticipation)
admin.site.register(VideoPace)
admin.site.register(VideoTackling)
admin.site.register(VideoVision)
admin.site.register(VideoWorkRate)
admin.site.register(VideoAggression)
admin.site.register(VideoCharisma)
admin.site.register(VideoBallProtection)
admin.site.register(VideoSpeed)
admin.site.register(VideoHeading)
admin.site.register(VideoFlair)
admin.site.register(VideoJumpingReach)
admin.site.register(VideoShooting)
admin.site.register(VideoTechnique)
admin.site.register(VideoPassing)
admin.site.register(VideoFinishing)
admin.site.register(VideoBallControl)
admin.site.register(VideoFreeKick)
admin.site.register(VideoDribbling)
admin.site.register(VideoCrossing)
admin.site.register(FollowersCount)
admin.site.register(VideoReflexes)
admin.site.register(Notification)
admin.site.register(VideoSavingOneOnOne)
admin.site.register(VideoCommandingInDefence)
admin.site.register(VideoFootworkAndDistribution)
admin.site.register(VideoSavingPenalties)
admin.site.register(VideoConcentration)
admin.site.register(VideoAgility)
admin.site.register(VideoCloseRangeShotStoppingAbility)
admin.site.register(Repost)
admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(OverageEvent)
admin.site.register(UsageQuota)
admin.site.register(Campaign)
admin.site.register(Creative)
admin.site.register(AdImpression)
admin.site.register(AdClick)
admin.site.register(Advertiser)
admin.site.register(AdPlacement)