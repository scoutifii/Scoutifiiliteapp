from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .kafka.producer import send_event
from django.utils.timezone import now
from .models import (
    VideoReflexes, VideoFlair, VideoPositioning, 
    VideoMarking, VideoAnticipation, OffTheBallVideo, 
    VideoTackling, VideoVision, VideoSpeed, VideoHeading, 
    VideoJumpingReach, VideoWorkRate, VideoAggression, 
    VideoCharisma, VideoBallProtection, VideoShooting, 
    VideoTechnique, VideoPassing, VideoFinishing, 
    VideoBallControl, VideoFreeKick, VideoDribbling,
    VideoCrossing, VideoPace, Comment, LikePost, 
    Notification, VideoCloseRangeShotStoppingAbility,
    VideoSavingOneOnOne, VideoFootworkAndDistribution,
    VideoSavingPenalties, VideoConcentration, VideoAgility,
    VideoCommandingInDefence, FollowersCount, Post
)
import os
from dotenv import load_dotenv

load_dotenv()


@receiver(post_save, sender=FollowersCount)
def user_followed(sender, instance, created, *args, **kwargs):
    try:
        if not created:
            return

        follow = instance
        
        follower_user = User.objects.filter(username=follow.follower).first()
        followed_user = User.objects.filter(username=follow.user).first()

        if not follower_user or not followed_user:
            return  # safety if usernames don’t resolve

        Notification.objects.create(
            post=None,  # no post context for follows
            sender=follower_user,
            user=followed_user,
            profile=follow.profile,  # keep consistent with your other notifications
            text_preview=f"{follower_user.last_name} {follower_user.first_name} has started following you",
            notification_type=3,  # Follow
        )
    except Exception as e:
        raise e


@receiver(post_delete, sender=FollowersCount)
def user_unfollowed(sender, instance, *args, **kwargs):
    """
    When a FollowersCount row is deleted, remove the corresponding follow notification.
    """
    try:
        follow = instance
        follower_user = User.objects.filter(username=follow.follower).first()
        followed_user = User.objects.filter(username=follow.user).first()

        if not follower_user or not followed_user:
            return

        Notification.objects.filter(
            sender=follower_user,
            user=followed_user,
            profile=follow.profile,
            notification_type=3,
        ).delete()
    except Exception as e:
        raise e


@receiver(post_save, sender=Comment)   
def user_commented_post(sender, instance, created, *args, **kwargs):
    try:
        if created:
            comment = instance
            post = comment.post
            sender = comment.user
            profile = comment.profile
            text_preview = f"{comment.user.first_name} {comment.user.last_name} commented on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=2
            )  
    except Exception as e:
        raise e    


@receiver(post_delete, sender=Comment)
def user_uncommented_post(sender, instance, *args, **kwargs):
    try:
        comment = instance
        post = comment.post
        sender = comment.user
        profile = comment.profile

        notify = Notification.objects.filter(
            post=post, 
            user=sender, 
            profile=profile, 
            notification_type=2
        )
        notify.delete()  
    except Exception as e:
        raise e


@receiver(post_save, sender=LikePost)
def user_liked_post(sender, instance, created, *args, **kwargs):
    try:
        if created:
            like = instance
            post = like.post
            sender = like.user
            profile = like.profile
            text_preview = f"{like.user.first_name} {like.user.last_name} liked on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=1
            )
    except Exception as e:
        raise e


@receiver(post_delete, sender=LikePost)
def user_unliked_post(sender, instance, *args, **kwargs):
    try:
        like = instance
        post = like.post
        sender = like.user
        profile = like.profile

        notify = Notification.objects.filter(
            post=post,
            user=sender, 
            profile=profile, 
            notification_type=1
        )
        notify.delete()
    except Exception as e:
        raise e

@receiver(post_save, sender=OffTheBallVideo)
def user_rated_offTheBallVideo(sender, instance, created, *args, **kwargs):
    try:
        if created:
            offTheBallVideo = instance
            post = offTheBallVideo.post
            sender = offTheBallVideo.user
            profile = offTheBallVideo.profile
            text_preview = f"{offTheBallVideo.user.first_name} {offTheBallVideo.user.last_name} voted on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e

@receiver(post_save, sender=VideoPositioning)
def user_rated_positioning(sender, instance, created, *args, **kwargs):
    try:
        if created:
            positioning = instance
            post = positioning.post
            sender = positioning.user
            profile = positioning.profile
            text_preview = f"{positioning.user.first_name} {positioning.user.last_name} voted on your post"

            Notification.objects.create(
               post=post,
               sender=sender, 
               user=post.user,
               profile=profile, 
               text_preview=text_preview, 
               notification_type=4
            )  
    except Exception as e:
        raise e
        
@receiver(post_save, sender=VideoMarking)
def user_rated_marking(sender, instance, created, *args, **kwargs):
    try:
        if created:
            marking = instance
            post = marking.post
            sender = marking.user
            profile = marking.profile
            text_preview = f"{marking.user.first_name} {marking.user.last_name} voted on your post"

            Notification.objects.create(
               post=post, 
               sender=sender, 
               user=post.user, 
               profile=profile, 
               text_preview=text_preview,
               notification_type=4
            ) 
    except Exception as e:
        raise e

@receiver(post_save, sender=VideoAnticipation)
def user_rated_anticipation(sender, instance, created, *args, **kwargs):
    try:
        if created:
            anticipation = instance
            post = anticipation.post
            sender = anticipation.user
            profile = anticipation.profile
            text_preview = f"{anticipation.user.first_name} {anticipation.user.last_name} voted on your post"

            Notification.objects.create(
               post=post, 
               sender=sender, 
               user=post.user, 
               profile=profile, 
               text_preview=text_preview, 
               notification_type=4
            ) 
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoPace)
def user_rated_pace(sender, instance, created, *args, **kwargs):
    try:
        if created:
            pace = instance
            post = pace.post
            sender = pace.user
            profile = pace.profile
            text_preview = f"{pace.user.first_name} {pace.user.last_name} voted on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoTackling)
def user_rated_tackling(sender, instance, created, *args, **kwargs):
    try:
        if created:
            tackling = instance
            post = tackling.post
            sender = tackling.user
            profile = tackling.profile
            text_preview = f"{tackling.user.first_name} {tackling.user.last_name} voted on your post"

            Notification.objects.create(
               post=post, 
               sender=sender, 
               user=post.user, 
               profile=profile, 
               text_preview=text_preview, 
               notification_type=4
            ) 
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoVision)
def user_rated_vision(sender, instance, created, *args, **kwargs):
    try:
        if created:
            vision = instance
            post = vision.post
            sender = vision.user
            profile = vision.profile
            text_preview = f"{vision.user.first_name} {vision.user.last_name} voted on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            ) 
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoWorkRate)
def user_rated_workrate(sender, instance, created, *args, **kwargs):
    try:
        if created:
            workrate = instance
            post = workrate.post
            sender = workrate.user
            profile = workrate.profile
            text_preview = f"{workrate.user.first_name} {workrate.user.last_name} voted on your post"

            Notification.objects.create(
               post=post, 
               sender=sender, 
               user=post.user, 
               profile=profile, 
               text_preview=text_preview, 
               notification_type=4
            ) 
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoAggression)
def user_rated_aggression(sender, instance, created, *args, **kwargs):
    try:
        if created:
            aggression = instance
            post = aggression.post
            sender = aggression.user
            profile = aggression.profile
            text_preview = f"{aggression.user.first_name} {aggression.user.last_name} voted on your post"

            Notification.objects.create(
               post=post, 
               sender=sender, 
               user=post.user, 
               profile=profile, 
               text_preview=text_preview, 
               notification_type=4
            ) 
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoCharisma)
def user_rated_charisma(sender, instance, created, *args, **kwargs):
    try:
        if created:
            charisma = instance
            post = charisma.post
            sender = charisma.user
            profile = charisma.profile
            text_preview = f"{charisma.user.first_name} {charisma.user.last_name} voted on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e
    

@receiver(post_save, sender=VideoBallProtection)
def user_rated_ballprotection(sender, instance, created, *args, **kwargs):
    try:
        if created:
            ballprotection = instance
            post = ballprotection.post
            sender = ballprotection.user
            profile = ballprotection.profile
            text_preview = f"{ballprotection.user.first_name} {ballprotection.user.last_name} voted on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoSpeed)
def user_rated_speed(sender, instance, created, *args, **kwargs):
    try:
        if created:
            speed = instance
            post = speed.post
            sender = speed.user
            profile = speed.profile
            text_preview = f"{speed.user.first_name} {speed.user.last_name} voted on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoHeading)
def user_rated_heading(sender, instance, created, *args, **kwargs):
    try:
        if created:
            heading = instance
            post = heading.post
            sender = heading.user
            text_preview = f"{heading.user.first_name} {heading.user.last_name} voted on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=post.profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoFlair)
def user_rated_flair(sender, instance, created, *args, **kwargs):
    try:
        if created:
            flair = instance
            post = flair.post
            sender = flair.user
            profile = flair.profile
            text_preview = f"{flair.user.first_name} {flair.user.last_name} voted on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoJumpingReach)
def user_rated_jumpingreach(sender, instance, created, *args, **kwargs):
    try:
        if created:
            jumpingreach = instance
            post = jumpingreach.post
            sender = jumpingreach.user
            profile = jumpingreach.profile
            text_preview = f"{jumpingreach.user.first_name} {jumpingreach.user.last_name} voted on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoShooting)
def user_rated_shooting(sender, instance, created, *args, **kwargs):
    try:
        if created:
            shooting = instance
            post = shooting.post
            sender = shooting.user
            profile = shooting.profile
            text_preview = f"{shooting.user.first_name} {shooting.user.last_name} voted your ball passing skill on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoTechnique)
def user_rated_technique(sender, instance, created, *args, **kwargs):
    try:
        if created:
            technique = instance
            post = technique.post
            sender = technique.user
            profile = technique.profile
            text_preview = f"{technique.user.first_name} {technique.user.last_name} voted your ball technique on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoPassing)
def user_rated_passing(sender, instance, created, *args, **kwargs):
    try:
        if created:
            passing = instance
            post = passing.post
            sender = passing.user
            profile = passing.profile
            text_preview = f"{passing.user.first_name} {passing.user.last_name} voted your passing skill on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoFinishing)
def user_rated_finishing(sender, instance, created, *args, **kwargs):
    try:
        if created:
            finishing = instance
            post = finishing.post
            sender = finishing.user
            profile = finishing.profile
            text_preview = f"{finishing.user.first_name} {finishing.user.last_name} voted finishing skill on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoBallControl)
def user_rated_ballcontrol(sender, instance, created, *args, **kwargs):
    try:
        if created:
            ballcontrol = instance
            post = ballcontrol.post
            sender = ballcontrol.user
            profile = ballcontrol.profile
            text_preview = f"{ballcontrol.user.first_name} {ballcontrol.user.last_name} voted ball control skill on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoFreeKick)
def user_rated_freekick(sender, instance, created, *args, **kwargs):
    try:
        if created:
            freekick = instance
            post = freekick.post
            sender = freekick.user
            profile = freekick.profile
            text_preview = f"{freekick.user.first_name} {freekick.user.last_name} voted freekick skill on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoDribbling)
def user_rated_dribbling(sender, instance, created, *args, **kwargs):
    try:
        if created:
            dribbling = instance
            post = dribbling.post
            sender = dribbling.user
            profile = dribbling.profile
            text_preview = f"{dribbling.user.first_name} {dribbling.user.last_name} voted for dribbling skill on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoCrossing)
def user_rated_crossing(sender, instance, created, *args, **kwargs):
    try:
        if created:
            crossing = instance
            post = crossing.post
            sender = crossing.user
            profile = crossing.profile
            text_preview = f"{crossing.user.first_name} {crossing.user.last_name} voted for crossing skill on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoSavingOneOnOne)
def user_rated_savingoneonone(sender, instance, created, *args, **kwargs):
    try:
        if created:
            savingoneonone = instance
            post = savingoneonone.post
            sender = savingoneonone.user
            profile = savingoneonone.profile
            text_preview = f"{savingoneonone.user.first_name} {savingoneonone.user.last_name} voted saving one-on-one skill on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoFootworkAndDistribution)
def user_rated_footworkanddistribution(sender, instance, created, *args, **kwargs):
    try:
        if created:
            footworkanddistribution = instance
            post = footworkanddistribution.post
            sender = footworkanddistribution.user
            profile = footworkanddistribution.profile
            text_preview = f"{footworkanddistribution.user.first_name} {footworkanddistribution.user.last_name} voted your footwork distribution on your post"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoSavingPenalties)
def user_rated_savingpenalties(sender, instance, created, *args, **kwargs):
    try:
        if created:
            savingpenalties = instance
            post = savingpenalties.post
            sender = savingpenalties.user
            profile = savingpenalties.profile
            text_preview = "Saving Penalties"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoConcentration)
def user_rated_concentration(sender, instance, created, *args, **kwargs):
    try:
        if created:
            concentration = instance
            post = concentration.post
            sender = concentration.user
            profile = concentration.profile
            text_preview = "Concentration"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoAgility)
def user_rated_agility(sender, instance, created, *args, **kwargs):
    try:
        if created:
            agility = instance
            post = agility.post
            sender = agility.user
            profile = agility.profile
            text_preview = "Agility"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoCloseRangeShotStoppingAbility)
def user_rated_closerangeshotstoppingability(sender, instance, created, *args, **kwargs):
    try:
        if created:
            closerangeshotstoppingability = instance
            post = closerangeshotstoppingability.post
            sender = closerangeshotstoppingability.user
            profile = closerangeshotstoppingability.profile
            text_preview = "Close Range Shot Stopping Ability"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoReflexes)
def user_rated_reflexes(sender, instance, created, *args, **kwargs):
    try:
        if created:
            reflexes = instance
            post = reflexes.post
            sender = reflexes.user
            profile = reflexes.profile
            text_preview = "Reflexes"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=VideoCommandingInDefence)
def user_rated_commandingindefence(sender, instance, created, *args, **kwargs):
    try:
        if created:
            commandingindefence = instance
            post = commandingindefence.post
            sender = commandingindefence.user
            profile = commandingindefence.profile
            text_preview = "Commanding in Defence"

            Notification.objects.create(
                post=post, 
                sender=sender, 
                user=post.user, 
                profile=profile, 
                text_preview=text_preview, 
                notification_type=4
            )
    except Exception as e:
        raise e


@receiver(post_save, sender=Post)
def post_created_event(sender, instance: "Post", created, **kwargs):
    if not created:
        return
    payload = {
        "id": instance.id,
        "user_id": instance.user_id,
        "created_at": now().isoformat(),
        "video_url": getattr(instance, "video", None) and instance.video.url,
        "caption": getattr(instance, "caption", None),
    }
    send_event(os.getenv('KAFKA_TOPICS["post_created"]'), key=str(instance.id), payload=payload)


@receiver(post_save, sender=Comment)
def comment_created_event(sender, instance: "Comment", created, **kwargs):
    if not created:
        return
    payload = {
        "id": instance.id,
        "post_id": instance.post_id,
        "author_id": instance.user_id,
        "text": instance.body[:512],
        "created_at": now().isoformat(),
    }
    send_event(os.getenv('KAFKA_TOPICS["comment_created"]'), key=str(instance.post_id), payload=payload)