from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete

from .signals_handlers import post_likes_decrement, post_likes_increment


class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    title = models.CharField(max_length=120)
    number_of_likes = models.IntegerField()
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def increment_likes(self):
        self.number_of_likes += 1
        self.save()

    def decrement_likes(self):
        self.number_of_likes -= 1
        self.save()

    def get_users_who_liked(self):
        return self.likes.all()

    def __str__(self):
        return self.title


class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='likes')
    post = models.ForeignKey(Post, related_name='likes')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


post_save.connect(post_likes_increment, sender=Like)


post_delete.connect(post_likes_decrement, sender=Like)
