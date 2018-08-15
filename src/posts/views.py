from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

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
