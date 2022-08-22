from django.urls import include, path
from rest_framework import routers

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    TitleViewSet,
    UserRegistrationView,
    UserTokenView,
    UserViewSet,
    UserSettingsView
)

app_name = 'api'

router = routers.DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('genres', GenreViewSet)
router.register('titles', TitleViewSet)
router.register(
    r'titles/(?P<title_id>[\d]+)/reviews',
    ReviewViewSet, basename='review')
router.register(
    r'titles/(?P<title_id>[\d]+)/reviews/(?P<review_id>[\d]+)/comments',
    CommentViewSet, basename='comment')
router.register('users', UserViewSet)


urlpatterns = [
    path('v1/auth/signup/', UserRegistrationView.as_view(), name='users_auth'),
    path('v1/auth/token/', UserTokenView.as_view(), name='token_obtain_pair'),
    path(
        'v1/users/me/',
        UserSettingsView.as_view(),
        name='token_refresh'),
    path('v1/', include(router.urls)),
]
