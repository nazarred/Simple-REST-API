from rest_framework import serializers
from .models import User


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
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
        ]

    def validate_password1(self, value):
        data = self.get_initial()
        password = data.get("password")
        password1 = value
        if password != password1:
            raise serializers.ValidationError("Passwords must match")
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
