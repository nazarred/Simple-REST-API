from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
    )
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    PostDetailSerializer,
    PostCreateUpdateSerializer,
    PostListSerializer,
    LikeListSerializer
)
from .permissions import IsOwnerOrReadOnly
from .models import Post, Like

User = get_user_model()


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def like_or_unlike_view(request):
    try:
        user_id = int(request.POST.get('user_id'))
        post_id = int(request.POST.get('post_id'))
    except ValueError as e:
        return Response({'error': e.args[0]})
    user = get_object_or_404(User, id=user_id)
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=user, post=post)
    if not created:
        like.delete()
    return Response({'liked': created})


class LikeListAPIView(ListAPIView):
    serializer_class = LikeListSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('pk')
        return Like.objects.filter(post_id=post_id)


class PostDetailAPIView(RetrieveAPIView):
    serializer_class = PostDetailSerializer
    queryset = Post.objects.all()


class PostCreateAPIView(CreateAPIView):
    serializer_class = PostCreateUpdateSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class PostDeleteAPIView(DestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]


class PostListAPIView(ListAPIView):
    serializer_class = PostListSerializer
    queryset = Post.objects.get_active_posts()
