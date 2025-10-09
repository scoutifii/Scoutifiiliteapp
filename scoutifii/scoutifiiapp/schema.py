import graphene
from graphene_django.types import DjangoObjectType
from .models import Profile, Post
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
        fields = ('id', 'user_prof', 'video_name', 'created_at')

class Query(graphene.ObjectType):
    all_profiles = graphene.List(ProfileType)
    all_posts = graphene.List(PostType)

    def resolve_all_profiles(root, info):
        return Profile.objects.all()

    def resolve_all_posts(root, info):
        return Post.objects.all()

schema = graphene.Schema(query=Query)