from django.conf.urls import url
from .views import (
    like_or_unlike_view
)

urlpatterns = [
    url(r'^likes/$', like_or_unlike_view, name='likes'),
]
