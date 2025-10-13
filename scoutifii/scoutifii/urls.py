from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from graphene_django.views import GraphQLView
from django_ratelimit.decorators import ratelimit


@ratelimit(key="ip", rate="10/m", block=True)  # Limit to 10 requests per minute per IP
def graphql_view(request, *args, **kwargs):
    return GraphQLView.as_view(graphiql=True)(request, *args, **kwargs)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('scoutifiiapp.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.VIDEOS_URL, document_root=settings.VIDEOS_ROOT)
urlpatterns += [
    path("graphql/", graphql_view),
]
