import uuid

from django.shortcuts import get_object_or_404
from django_filters import rest_framework as dfilters
from rest_framework import filters, permissions, status, views, viewsets
from rest_framework.response import Response
from reviews.models import Category, Genre, Review, Title, User

from api.mixins import CreateListDestroyViewSet
from api.permissions import (AuthorModAdminOrReadOnly,
                             SuperuserAdminOrReadOnly, SuperuserOrAdminOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenreSerializer, ReviewSerializer,
                             TitleReadSerializer, TitleWriteSerializer,
                             UserOwnSettingsSerializer,
                             UserRegistrationSerializer, UserSerializer)
from api.utils import get_tokens_for_user


class TitleFilter(dfilters.FilterSet):
    """ Фильтр для поиска произведений через query parameters. """
    genre = dfilters.CharFilter(field_name='genre__slug')
    category = dfilters.CharFilter(field_name='category__slug')
    name = dfilters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'name', 'year',)


class CategoryViewSet(CreateListDestroyViewSet):
    """ Вьюсет для категорий произведений. """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer
    permission_classes = (SuperuserAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(CreateListDestroyViewSet):
    """ Вьюсет для жанров произведений. """
    queryset = Genre.objects.all().order_by('name')
    serializer_class = GenreSerializer
    permission_classes = (SuperuserAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """ Вьюсет для художественных произведений. """
    queryset = Title.objects.all().order_by('-year')
    permission_classes = (SuperuserAdminOrReadOnly,)
    filter_backends = (dfilters.DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitleWriteSerializer
        return TitleReadSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ Вьюсет для отзывов на произведения. """
    serializer_class = ReviewSerializer
    permission_classes = (AuthorModAdminOrReadOnly,)

    def get_queryset(self):
        """ Принимает URL-ID произведения и берёт queryset его отзывов. """
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all().order_by('-pub_date')

    def perform_create(self, serializer):
        """ Передаёт в сериализатор произведение и автора. """
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(title=title, author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ Вьюсет для комментариев к отзывам. """
    serializer_class = CommentSerializer
    permission_classes = (AuthorModAdminOrReadOnly,)

    def get_queryset(self):
        """ Принимает URL-ID отзыва и берёт queryset его комментов. """
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all().order_by('-pub_date')

    def perform_create(self, serializer):
        """ Гарантирует авторство комментария. """
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(review=review, author=self.request.user)


class UserRegistrationView(views.APIView):
    """ Вью-класс для регистрации пользователя. """
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserTokenView(views.APIView):
    """ Вью-класс для выдачи JWT-токенов пользователям. """
    def post(self, request):
        if not request.data.get('username'):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, username=request.data.get('username'))
        if user.confirmation_code == request.data.get('confirmation_code'):
            user.confirmation_code = str(uuid.uuid4())
            token = get_tokens_for_user(user)
            user.save()
            return Response(token, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """ Вьюсет управления пользователями для админа. """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    permission_classes = (SuperuserOrAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)


class UserSettingsView(views.APIView):
    """ Вьюсет управления профилем для пользователя (/me). """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserOwnSettingsSerializer(user)
        return Response(serializer.data)

    def patch(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserOwnSettingsSerializer(
            user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
