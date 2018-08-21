import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from mixer.backend.django import mixer
from posts.models import Post, Like
from simple_api.bot_settings import (
    number_of_users,
    max_posts_per_user,
    max_likes_per_user
)


User = get_user_model()


class Command(BaseCommand):
    help = 'create test data'

    def handle(self, *args, **options):
        # create users
        users = mixer.cycle(number_of_users).blend(User)
        all_posts = []
        # create posts for each user
        for user in users:
            posts = mixer.cycle(random.randint(1, max_posts_per_user)).blend(Post, user=user, content=mixer.RANDOM)
            all_posts += posts
        # user likes some posts
        for user in users:
            number_of_likes = random.randint(1, max_likes_per_user)
            random.shuffle(all_posts)
            likes = mixer.cycle(number_of_likes).blend(Like, user=user, post=(post for post in all_posts[:number_of_likes]))

