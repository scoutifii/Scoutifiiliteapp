import graphene
from graphene_django.types import DjangoObjectType
from .models import Profile, Post, Comment, Notification, FollowersCount
from django.contrib.auth.models import User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class ProfileType(DjangoObjectType):
    class Meta:
        model = Profile
        fields = ('id', 'user', 'bio', 'location', 'phone_no')

    user = graphene.Field(UserType)

    def resolve_user(self, info):
        return self.user


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = (
            'id', 
            'user_prof', 
            'video_name', 
            'no_of_likes', 
            'category_type', 
            'created_at'
        )


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = (
            'id', 
            'user_prof', 
            'post', 
            'user', 
            'comment_body', 
            'created_at'
        )


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = (
            'id', 
            'notification_type', 
            'user', 
            'text_preview', 
            'is_seen', 
            'created_at'
        )


class FollowersCountType(DjangoObjectType):
    class Meta:
        model = FollowersCount
        fields = ('id', 'follower', 'user', 'created_at', 'status')


class Query(graphene.ObjectType):
    all_profiles = graphene.List(ProfileType)
    # User and Profile APIs
    user_profile = graphene.Field(
        ProfileType, 
        username=graphene.String(required=True))
   
    # Post APIs
    all_posts = graphene.List(PostType)
    posts_by_user = graphene.List(
        PostType, 
        user_id=graphene.Int(required=True))

    # Comment APIs
    comments_by_post = graphene.List(
        CommentType, 
        post_id=graphene.String(required=True))

    # Notification APIs
    notifications_by_user = graphene.List(
        NotificationType, 
        user_id=graphene.Int(required=True))

    # Follower/Following APIs
    followers = graphene.List(
        FollowersCountType, 
        user_id=graphene.Int(required=True))
    following = graphene.List(
        FollowersCountType, 
        user_id=graphene.Int(required=True))

    # Search APIs
    search_users = graphene.List(
        ProfileType, 
        query=graphene.String(required=True))

    # Define resolvers
    def resolve_user_profile(self, info, username):
        try:
            return Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return None

    def resolve_all_profiles(self, info):
        return Profile.objects.all()

    def resolve_all_posts(self, info):
        return Post.objects.all()

    def resolve_posts_by_user(self, info, user_id):
        return Post.objects.filter(user_id=user_id)

    def resolve_comments_by_post(self, info, post_id):
        return Comment.objects.filter(post_id=post_id)

    def resolve_notifications_by_user(self, info, user_id):
        return Notification.objects.filter(user_id=user_id)

    def resolve_followers(self, info, user_id):
        return FollowersCount.objects.filter(followed=user_id)

    def resolve_following(self, info, user_id):
        return FollowersCount.objects.filter(follower=user_id)

    def resolve_search_users(self, info, query):
        return Profile.objects.filter(user__username__icontains=query)


# Define Mutations

class FollowUser(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, user_id):
        user = info.context.user
        if not user.is_authenticated:
            return FollowUser(
                success=False, 
                message="Authentication required.")
        followed_user = Profile.objects.get(user_id=user_id)
        FollowersCount.objects.create(
            follower=user, 
            followed=followed_user.user)
        return FollowUser(success=True, message="User followed successfully.")


class CreatePost(graphene.Mutation):
    class Arguments:
        video_name = graphene.String(required=True)
        category_type = graphene.String(required=True)
        video_url = graphene.String(required=True)

    post = graphene.Field(PostType)

    def mutate(self, info, video_name, category_type, video_url):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication required.")
        post = Post.objects.create(
            user=user,
            video_name=video_name,
            category_type=category_type,
            video=video_url,
        )
        return CreatePost(post=post)


class Mutation(graphene.ObjectType):
    follow_user = FollowUser.Field()
    create_post = CreatePost.Field()

# Combine Queries and Mutations into Schema


schema = graphene.Schema(query=Query, mutation=Mutation)