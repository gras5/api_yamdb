import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from reviews.models import (Category, Genre, Title, User,
                            GenreTitle, Review, Comment)

CSV_MODEL = {
    'users': User,
    'category': Category,
    'genre': Genre,
    'titles': Title,
    'genre_title': GenreTitle,
    'review': Review,
    'comments': Comment,
}
DIR = settings.BASE_DIR


class Command(BaseCommand):
    help = 'Loads data to database from csv files'

    def handle(self, *args, **options):
        for csv_name in CSV_MODEL:
            with open(
                DIR + f'/static/data/{csv_name}.csv',
                'r',
                encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file, delimiter=",")
                for row in reader:
                    CSV_MODEL[csv_name].objects.get_or_create(**row)
