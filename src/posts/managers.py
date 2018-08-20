from django.db import models


class PostManager(models.Manager):
    def get_active_posts(self):
        return self.filter(is_published=True)
