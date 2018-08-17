from django.conf.urls import url
from .views import (
    UserCreateAPIView,
    UserDetailAPIView
)

urlpatterns = [
    url(r'^register/$', UserCreateAPIView.as_view(), name='register'),
    url(r'^detail/(?P<pk>\d+)/$', UserDetailAPIView.as_view(), name='detail'),

]
