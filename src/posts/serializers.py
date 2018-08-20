from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField
)

from accounts.serializers import UserDetailSerializer
from posts.models import Post


class LikeListSerializer(ModelSerializer):
    user = UserDetailSerializer()

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
        ]


class PostCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'title',
            'content',
            'is_published'
        ]


class PostDetailSerializer(ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    likes = LikeListSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'title',
            'content',
            'number_of_likes',
            'likes',
            'is_published',
            'updated',
            'timestamp'
        ]

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(PostDetailSerializer, self).__init__(*args, **kwargs)
        show_who_liked = self.context['request'].GET.get('likes')
        if not show_who_liked == '1':
            self.fields.pop('likes')


class PostListSerializer(ModelSerializer):
    user_id = SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'number_of_likes',
            'is_published',
            'user_id'
        ]

    def get_user_id(self, obj):
        return obj.user.id
