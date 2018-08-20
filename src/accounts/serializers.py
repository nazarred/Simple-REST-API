from django.conf import settings

from rest_framework import serializers
from .models import User
from .utils import HunterAPIClient

hunter = HunterAPIClient(settings.HUNTER_API_KEY)


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'last_name',
            'first_name',
            'phone',
            'date_joined'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'password1',
            'last_name',
            'first_name',
            'phone',
            'location',
            'bio',
            'site'
        ]

    def validate_password1(self, value):
        data = self.get_initial()
        password = data.get("password")
        password1 = value
        if password != password1:
            raise serializers.ValidationError("Passwords must match")
        return value

    def validate_email(self, value):
        status = hunter.email_verifier(value)
        if status == 'undeliverable':
            raise serializers.ValidationError("This email is undeliverable")
        return value

    def create(self, validated_data):
        data = validated_data.copy()
        data.pop('password1')
        user_inst = User.objects.create_inactive_user(**data)
        return user_inst


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'last_name',
            'first_name',
        ]
