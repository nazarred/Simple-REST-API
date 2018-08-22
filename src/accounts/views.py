from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.views.generic import TemplateView

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import (
    CreateAPIView,
    RetrieveAPIView,
    )
from rest_framework.response import Response

from .serializers import (
    UserCreateSerializer,
    UserDetailSerializer,
)
from .utils import get_additional_info

User = get_user_model()


class UserDetailAPIView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()

    def get_full_data(self, request):
        """
        get additional data for user from clearbit.com
        return request.data wit additional data
        """
        email = request.data.get('email')
        additional_data = get_additional_info(email)
        if additional_data:
            data = request.data.copy()
            data.update(additional_data)
            return data
        return request.data

    def create(self, request, *args, **kwargs):
        data = self.get_full_data(request)
        serializer = self.get_serializer(data=data)
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
            return user.activate()
