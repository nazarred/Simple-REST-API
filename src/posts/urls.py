from django.conf.urls import url
from .views import (
    like_or_unlike_view,
    PostUpdateAPIView,
    PostCreateAPIView,
    PostDeleteAPIView,
    PostDetailAPIView,
    PostListAPIView,
    LikeListAPIView
)

urlpatterns = [
    url(r'^likes/$', like_or_unlike_view, name='likes'),
    url(r'^likes-list/(?P<pk>\d+)/', LikeListAPIView.as_view(), name='likes_list'),
    url(r'^list/', PostListAPIView.as_view(), name='post_list'),
    url(r'^create/', PostCreateAPIView.as_view(), name='post_create'),
    url(r'^detail/(?P<pk>\d+)/', PostDetailAPIView.as_view(), name='post_detail'),
    url(r'^update/(?P<pk>\d+)/', PostUpdateAPIView.as_view(), name='post_update'),
    url(r'^delete/(?P<pk>\d+)/', PostDeleteAPIView.as_view(), name='post_delete'),

]
