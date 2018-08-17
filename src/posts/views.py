from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
    )
from rest_framework.response import Response

from .serializers import (
    PostDetailSerializer,
    PostCreateUpdateSerializer,
    PostListSerializer
)
from .models import Post, Like

User = get_user_model()


@api_view(['POST'])
def like_or_unlike_view(request):
    try:
        user_id = int(request.POST.get('user_id'))
        post_id = int(request.POST.get('post_id'))
    except ValueError as e:
        return Response({'error': 'dfdf'})
    user = get_object_or_404(User, id=user_id)
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=user, post=post)
    if not created:
        like.delete()
    return Response({'liked': created})


class PostDetailAPIView(RetrieveAPIView):
    serializer_class = PostDetailSerializer
    queryset = Post.objects.all()


class PostCreateAPIView(CreateAPIView):
    serializer_class = PostCreateUpdateSerializer
    queryset = Post.objects.all()


class PostUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateUpdateSerializer
    lookup_field = 'slug'
    # permission_classes = [IsOwnerOrReadOnly]

    # lookup_url_kwarg = "abc"
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)


class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'
    # permission_classes = [IsOwnerOrReadOnly]


class PostListAPIView(ListAPIView):
    serializer_class = PostListSerializer
    queryset = Post.objects.all()

