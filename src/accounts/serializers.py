from rest_framework import serializers
from .models import User
from .utils import get_hunter_client


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'last_name',
            'first_name',
            'phone',
            'is_active',
            'date_joined'
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)
    activation_key = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'password1',
            'last_name',
            'first_name',
            'phone',
            'location',
            'bio',
            'site',
            'activation_key'
        ]
        extra_kwargs = {"id":
                            {"read_only": True}
                        }

    def get_activation_key(self, obj):
        if obj.id:
            return obj.generate_activation_key()

    def validate_password1(self, value):
        data = self.get_initial()
        password = data.get("password")
        password1 = value
        if password != password1:
            raise serializers.ValidationError("Passwords must match")
        return value

    def validate_email(self, value):
        hunter = get_hunter_client()
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
