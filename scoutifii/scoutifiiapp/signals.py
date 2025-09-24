from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
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
    VideoCommandingInDefence, FollowersCount
)


@receiver(post_save, sender=FollowersCount)
def user_followed(sender, instance, created, *args, **kwargs):
    """
    When a FollowersCount row is created, create a follow notification (type 3).
    """
    try:
        if not created:
            return

        follow = instance
        # FollowersCount stores usernames as \CharFields
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
            text_preview = 'You commented'

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
            text_preview = 'You liked'

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
            text_preview = "Off the Ball"

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
            text_preview = "Positioning"

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
            text_preview = "Marking"

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
            text_preview = "Anticipation"

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
            text_preview = "Pace"

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
            text_preview = "Tackling"

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
            text_preview = "Vision"

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
            text_preview = "Workrate"

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
            text_preview = "Aggression"

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
            text_preview = "Charisma"

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
            text_preview = "Ball Protection"

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
            text_preview = "Speed"

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
            text_preview = "Heading"

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
            text_preview = "Flair"

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
            text_preview = "Jumping Reach"

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
            text_preview = "Shooting"

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
            text_preview = "Technique"

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
            text_preview = "Passing"

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
            text_preview = "Finishing"

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
            text_preview = "Ball Control"

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
            text_preview = "Freekick"

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
            text_preview = "Dribbling"

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
            text_preview = "Crossing"

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
            text_preview = "Saving One on One"

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
            text_preview = "Footwork Distribution"

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
    