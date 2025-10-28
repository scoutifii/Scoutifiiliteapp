from django.shortcuts import (
    render, 
    redirect, 
    HttpResponseRedirect, 
    reverse
)
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .models import (
    AllLogins, Profile, Post, VideoFlair, VideoPositioning, 
    VideoMarking, VideoAnticipation, OffTheBallVideo, 
    VideoTackling, VideoVision, VideoSpeed, VideoHeading, 
    VideoJumpingReach, VideoWorkRate, VideoAggression, 
    VideoCharisma, VideoBallProtection, VideoShooting, 
    VideoTechnique, VideoPassing, VideoFinishing, 
    VideoBallControl, VideoFreeKick, VideoDribbling,
    VideoCrossing, VideoPace, Comment, LikePost, 
    FollowersCount, Notification, ActivityLog,
    Repost, VideoCounts, LiveStream, AdImpression, 
    AdClick, BrandSetting
)
from django.utils import timezone
# from django.utils.timezone import now
# import os
from dotenv import load_dotenv
from django.contrib import auth
from django.core.cache import cache
from django.contrib import messages
import random
import json
from django.core.exceptions import PermissionDenied
from itertools import chain
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from .helper import parse_user_agent
from django.views.generic import TemplateView
from django.views.decorators.http import (
    require_GET, 
    require_POST,
    require_http_methods
)
from django.shortcuts import get_object_or_404
# from scoutifiiapp.kafka.producer import send_event
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import mail_managers
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .ad_selector import select_creative
from django.db import transaction
from django.utils.html import escape


load_dotenv()


def index(request):
    if request.user.is_authenticated:
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)
        posts = Post.objects.all().order_by('-created_at')
        brand_setting = BrandSetting.objects.all()
        year = datetime.now().strftime("%Y")
    else:
        user_profile = Profile.objects.all()
        posts = Post.objects.all().order_by('-created_at')
        brand_setting = BrandSetting.objects.all()
        year = datetime.now().strftime("%Y")

    context = {
        'posts': posts,
        'user_profile': user_profile,
        'brand_setting': brand_setting,
        'year': year,
    }
    return render(request, 'index.html', context)


@login_required(login_url='login')
def dashboard(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)
    brand_setting = BrandSetting.objects.all()    
    year = datetime.now().strftime("%Y")

    # assign two empty lists, list to contain all logged in user is following
    user_following_list = []  # List that will contain users the logged in user is following
    feed = []  # List that will contain the posts that the logged in user is following
    user_following = FollowersCount.objects.filter(
        follower=request.user.username
    )

    for users in user_following:
        user_following_list.append(users.user)    
    # append to the feed list
    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user_prof=usernames)
        feed.append(feed_lists)


    # convert to a feed list and pass it to posts under context
    feed_list = list(chain(*feed))
    random.shuffle(feed)    
    # user suggestions
    all_users = User.objects.all()
    user_following_all = []

    for obj in user_following:
        user_list = User.objects.get(username=obj.user)
        user_following_all.append(user_list)

    new_suggestions_list = [
        x for x in list(all_users)
        if (x not in list(user_following_all))
    ]
    current_user = User.objects.filter(username=request.user.username)
    # list of all we are not following and is not myself
    final_suggestions_list = [
        x for x in list(new_suggestions_list)
        if (x not in list(current_user))
    ]
    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))
    num_of_followers = len(suggestions_username_profile_list)
    # token = str(uuid.uuid4())  

    context = {
        'user_profile': user_profile, 
        'posts': feed_list,
        'brand_setting': brand_setting,
        'username_suggestions': suggestions_username_profile_list,
        'year': year,
        'num_of_followers': num_of_followers,
        # 'token': token
    }
    return render(request, 'dashboard.html', context)


def signup(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if password == password_confirm:
            if User.objects.filter(email__iexact=email).exists():
                messages.info(request, 'Email Exists')
                return redirect('signup')
            elif User.objects.filter(username__iexact=username).exists():
                messages.info(request, 'Username Exists')
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    email=email,
                    password=password
                )
                user.save()               
                user_login = auth.authenticate(
                    username=username, password=password
                )
                auth.login(request, user_login)

                return redirect('settings')

        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')
    else:
        return redirect('index')


def track_login_attempts(request, username):
    attempts = cache.get(f'login_attempts_{username}', 0)
    cache.set(f'login_attempts_{username}', attempts + 1, 60 * 60)
    return attempts + 1  # Return updated attempts


def login(request):
    if request.user.is_authenticated:
        return redirect('settings')
    else:
        ip_address = request.META['REMOTE_ADDR']
        host = request.META['SERVER_NAME']
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        device_info = parse_user_agent(user_agent_string)
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            attempts = track_login_attempts(request, username)

            if attempts > 3:
                # Handle too many login attempts
                return render(request, "too_many_attempts.html")

            user = auth.authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    cache.delete(f'login_attempts_{username}')
                    login_record = AllLogins.objects.create(
                        user=request.user, 
                        username=request.user.username, 
                        ip_address=ip_address, 
                        server=host,
                        last_logged_out=None,
                        user_agent=user_agent_string,
                        device_type=device_info['device_type'],
                        browser=device_info['browser']
                    )
                    request.session['login_record_id'] = login_record.id
                    return redirect('dashboard')
                else:
                    messages.info(request, 'Account Deactivated')
            else:
                messages.info(request, 'Invalid username OR password')
                return redirect('login')

        return redirect('index')


@login_required(login_url='login')
def logout(request):
    login_record_id = request.session.get('login_record_id')
    if login_record_id:
        AllLogins.objects.filter(
            id=login_record_id
        ).update(last_logged_out=timezone.now())
        # Optionally, remove the session key
        del request.session['login_record_id']
    auth.logout(request)
    return redirect('index')


@login_required(login_url='login')
@require_http_methods(["GET", "POST"])
def settings(request):
    brand_setting = BrandSetting.objects.all()
    otp = random.randint(10000, 99999)

    try:
        profile = Profile.objects.get(user=request.user)
        is_new = False
    except Profile.DoesNotExist:
        profile = Profile(user=request.user, id_user=request.user.id)
        is_new = True
     
    if request.method == "POST":
        profile.bio = (request.POST.get('bio') or '').strip()
        profile.location = request.POST.get('location') or ''
        profile.phone_no = request.POST.get('phone_no') or ''
        profile.country_id = request.POST.get('country_id') or ''
        profile.profile_type_data = request.POST.get('profile_type_data') or ''
        profile.primary_position = request.POST.get('primary_position', '') or ''
        profile.dominant_side = request.POST.get('dominant_side', '') or ''
        profile.height_cm = request.POST.get('height_cm') or None
        profile.weight_kg = request.POST.get('weight_kg') or None
        profile.jersey_number = request.POST.get('jersey_number') or ''
        profile.otp = getattr(profile, 'otp', None) or otp
        profile.birth_date = (request.POST.get('birth_date') or '').strip()

        secondary_positions = request.POST.getlist('secondary_positions')
        profile.secondary_positions = secondary_positions

        privacy = {
            'bio_public': bool(request.POST.get('privacy_settings[bio_public]')),
            'contact_public': bool(request.POST.get('privacy_settings[contact_public]')),
            'media_public': bool(request.POST.get('privacy_settings[media_public]')),
        }
        profile.privacy_settings = privacy

        # Image upload
        uploaded = request.FILES.get('profileimg')
        if uploaded:
            profile.profileimg = uploaded   

        profile.save()
        messages.success(request, "Profile created." if is_new else "Profile updated")
        return redirect('dashboard')

    context = {
        'brand_setting': brand_setting,
        'user_profile': profile,
    }

    return render(request, 'settings.html', context)


@login_required(login_url='login')
def search(request):
    brand_setting = BrandSetting.objects.all()
    user_object = User.objects.get(username=request.user.username) 
    user_profile = Profile.objects.get(user=user_object) 
    
    if request.method == 'POST':
        q = request.GET.get("q", "").strip()
        username_object = User.objects.filter(username__icontains=q)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(
                id_user=ids
            )
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

        context = {
            'user_profile': user_profile, 
            'username_profile_list': username_profile_list,
            'brand_setting': brand_setting,
            'q': q,
        }

    return render(request, 'search.html', context)


@login_required(login_url='login')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=user_object).order_by('-created_at')
    user_post_length = len(user_posts)
    brand_setting = BrandSetting.objects.all()

    follower = request.user.username   # someone is following
    user = pk  # Someone that's being followed
    # if this is in our database, these means the user is already following
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Following'
        Profile.objects.update(status=1)
    else:
        button_text = 'Follow'
        Profile.objects.update(status=0)

    # len() is the integer for calculating numbers
    user_followers = len(FollowersCount.objects.filter(user=user))
    user_following = len(FollowersCount.objects.filter(follower=follower))

    year = datetime.now().strftime("%Y")

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following,
        'brand_setting': brand_setting,
        'year': year
    }

    return render(request, 'profile.html', context)


@login_required(login_url='login')
def follower(request, pk):
    user_object = get_object_or_404(User, username=pk)
    user_profile = get_object_or_404(Profile, user=user_object)
    brand_setting = BrandSetting.objects.all()
   
    follower_qs = FollowersCount.objects.filter(user=user_object.username) 
    
    # Count without materializing the list
    user_followers = follower_qs.count()

    # Get actual follower users in one go
    follower_usernames = follower_qs.values_list('follower', flat=True)

    followers_users = (
        User.objects.filter(username__in=follower_usernames)
        .select_related('profile')
        .only('id', 'username', 'first_name', 'last_name', 'profile__profileimg', 'profile__bio')
        .order_by('username')
    )

    # Pagination (query param ?page=)
    page = request.GET.get('page', 1)
    paginator = Paginator(followers_users, 24)  # 24 per page
    try:
        followers_page = paginator.page(page)
    except PageNotAnInteger:
        followers_page = paginator.page(1)
    except EmptyPage:
        followers_page = paginator.page(paginator.num_pages)

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_followers': user_followers,
        'brand_setting': brand_setting,
        'paginator': paginator,
        'followers_page': followers_page, 
    }

    return render(request, 'follower.html', context)


@login_required(login_url='login')
def following(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    brand_setting = BrandSetting.objects.all()
    follower = pk
    user_following = len(FollowersCount.objects.filter(follower=follower))
    user_following_list = list(FollowersCount.objects.filter(follower=follower))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_following_list': user_following_list,
        'user_following': user_following,
        'brand_setting': brand_setting
    }

    return render(request, 'following.html', context)


def autosuggest(request):
    if 'term' in request.GET: 
        search_term = request.GET.get('term')       
        users = User.objects.filter(
            Q(first_name__icontains=search_term) | 
            Q(last_name__icontains=search_term) |
            Q(username__icontains=search_term)
        )
        payload = [
            f"{obj.first_name} {obj.last_name}" 
            for obj in users
        ]
    return JsonResponse(payload, safe=False)


@login_required(login_url='login')
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']   # Person that's following someone else
        user = request.POST['user']   # Person that's being followed
        profile = request.POST.get('profile_id')

        # check if the currently logged in user is already following this user and tries to unfollow
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(
                follower=follower,
                user=user
            )
            delete_follower.delete()
            return redirect('/profile/'+user)
            # if person is not following yet and is trying to follow this person
        else:
            data = {
                'user': user,
                'follower': follower,
                'profile_id': profile,
            }
            new_follower = FollowersCount.objects.create(
                user=data['user'],
                follower=data['follower'],
                profile_id=data['profile_id'],
            )
            new_follower.save()
            return redirect('/profile/'+user)
    else:
        return redirect('dashboard')


@login_required(login_url='login')
def user_post(request, id):
    if request.method == 'POST':
        user = request.user.pk
        user_obj = request.user.username
        video = request.FILES.get('video_upload')
        video_name = request.POST['video_name']
        category_type = request.POST['category_type']
        profile = request.POST['profile_id']

        new_post = Post.objects.create(
            user_id=user,
            user_prof=user_obj,
            profile_id=profile,
            video=video,
            video_name=video_name,
            category_type=category_type
        )
        new_post.save()
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return render(request, 'dashboard')


@login_required(login_url='login')
@require_POST
def post_repost(request):
    original_id = request.POST.get('original_post_id')
    message = (request.POST.get('message') or '').strip()
    if not original_id:
        return HttpResponseBadRequest('missing original_post_id')
    original = get_object_or_404(Post, pk=original_id, status=True)
    # Either create a dedicated Repost model or a Post with type='repost'
    repost = Repost.objects.create(
        user=request.user,
        original=original,
        message=message
    )
    # Optional: bump a repost_count metric on the original
    original.repost_count = (original.repost_count or 0) + 1
    original.save(update_fields=['repost_count'])

    return JsonResponse({
        "ok": True,
        "repost_id": repost.id,
        "original_id": original.id,
        "repost_count": original.repost_count,
    })


@login_required(login_url='login')
def like_post(request, id):
    username = request.user.username
    userid = request.user.pk
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id') 

    # getting the entire object of the post
    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=userid
    ).first()

    # Prevent user from liking their own posts
    if post.user_id == request.user.id:
        raise PermissionDenied
        # messages.info(request, 'You cannot like your own post')
    # if user has not liked any post
    elif like_filter == None:
        new_like = LikePost.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=userid, 
            profile_id=profile
        )
        new_like.save()

        post.no_of_likes = post.no_of_likes+1
        post.save()

        return redirect('dashboard')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()

        return redirect('dashboard')


@login_required(login_url='login')
def flair(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    # getting the entire object of the post
    post = Post.objects.get(id=post_id)

    flair_filter = VideoFlair.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's flair any post
    elif flair_filter == None:
        new_flair = VideoFlair.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_flair.save()

        post.no_of_flair = post.no_of_flair+1
        post.save()
        return redirect('dashboard')
    else:
        flair_filter.delete()
        post.no_of_flair = post.no_of_flair-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def positioning(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    positioning_filter = VideoPositioning.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's positioning 
    elif positioning_filter == 'None':
        new_positioning = VideoPositioning.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_positioning.save()

        post.no_of_positioning = post.no_of_positioning+1
        post.save()
        return redirect('dashboard')
    else:
        positioning_filter.delete()
        post.no_of_positioning = post.no_of_positioning-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def marking(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    marking_filter = VideoMarking.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's marking 
    elif marking_filter == 'None':
        new_marking = VideoMarking.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_marking.save()

        post.no_of_marking = post.no_of_marking+1
        post.save()
        return redirect('dashboard')
    else:
        marking_filter.delete()
        post.no_of_marking = post.no_of_marking-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def anticipation(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    anticipation_filter = VideoAnticipation.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's anticipation 
    elif anticipation_filter == 'None':
        new_anticipation = VideoAnticipation.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_anticipation.save()

        post.no_of_anticipation = post.no_of_anticipation+1
        post.save()
        return redirect('dashboard')
    else:
        anticipation_filter.delete()
        post.no_of_anticipation = post.no_of_anticipation-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def offtheball(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    off_the_ball_filter = OffTheBallVideo.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's off_the_ball 
    elif off_the_ball_filter == 'None':
        new_off_the_ball = OffTheBallVideo.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_off_the_ball.save()

        post.no_of_off_the_ball = post.no_of_off_the_ball+1
        post.save()
        return redirect('dashboard')
    else:
        off_the_ball_filter.delete()
        post.no_of_off_the_ball = post.no_of_off_the_ball-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def tackling(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    tackling_filter = VideoTackling.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's tackling 
    elif tackling_filter == 'None':
        new_tackling = VideoTackling.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_tackling.save()

        post.no_of_tackling = post.no_of_tackling+1
        post.save()
        return redirect('dashboard')
    else:
        tackling_filter.delete()
        post.no_of_tackling = post.no_of_tackling-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def vision(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    vision_filter = VideoVision.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's vision for the ball 
    elif vision_filter == 'None':
        new_vision = VideoVision.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_vision.save()

        post.no_of_vision = post.no_of_vision+1
        post.save()
        return redirect('dashboard')
    else:
        vision_filter.delete()
        post.no_of_vision = post.no_of_vision-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def speed(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    speed_filter = VideoSpeed.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's speed on the ball 
    elif speed_filter == 'None':
        new_speed = VideoSpeed.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_speed.save()

        post.no_of_speed = post.no_of_speed+1
        post.save()
        return redirect('dashboard')
    else:
        speed_filter.delete()
        post.no_of_speed = post.no_of_speed-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def heading(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    heading_filter = VideoHeading.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's heading of the ball 
    elif heading_filter == 'None':
        new_heading = VideoHeading.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_heading.save()

        post.no_of_heading = post.no_of_heading+1
        post.save()
        return redirect('dashboard')
    else:
        heading_filter.delete()
        post.no_of_heading = post.no_of_heading-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def jumping_reach(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    jumping_reach_filter = VideoJumpingReach.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's jumping_reach of the ball 
    elif jumping_reach_filter == 'None':
        new_jumping_reach = VideoJumpingReach.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_jumping_reach.save()

        post.no_of_jumping_reach = post.no_of_jumping_reach+1
        post.save()
        return redirect('dashboard')
    else:
        jumping_reach_filter.delete()
        post.no_of_jumping_reach = post.no_of_jumping_reach-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def work_rate(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    work_rate_filter = VideoWorkRate.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's work rate of the ball 
    elif work_rate_filter == 'None':
        new_work_rate = VideoWorkRate.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_work_rate.save()

        post.no_of_work_rate = post.no_of_work_rate+1
        post.save()
        return redirect('dashboard')
    else:
        work_rate_filter.delete()
        post.no_of_work_rate = post.no_of_work_rate-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def aggression(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    aggression_filter = VideoAggression.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's aggression on the ball 
    elif aggression_filter == 'None':
        new_aggression = VideoAggression.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_aggression.save()

        post.no_of_aggression = post.no_of_aggression+1
        post.save()
        return redirect('dashboard')
    else:
        aggression_filter.delete()
        post.no_of_aggression = post.no_of_aggression-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def charisma(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    charisma_filter = VideoCharisma.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's charisma on the ball 
    elif charisma_filter == 'None':
        new_charisma = VideoCharisma.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_charisma.save()

        post.no_of_charisma = post.no_of_charisma+1
        post.save()
        return redirect('dashboard')
    else:
        charisma_filter.delete()
        post.no_of_charisma = post.no_of_charisma-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def ball_protection(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    ball_protection_filter = VideoBallProtection.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's on the ball protection 
    elif ball_protection_filter == 'None':
        new_ball_protection = VideoBallProtection.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_ball_protection.save()

        post.no_of_ball_protection = post.no_of_ball_protection+1
        post.save()
        return redirect('dashboard')
    else:
        ball_protection_filter.delete()
        post.no_of_ball_protection = post.no_of_ball_protection-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def shooting(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    shooting_filter = VideoShooting.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's shooting of the ball 
    elif shooting_filter == 'None':
        new_shooting = VideoShooting.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_shooting.save()

        post.no_of_shooting = post.no_of_shooting+1
        post.save()
        return redirect('dashboard')
    else:
        shooting_filter.delete()
        post.no_of_shooting = post.no_of_shooting-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def technique(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    technique_filter = VideoTechnique.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's technique on the ball 
    elif technique_filter == 'None':
        new_technique = VideoTechnique.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_technique.save()

        post.no_of_technique = post.no_of_technique+1
        post.save()
        return redirect('dashboard')
    else:
        technique_filter.delete()
        post.no_of_technique = post.no_of_technique-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def passing(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    passing_filter = VideoPassing.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's passing rate of the ball
    elif passing_filter == 'None':
        new_passing = VideoPassing.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_passing.save()

        post.no_of_passing = post.no_of_passing+1
        post.save()
        return redirect('dashboard')
    else:
        passing_filter.delete()
        post.no_of_passing = post.no_of_passing-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def finishing(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    finishing_filter = VideoFinishing.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's passing rate of the ball
    elif finishing_filter == 'None':
        new_passing = VideoFinishing.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_passing.save()

        post.no_of_finishing = post.no_of_finishing+1
        post.save()
        return redirect('dashboard')
    else:
        finishing_filter.delete()
        post.no_of_finishing = post.no_of_finishing-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def ball_control(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    ball_control_filter = VideoBallControl.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's passing rate of the ball
    elif ball_control_filter == 'None':
        new_bal_control = VideoBallControl.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_bal_control.save()

        post.no_of_ball_control = post.no_of_ball_control+1
        post.save()
        return redirect('dashboard')
    else:
        ball_control_filter.delete()
        post.no_of_ball_control = post.no_of_ball_control-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def free_kick(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    free_kick_filter = VideoFreeKick.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's free kick on the ball
    elif free_kick_filter == 'None':
        new_free_kick = VideoFreeKick.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_free_kick.save()

        post.no_of_free_kick = post.no_of_free_kick+1
        post.save()
        return redirect('dashboard')
    else:
        free_kick_filter.delete()
        post.no_of_free_kick = post.no_of_free_kick-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def dribbling(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    dribbling_filter = VideoDribbling.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's dribbling skills of the ball
    elif dribbling_filter == 'None':
        new_free_kick = VideoDribbling.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_free_kick.save()

        post.no_of_dribbling = post.no_of_dribbling+1
        post.save()
        return redirect('dashboard')
    else:
        dribbling_filter.delete()
        post.no_of_dribbling = post.no_of_dribbling-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def crossing(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    crossing_filter = VideoCrossing.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's crossing style of the ball
    elif crossing_filter == 'None':
        new_crossing = VideoCrossing.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_crossing.save()

        post.no_of_crossing = post.no_of_crossing+1
        post.save()
        return redirect('dashboard')
    else:
        crossing_filter.delete()
        post.no_of_crossing = post.no_of_crossing-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def pace(request, id):
    username = request.user.username
    post_id = request.POST.get('post_id')
    profile = request.POST.get('profile_id')
    user_id = request.user.pk

    post = Post.objects.get(id=post_id)
    pace_filter = VideoPace.objects.filter(
        post_id=post_id, 
        username=username, 
        user_id=user_id
    ).first()

    if post.user_id == request.user.id:
        raise PermissionDenied
    # if user has not voted player's pace style of the ball
    elif pace_filter == 'None':
        new_pace = VideoPace.objects.create(
            post_id=post_id, 
            username=username, 
            user_id=user_id, 
            profile_id=profile
        )
        new_pace.save()

        post.no_of_pace = post.no_of_pace+1
        post.save()
        return redirect('dashboard')
    else:
        pace_filter.delete()
        post.no_of_pace = post.no_of_pace-1
        post.save()
        return redirect('dashboard')


@login_required(login_url='login')
def show_notifications(request):
    user_object = User.objects.get(username=request.user.username) 
    user_profile = Profile.objects.get(user=user_object)   
    brand_setting = BrandSetting.objects.all()
    user = request.user
    notifications = Notification.objects.filter(
        user=user
    ).order_by('-created_at')
    notifications.update(is_seen=True)
    year = datetime.now().strftime("%Y")

    context = {
        'notifications': notifications,
        'user_profile': user_profile,
        'brand_setting': brand_setting,
        'year': year
    }

    return render(request, 'notifications.html', context)


@login_required(login_url='login')
def delete_notifications(request, noti_id):
    user = request.user
    Notification.objects.filter(id=noti_id, user=user).delete()
    return redirect('dashboard')


def count_notifications(request):
    count_notifications = None
    if request.user.is_authenticated:
        count_notifications = Notification.objects.filter(
            user=request.user, 
            is_seen=False
        ).count()
    return {'count_notifications': count_notifications}


@login_required(login_url='login')
def user_comments(request, id):
    if request.method == 'POST':
        user = request.user.pk
        user_obj = request.user.username
        body = request.POST.get('comment_body')
        profile = request.POST.get('profile_id')
        post = request.POST.get('post_id')

        user_post = Post.objects.get(id=id)

        if user_post.user_id == request.user.id:
            messages.info(request, 'Access denied')
            return HttpResponseRedirect(reverse('dashboard'))  
        else:            
            Comment.objects.create(
                post_id=post, 
                user_id=user, 
                user_prof=user_obj, 
                profile_id=profile, 
                comment_body=body
            )
            # send_event(
            #     os.getenv('KAFKA_TOPICS["comment_created"]'),
            #     key=str(id),
            #     payload={
            #         "post_id": id, 
            #         "author_id": request.user.id, 
            #         "text": request.POST["body"],
            #         "created_at": now().isoformat()
            #     },
            # )
            # return JsonResponse({"ok": True})        
        return HttpResponseRedirect(reverse('dashboard'))
    else:
        return render(request, 'dashboard')


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def report(request):
    user_object = request.user
    try:
        user_profile = Profile.objects.get(user=user_object)
    except Profile.DoesNotExist:
        user_profile = None
    brand_setting = BrandSetting.objects.all()
    year = datetime.now().strftime("%Y")

    # Handle POST: weekly active users between dates
    if request.method == 'POST':
        from_str = (request.POST.get('from_date') or '').strip()
        to_str = (request.POST.get('to_date') or '').strip()
        weekly_users = 0

        if not from_str or not to_str:
            messages.error(request, "Please provide both From and To dates.")
        else:
            try:
                # Expect YYYY-MM-DD from your UI; make aware bounds
                start = timezone.make_aware(datetime.strptime(from_str, "%Y-%m-%d"))
                # include the whole end day 23:59:59
                end = timezone.make_aware(datetime.strptime(to_str, "%Y-%m-%d")) + timezone.timedelta(days=1)
                weekly_users = (
                    AllLogins.objects
                    .filter(login_date__gte=start, login_date__lt=end)
                    .values('user_id')
                    .distinct()
                    .count()
                )
            except ValueError:
                messages.error(request, "Invalid date format. Use YYYY-MM-DD.")

        context = {
            'weekly_users': weekly_users,
            'user_profile': user_profile,
            'brand_setting': brand_setting,
            'year': year,
            'from_date': from_str,
            'to_date': to_str,
        }
        return render(request, 'report.html', context)

    # GET: full dashboard metrics
    active_users = Profile.objects.count()
    total_posts = Post.objects.count()

    today = timezone.localdate()
    daily_users = (
        AllLogins.objects
        .filter(login_date__date=today)
        .values('user_id')
        .distinct()
        .count()
    )

    # Top 10 most viewed videos (by VideoCounts rows)
    most_viewed = (
        VideoCounts.objects
        .values('post_id', 'post__video_name')
        .annotate(most_watched=Count('id'))
        .order_by('-most_watched')[:10]
    )
    most_viewed_videos = [[item['post_id'], item['post__video_name']] for item in most_viewed]

    # Posts by user and country
    # Use Profile.country_id directly via Post->profile relationship name (Post.profile FK exists)
    posts_by_user_country_qs = (
        Post.objects
        .values('user_prof', 'profile__country_id')
        .annotate(num_posts=Count('id'))
        .order_by('user_prof')
    )
    users = []
    users_posts_counts = []
    users_countries_counts = []
    # Aggregate per user across countries
    from collections import defaultdict
    posts_per_user = defaultdict(int)
    countries_per_user = defaultdict(set)
    for row in posts_by_user_country_qs:
        user = row['user_prof']
        posts_per_user[user] += row['num_posts']
        countries_per_user[user].add(row['profile__country_id'])
    users = list(posts_per_user.keys())
    users_posts_counts = [posts_per_user[u] for u in users]
    users_countries_counts = [len(countries_per_user[u]) for u in users]

    posts_by_user_payload = {
        "labels": users,  # x-axis user names
        "series": [
            {"label": "Posts", "data": users_posts_counts},
            {"label": "Countries", "data": users_countries_counts},
        ],
    }
    posts_by_user = json.dumps(posts_by_user_payload)

    # Profiles by country and type
    prof_qs = (
        Profile.objects
        .values('country_id')
        .annotate(
            user_count=Count('id', filter=Q(profile_type_data='user')),
            player_count=Count('id', filter=Q(profile_type_data='player')),
            agent_count=Count('id', filter=Q(profile_type_data='agent')),
            coach_count=Count('id', filter=Q(profile_type_data='coach')),
        )
        .order_by('country_id')
    )
    countries = [row['country_id'] for row in prof_qs]
    
    profile_payload = {
        "labels": countries,  # x-axis country codes
        "series": [
            {"label": "User", "data": [row['user_count'] for row in prof_qs]},
            {"label": "Player", "data": [row['player_count'] for row in prof_qs]},
            {"label": "Agent", "data": [row['agent_count'] for row in prof_qs]},
            {"label": "Coach", "data": [row['coach_count'] for row in prof_qs]},
        ],
    }
    profile_data = json.dumps(profile_payload)

    category_qs = (
        Post.objects
        .values('user__username')
        .annotate(football_count=Count('id', filter=Q(category_type='football')))
        .order_by('user__username')
    )
    cat_users = [row['user__username'] for row in category_qs]

    posts_by_category_payload = {
        "labels": cat_users,
        "series": [
            {"label": "Football", "data": [row['football_count'] for row in category_qs]},
        ],
    }
    posts_by_category = json.dumps(posts_by_category_payload)

    context = {
        'active_users': active_users,
        'total_posts': total_posts,
        'daily_users': daily_users,
        'most_viewed_videos': most_viewed_videos,
        'posts_by_user': posts_by_user,
        'chart': profile_data,
        'posts_by_category': posts_by_category,
        'user_profile': user_profile,
        'brand_setting': brand_setting,
        'year': year,
    }
    return render(request, 'report.html', context)

# @login_required(login_url='login')
def view_logs(request):
    log_list = ActivityLog.objects.all().values(
        'username', 
        'activity', 
        'ip_address', 
        'url', 
        'user_agent', 
        'created_at'
    )
    # user_object = User.objects.get(username=request.user.username) 
    # user_profile = Profile.objects.get(user=user_object)   
    # brand_setting = BrandSetting.objects.all()

    data = {
        'log_list': list(log_list)
    }
    return JsonResponse({'log_data': data})

   
class LogView(TemplateView):
    template_name = 'view_logs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['log_list'] = ActivityLog.objects.all().order_by('-created_at')    
        return context


@require_GET
def post_counts(request, id):
    post = get_object_or_404(Post, pk=id)
    return JsonResponse({
        "post_id": str(post.id),
        "likes": post.no_of_likes,
        "views": post.video_counts.count(),
        "comments": post.comments.count(),
    })


def forgot_password(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['email']
            user = User.objects.get(email=user)
            token = PasswordResetTokenGenerator().make_token(user)
            mail_managers('password_reset_link', 'password_reset_link', {'user': user, 'token': token}, user.email)
            return redirect('password_reset_sent')
    else:
        form = PasswordResetForm()
    return render(request, 'forgot_password.html', {'form': form})


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()  # sets new password securely
            update_session_auth_hash(request, user)  # prevents logout
            messages.success(request, 'Password changed successfully.')
            return redirect('dashboard')  # or profile/dashboard
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})


@require_GET
def watch(request, pk):
    if request.user.is_authenticated:
        user_object = User.objects.get(username=request.user.username) 
        user_profile = Profile.objects.get(user=user_object) 
        post = get_object_or_404(
            Post.objects.select_related('user').only(
                'id', 'user_id', 'video', 'video_name', 'created_at', 'status'
            ),
            pk=pk
        )
        video = get_object_or_404(Post, id=pk)
        post_lists = Post.objects.filter(id=pk)
        view_count = VideoCounts.objects.filter(post_id=post).count()
        brand_setting = BrandSetting.objects.all()
        year = datetime.now().strftime("%Y")
        if not request.session.session_key:
            request.session.save()
        
        session_key = request.session.session_key   
        ip_address = request.META.get('REMOTE_ADDR', '')
        if post.user_id == request.user.id:
            messages.info(request, 'Access denied')
            return redirect('dashboard')
        else:
            if not VideoCounts.objects.filter(post=video, session=session_key):
                views = VideoCounts(post=video, ip_address=ip_address, session=session_key, user_id=request.user.pk)
                views.save()
    else:
        post_lists = Post.objects.filter(id=pk)
        post = Post.objects.get(id=pk)
        view_count = VideoCounts.objects.filter(post_id=post).count()
        brand_setting = BrandSetting.objects.all() 
        user_profile = Profile.objects.all()
        year = datetime.now().strftime("%Y")

    context = {
        'posts':post,
        'view_count': view_count,
        'postLists': post_lists,
        'brand_setting': brand_setting,
        'user_profile': user_profile,
        'year': year
    }

    return render(request, 'watch.html', context)


@login_required(login_url='login')
def create_stream(request):
    user_object = User.objects.get(username=request.user.username) 
    user_profile = Profile.objects.get(user=user_object)
    if request.method == "POST":
        user = request.POST.get("user_id")
        profile = request.POST.get("profile_id")
        title = request.POST.get("title")
        stream_url = request.POST.get("stream_url")
        is_live = request.POST.get("is_live", "false").lower() == "true"

        # Save the stream to the database
        stream = LiveStream.objects.create(
            user=user,
            profile=profile,
            title=title,
            stream_url=stream_url,
            is_live=is_live
        )
        stream.save()
    context = {
        'user_profile': user_profile,
    }
        # return JsonResponse({"message": "Stream created successfully", "stream_id": stream.id})
    return render(request, 'live.html', context)


def stream_view(request, stream_id):
    stream = get_object_or_404(LiveStream, id=stream_id, is_live=True)
    return render(request, 'stream.html', {'stream': stream})


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # e.g., "client, proxy1, proxy2"
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@require_GET
def ad_slot(request, placement_code: str):
    selection = select_creative(
        placement_code,
        user=request.user if request.user.is_authenticated else None,
        ip=_client_ip(request),
    )
    if not selection:
        return HttpResponse()

    placement, campaign, creative = selection

    with transaction.atomic():
        impression = AdImpression.objects.create(
            campaign=campaign,
            creative=creative,
            placement=placement,
            user=request.user if request.user.is_authenticated else None,
            ip=_client_ip(request),
            user_agent=(request.META.get("HTTP_USER_AGENT") or "")[:500],
        )

    # Render HTML safely; allow custom creative.html if you trust its source
    if creative.html:
        # Optional: sanitize/whitelist if creatives are user-submitted
        html = creative.html
    else:
        headline = escape(creative.headline or "")
        img_src = creative.image.url if creative.image else ""
        html = (
            f'<a href="/ads/click/{impression.id}/" target="_blank" rel="noopener nofollow">'
            f'  <img src="{img_src}" alt="{headline}" style="max-width:100%;height:auto;" />'
            f'</a>'
        )

    payload = {
        "impression_id": impression.id,
        "html": html,
    }
    return JsonResponse(payload)


@require_GET
def ad_click(request, impression_id: int):
    impression = get_object_or_404(AdImpression, id=impression_id)
    # Basic duplicate click protection: one click per impression per IP in quick succession could be checked
    AdClick.objects.create(impression=impression)
    return redirect(impression.creative.click_url)