from django.contrib import admin
from django.utils.text import Truncator

from .models import Category, Genre, Title, Review, Comment, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'shortened_bio',
        'role',
        'confirmation_code',
    )
    list_editable = ('role',)
    search_fields = ('first_name', 'last_name', 'username',)
    list_filter = ('role',)
    list_display_links = ('pk', 'username',)
    empty_value_display = 'n/a'

    def shortened_bio(self, User):
        return Truncator(User.bio).chars(200)
    shortened_bio.short_description = 'Биография'


@admin.register(Category)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_display_links = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    list_display_links = ('name',)


@admin.register(Title)
class TitlesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year', 'category')
    list_display_links = ('name',)
    list_filter = ('category', 'genre')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'text', 'author', 'score')
    list_display_links = ('pk',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'review_id', 'text')
    list_display_links = ('pk',)

    def review_id(self, Review):
        return Review.pk
    review_id.short_description = 'ID отзыва'
