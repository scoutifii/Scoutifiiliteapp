from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from .helper import (
    validate_image_file_extension, 
    validate_image_file_size, 
    validate_video_file_extension, 
    validate_video_file_size,
    validate_video_mime,
    validate_image_mime,
    VideoStorage
)
import uuid
from datetime import date
videos_storage = VideoStorage()


class AllLogins(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    login_date = models.DateTimeField(auto_now_add=True)
    last_logged_out = models.DateTimeField(null=True, blank=True)
    ip_address = models.CharField(max_length=100, default=0, blank=True)
    server = models.CharField(max_length=100, default=0, blank=True)
    user_agent = models.CharField(max_length=255, default=0, blank=True)
    device_type = models.CharField(max_length=100, default=0, blank=True)
    browser = models.CharField(max_length=100, default=0, blank=True)

    class Meta:
        db_table = "all_logins"

    def __str__(self):
        return str(self.user) + ':' + str(self.login_date)


class Profile(models.Model):
    PROFILE_TYPES = (
        ("user", 'User'), 
        ("player", 'Player'), 
        ("coach", 'Coach'), 
        ("agent", 'Agent')
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )   # Foreign key of currently logged in user
    id_user = models.IntegerField()   # Primary key of profile
    bio = models.TextField(blank=True)
    profileimg = models.ImageField(
        upload_to='profile_images', 
        default='default-user.png', 
        validators=[
            validate_image_file_extension, 
            validate_image_file_size,
            validate_image_mime
        ], 
        blank=True
    )
    location = models.CharField(max_length=100, blank=True)
    phone_no = PhoneNumberField(
        unique=True, 
        max_length=13, 
        null=False, 
        blank=False
    )
    forgot_password_token = models.CharField(max_length=100)
    country_id = CountryField()
    profile_type_data = models.CharField(default="user", max_length=10)
    birth_date = models.DateField(null=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "profile"
    
    def __str__(self):
        return self.user.username


class BrandSetting(models.Model):
    brand_name = models.CharField(max_length=100)
    brand_title = models.CharField(max_length=100)
    language = models.CharField(max_length=100)
    time_zone = models.CharField(max_length=100)
    brand_logo = models.ImageField(upload_to='brand_images')
    favicon_icon = models.ImageField(upload_to='brand_images')
    brand_footer = models.CharField(max_length=1000)
    brand_slogan = models.CharField(max_length=50, null=True)
    about = models.TextField()
    google_analytics = models.CharField(max_length=100)
    contact = models.CharField(max_length=50)
    website = models.URLField()
    location = models.CharField(max_length=255)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "brand_setting"

    def __str__(self):
        return self.brand_name


class Post(models.Model):
    POST_CATEGORY = (
        ("football", 'Football'), 
        ("netball", 'Netball'), 
        ("basketball", 'Basketball'), 
        ("volleyball", 'Volleyball'), 
        ("athletics", 'Athletics'), 
        ("boxing", 'Boxing')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uuid = models.CharField(max_length=255, blank=True, null=True)
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='posts'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_prof = models.CharField(max_length=100, blank=True, null=True)
    video = models.FileField(
        storage=VideoStorage, 
        upload_to='%Y/%m/%d',
        blank=True, 
        null=True,
        validators=[
            validate_video_file_extension, 
            validate_video_file_size, 
            validate_video_mime
        ],
    )
    video_name = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(blank=True, null=True, unique=True)
    category_type = models.CharField(
        choices=POST_CATEGORY, 
        max_length=50, 
        null=True
    )
    no_of_likes = models.IntegerField(default=0)
    no_of_views = models.IntegerField(default=0)
    no_of_flair = models.IntegerField(default=0)
    no_of_off_the_ball = models.IntegerField(default=0)
    no_of_positioning = models.IntegerField(default=0)
    no_of_marking = models.IntegerField(default=0)
    no_of_anticipation = models.IntegerField(default=0)
    no_of_pace = models.IntegerField(default=0)
    no_of_tackling = models.IntegerField(default=0)
    no_of_vision = models.IntegerField(default=0)
    no_of_work_rate = models.IntegerField(default=0)
    no_of_aggression = models.IntegerField(default=0)
    no_of_charisma = models.IntegerField(default=0)
    no_of_ball_protection = models.IntegerField(default=0)
    no_of_speed = models.IntegerField(default=0)
    no_of_heading = models.IntegerField(default=0)
    no_of_jumping_reach = models.IntegerField(default=0)
    no_of_shooting = models.IntegerField(default=0)
    no_of_technique = models.IntegerField(default=0)
    no_of_passing = models.IntegerField(default=0)
    no_of_finishing = models.IntegerField(default=0)
    no_of_ball_control = models.IntegerField(default=0)
    no_of_free_kick = models.IntegerField(default=0)
    no_of_dribbling = models.IntegerField(default=0)
    no_of_crossing = models.IntegerField(default=0)
    no_of_concentration = models.IntegerField(default=0)
    no_of_agility = models.IntegerField(default=0)
    no_of_reflexes = models.IntegerField(default=0)
    no_of_saving_penalties = models.IntegerField(default=0)
    no_of_footwork_and_distribution = models.IntegerField(default=0)
    no_of_commanding_in_defence = models.IntegerField(default=0)
    no_of_saving_one_on_one = models.IntegerField(default=0)
    no_of_handling = models.IntegerField(default=0)
    no_of_aerial_ability = models.IntegerField(default=0)
    no_of_close_range_shot_stopping_ability = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)
    repost_count = models.IntegerField(default=0)

    class Meta:
        db_table = "post"
        db_tablespace = "post_tablespace"
        indexes = [
            models.Index(
                fields=['video_name'], 
                name='post_video_name_idx', 
                db_tablespace='post_tablespace'
            ),
        ]

    def __str__(self):
        return f"{self.user}, {self.profile.country_id}"

    def get_timeago(self):
        from .helper import timeago
        return timeago(self)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        default=None, 
        related_name="comments"
    )
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        default=None
    )
    user_prof = models.CharField(max_length=50, blank=True, default=None)
    comment_body = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "comments"
        db_tablespace = "comment_tablespace"
        indexes = [
            models.Index(
                fields=['post'], 
                name='comment_idx', 
                db_tablespace='comment_tablespace'
            ),
        ]

    def __str__(self):
        return '%s - %s' % (self.post.video_name, self.comment_body)

    def get_timeago(self):
        from .helper import timeago
        return timeago(self)


class LikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name="like_post"
    )
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "like_post"
        db_tablespace = "likepost_tablespace"
        indexes = [
            models.Index(
                fields=['post'], 
                name='likepost_idx', 
                db_tablespace='likepost_tablespace'
            ),
        ]

    def __str__(self):
        return self.username


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        (1, 'Like'), 
        (2, 'Comment'), 
        (3, 'Follow'), 
        (4, 'Voted'), 
        (5, 'Viewed')
    )
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name="+", 
        blank=True, 
        null=True
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="noti_from_user", 
        null=True
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="noti_to_user", 
        null=True
    )
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name="profiles", 
        default=''
    )
    notification_type = models.IntegerField(choices=NOTIFICATION_TYPES)
    text_preview = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        db_table = "notifications"
        db_tablespace = "notification_tablespace"

    def __str__(self):
        return f"{self.post}"

    def get_timeago(self):
        from .helper import timeago
        return timeago(self)


class VideoCounts(models.Model):
    post = models.ForeignKey(
        Post, 
        related_name='video_counts', 
        on_delete=models.CASCADE
    )
    ip_address = models.GenericIPAddressField(
        max_length=15, 
        default="127.0.0.1"
    )
    session = models.CharField(max_length=50)
    user = models.ForeignKey(
        User, 
        related_name='users', 
        on_delete=models.CASCADE, 
        null=True
    )
    profile = models.ForeignKey(
        Profile, 
        related_name='video_counts', 
        on_delete=models.CASCADE, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "video_counts"

    def __str__(self):
        return f'{0} in {1} post'.format(self.ip_address, self.post.video_name)


class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)
    profile = models.ForeignKey(
        'Profile', 
        on_delete=models.CASCADE, 
        null=True, 
        related_name="followers_count"
    )
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "followers_count"
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'user'], 
                name='unique_follow_pair'
            ),
        ]

    def __str__(self):
        return self.user


class OffTheBallVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "off_the_ball"

    def __str__(self):
        return self.username


class VideoPositioning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "positioning"

    def __str__(self):
        return self.username


class VideoMarking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "marking"

    def __str__(self):
        return self.username


class VideoAnticipation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "anticipation"

    def __str__(self):
        return self.username


class VideoPace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "pace"

    def __str__(self):
        return self.username


class VideoTackling(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tackling"

    def __str__(self):
        return self.username


class VideoVision(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "vision"

    def __str__(self):
        return self.username


class VideoWorkRate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "work_rate"

    def __str__(self):
        return self.username


class VideoAggression(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "aggression"

    def __str__(self):
        return self.username


class VideoCharisma(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "charisma"

    def __str__(self):
        return self.username


class VideoBallProtection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ball_protection"

    def __str__(self):
        return self.username


class VideoSpeed(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "speed"

    def __str__(self):
        return self.username


class VideoHeading(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "heading"

    def __str__(self):
        return self.username


class VideoFlair(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "flair"

    def __str__(self):
        return self.username


class VideoJumpingReach(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "jumping_reach"

    def __str__(self):
        return self.username


class VideoShooting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shooting"

    def __str__(self):
        return self.username


class VideoTechnique(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "technique"

    def __str__(self):
        return self.username


class VideoPassing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "passing"

    def __str__(self):
        return self.username


class VideoFinishing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "finishing"

    def __str__(self):
        return self.username


class VideoBallControl(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ball_control"

    def __str__(self):
        return self.username


class VideoFreeKick(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "free_kick"

    def __str__(self):
        return self.username


class VideoDribbling(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "dribbling"

    def __str__(self):
        return self.username


class VideoCrossing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "crossing"

    def __str__(self):
        return self.username


class VideoSavingOneOnOne(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saving_one_on_one"

    def __str__(self):
        return self.username


class VideoCommandingInDefence(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "commanding_in_defence"

    def __str__(self):
        return self.username


class VideoFootworkAndDistribution(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "footwork_and_distribution"

    def __str__(self):
        return self.username


class VideoSavingPenalties(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "saving_penalties"

    def __str__(self):
        return self.username


class VideoConcentration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "concentration"

    def __str__(self):
        return self.username


class VideoAgility(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "agility"

    def __str__(self):
        return self.username


class VideoCloseRangeShotStoppingAbility(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "close_range_shot_stopping_ability"

    def __str__(self):
        return self.username


class VideoReflexes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reflexes"

    def __str__(self):
        return self.username


class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    username = models.CharField(max_length=100, null=True)
    activity = models.CharField(max_length=1000)
    ip_address = models.CharField(max_length=100)
    url = models.CharField(max_length=100)
    user_agent = models.CharField(max_length=1000, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "activity_log"

    def __str__(self):
        return '%s - %s' % (self.activity, self.created_at) 

    # JSON
    def get_data(self):
        return {
            'user': self.user_id,
            'username': self.username,
            'activity': self.activity,
            'ip_address': self.ip_address,
            'url': self.url,
            'user_agent': self.user_agent,
            'created_at': self.created_at,
        }


class Plan(models.Model):
    code = models.CharField(max_length=30, unique=True)  # free, plus, pro
    name = models.CharField(max_length=64, unique=True)
    price_cents = models.PositiveIntegerField(default=0)  # monthly
    currency = models.CharField(max_length=8, default="USD")
    max_uploads_per_day = models.PositiveIntegerField(null=True, blank=True)
    max_bytes_per_day = models.BigIntegerField(null=True, blank=True)
    soft_limit = models.BooleanField(default=False)  # allow overage but bill later
    overage_price_cents_per_upload = models.PositiveIntegerField(null=True, blank=True)
    overage_price_cents_per_gb = models.PositiveIntegerField(null=True, blank=True)
    features = models.JSONField(default=dict)

    class Meta:
        db_table = "plan"
    
    def __str__(self):
        return '%s - %s' % (self.code, self.name)


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    stripe_customer_id = models.CharField(max_length=120, blank=True, default="")
    stripe_sub_id = models.CharField(max_length=120, blank=True, default="")
    status = models.CharField(max_length=30, default="active")  # active, past_due, canceled
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    seats = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "subscription"
    
    def __str__(self):
        return '%s - %s' % (self.user, self.plan)

class UsageQuota(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    period_start = models.DateField()
    uploads = models.PositiveIntegerField(default=0)
    bytes_uploaded = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "usage_quota"
        unique_together = ("user", "period_start")
    
    def __str__(self):
        return f"(self.user, self.period_start, self.bytes_uploaded)"


class OverageEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    type = models.CharField(max_length=32)  # "upload" or "bytes"
    quantity = models.BigIntegerField()     # count or bytes
    unit_price_cents = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def record_overage(user, over_uploads: int = 0, over_bytes: int = 0):
        overage_event = OverageEvent(
            user=user,
            date=date.today(),
            type="upload",
            quantity=over_uploads,
            unit_price_cents=user.plan.overage_price_cents_per_upload,
        )
        overage_event.save()


class Repost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reposts')
    profile = models.ForeignKey(
        'Profile', 
        on_delete=models.CASCADE, 
        related_name='reposts',
        null=True
    )
    original = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='reposts')
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "repost"
        db_tablespace = "repost_tablespace"
    
    def __str__(self):
        return f"{self.user} - {self.original} - {self.message}"

