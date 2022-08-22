import datetime as dt
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Genre, Title, Review, Comment, User
from .utils import send_confirm_mail
from .validators import MeNameNotInUsername


class CategorySerializer(serializers.ModelSerializer):
    """ Сериализатор категорий. """
    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """ Сериализатор жанров. """
    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleWriteSerializer(serializers.ModelSerializer):
    """ Сериализатор для POST/PATCH-запросов произведений. """
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category',)

    def validate_year(self, value):
        year = dt.date.today().year
        if value > year:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, '
                'которые еще не вышли!'
            )
        return value

    def get_rating(self, obj):
        """ Рассчитывает усреднённый рейтинг по оценкам произведения. """
        reviews = Review.objects.filter(title=obj.pk)
        if not reviews.exists():
            return None
        average = reviews.aggregate(avg_rating=models.Avg('score'))
        return int(round(average['avg_rating']))


class TitleReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для GET-запросов произведений. """
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating',
            'description', 'genre', 'category',)

    def get_rating(self, obj):
        """ Рассчитывает усреднённый рейтинг по оценкам произведения. """
        reviews = Review.objects.filter(title=obj.pk)
        if not reviews.exists():
            return None
        average = reviews.aggregate(avg_rating=models.Avg('score'))
        return int(round(average['avg_rating']))


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        title = self.context['request'].parser_context['kwargs']['title_id']
        duplicate = Review.objects.filter(
            author=self.context['request'].user,
            title=title)
        if self.context['request'].method != 'PATCH' and duplicate.exists():
            raise ValidationError('Уже оставляли отзыв на это произведение.')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MeNameNotInUsername()
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')

        if not User.objects.filter(email=email).exists():
            validated_data['confirmation_code'] = str(uuid.uuid4())
            user = User.objects.create(**validated_data)
        else:
            user = User.objects.get(email=email)
            if user.username != username:
                raise serializers.ValidationError(
                    (
                        f'Аккаунт с {email} уже зарегистрирован. '
                        'Пожалуйста используйте корректный username.'
                    )
                )
            user.save()
        send_confirm_mail(user)
        return user


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор профилей пользователя. """
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MeNameNotInUsername()
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)


class UserOwnSettingsSerializer(serializers.ModelSerializer):
    """ Сериализатор для личного кабинета пользователя. """
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            MeNameNotInUsername()
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def update(self, instance, validated_data):
        if (instance.role == 'user') and ('role' in validated_data):
            validated_data['role'] = 'user'
        return super().update(instance, validated_data)
