from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class User(AbstractUser):
    """ Кастом-модель пользователя. """
    USER_ROLES = (
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь'),
    )

    role = models.CharField(
        max_length=15,
        choices=USER_ROLES,
        default='user'
    )
    bio = models.TextField(blank=True)
    confirmation_code = models.CharField(max_length=254)

    class Meta:
        ordering = ('username',)

    def is_user_role(self):
        """ Метод вывода прав доступа пользователя. """
        return self.role == self.USER_ROLES[2][0]

    def is_moder_role(self):
        """ Метод вывода прав доступа пользователя. """
        return self.role == self.USER_ROLES[1][0]

    def is_admin_role(self):
        """ Метод вывода прав доступа пользователя. """
        return self.role == self.USER_ROLES[0][0]


class Category(models.Model):
    """ Модель категорий худ. произведений. """
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """ Модель жанров худ. произведений. """
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    """ Модель произведений (фильмов, книг). """
    name = models.CharField(max_length=200)
    year = models.IntegerField()
    rating = models.IntegerField('Рейтинг', blank=True, null=True)
    description = models.TextField('Описание', blank=True, null=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='category',
        blank=True,
        null=True,
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """ Through-модель для жанров/произведений. """
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    """ Модель для отзывов на произведения. """
    title = models.ForeignKey(
        Title, related_name='reviews', on_delete=models.CASCADE)
    text = models.TextField('Текст отзыва', max_length=6000)
    author = models.ForeignKey(
        User, related_name='reviews', on_delete=models.CASCADE)
    score = models.IntegerField(
        'Оценка', blank=True, null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(
                       fields=('author', 'title'),
                       name='unique_review')]


class Comment(models.Model):
    """ Модель для комментариев к отзывам на произведения. """
    review = models.ForeignKey(
        Review, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField('Комментарий', max_length=2000)
    author = models.ForeignKey(
        User, related_name='comments', on_delete=models.CASCADE)
    pub_date = models.DateTimeField('Дата', auto_now_add=True)
