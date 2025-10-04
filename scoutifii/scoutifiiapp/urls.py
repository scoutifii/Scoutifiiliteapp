from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('signup', views.signup, name='signup'), 
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('settings', views.settings, name='settings'),
    path('like-post/<uuid:id>', views.like_post, name='like-post'),
    path('profile/<str:pk>', views.profile, name='profile'),
    path('follower/<str:pk>', views.follower, name='follower'),
    path('following/<str:pk>', views.following, name='following'),
    path('follow', views.follow, name='follow'),
    path('user-post/<str:id>', views.user_post, name='user-post'),
    path('report', views.report, name='report'),
    path('notifications', views.show_notifications, name='notifications'),
    path('search', views.search, name='search'),
    path('flair/<str:id>', views.flair, name='flair'),
    path('positioning/<str:id>', views.positioning, name='positioning'),
    path('marking/<str:id>', views.marking, name='marking'),
    path('anticipation/<str:id>', views.anticipation, name='anticipation'),
    path('offtheball/<str:id>', views.offtheball, name='offtheball'),
    path('tackling/<str:id>', views.tackling, name='tackling'),
    path('vision/<str:id>', views.vision, name='vision'),
    path('speed/<str:id>', views.speed, name='speed'),
    path('heading/<str:id>', views.heading, name='heading'),
    path('jumpingreach/<str:id>', views.jumping_reach, name='jumpingreach'),
    path('workrate/<str:id>', views.work_rate, name='workrate'),
    path('aggression/<str:id>', views.aggression, name='aggression'),
    path('charisma/<str:id>', views.charisma, name='charisma'),
    path('ballprotection/<str:id>', views.ball_protection, name='ballprotection'),
    path('shooting/<str:id>', views.shooting, name='shooting'),
    path('technique/<str:id>', views.technique, name='technique'),
    path('passing/<str:id>', views.passing, name='passing'),
    path('finishing/<str:id>', views.finishing, name='finishing'),
    path('ballcontrol/<str:id>', views.ball_control, name='ballcontrol'),
    path('freekick/<str:id>', views.free_kick, name='freekick'),
    path('dribbling/<str:id>', views.dribbling, name='dribbling'),
    path('crossing/<str:id>', views.crossing, name='crossing'),
    path('pace/<str:id>', views.pace, name='pace'),
    path('user-comments/<str:id>', views.user_comments, name='user-comments'),
    path('autosuggest', views.autosuggest, name='autosuggest'),
    path('log', views.view_logs, name='log'),
    path('logs', views.LogView.as_view(template_name='view_logs.html'), name='logs'),
    path('post/<uuid:id>', views.post_counts, name='post-counts'),
    path('post-repost', views.post_repost, name='post-repost'),
    path('forgot-password', views.forgot_password, name='forgot-password'),
    path('watchqv=<str:pk>', views.watch, name='watch'),
    path('<str:pk>/follower', views.follower, name='follower'),
    path('<str:pk>/following', views.following, name='following'),
    path('password-reset/sent/',
         TemplateView.as_view(template_name='password_reset_sent.html'),
         name='password_reset_sent'),
    path('password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='forgot_password.html',
            email_template_name='emails/password_reset_email.html',
            subject_template_name='emails/password_reset_subject.txt',
            success_url='/password-reset/done/'
        ),
        name='password_reset'),
    path('password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url='/reset/done/'
        ),
        name='password_reset_confirm'),
    path('reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ),
        name='password_reset_complete'),
]
