from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.views.generic import TemplateView

from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
    )
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserDetailSerializer

User = get_user_model()


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_inst = serializer.save()
        user_inst.send_activation_email()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ActivationView(TemplateView):
    template_name = 'accounts/activate.html'

    def get_context_data(self, **kwargs):
        context = super(ActivationView, self).get_context_data(**kwargs)
        context['activated'] = self.check_activation()
        return context

    def check_activation(self):
        token = self.kwargs.get('token')
        pk = self.kwargs.get('pk')
        user = get_object_or_404(User, id=int(pk))
        token_generator = PasswordResetTokenGenerator()
        verified = token_generator.check_token(user, token)
        if verified:
            user.activate()
        return user.is_active

