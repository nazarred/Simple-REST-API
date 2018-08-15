def post_likes_increment(sender, instance, **kwargs):
    instance.post.increment_likes()


def post_likes_decrement(sender, instance, **kwargs):
    instance.post.decrement_likes()
