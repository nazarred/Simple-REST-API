from rest_framework.serializers import (
    ModelSerializer,
    SerializerMethodField
)

from accounts.serializers import UserDetailSerializer, UserListSerializer
from posts.models import Post


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
    who_liked = SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'title',
            'content',
            'number_of_likes',
            'who_liked',
            'is_published',
            'updated',
            'timestamp',
        ]

    def get_who_liked(self, obj):
        qs = obj.get_users_who_liked()
        who_liked = UserListSerializer(qs, many=True).data
        return who_liked

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(PostDetailSerializer, self).__init__(*args, **kwargs)
        show_who_liked = self.context['request'].GET.get('who_liked')
        if not show_who_liked == '1':
            self.fields.pop('who_liked')


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