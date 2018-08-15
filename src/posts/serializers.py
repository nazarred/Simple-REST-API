from rest_framework import serializers
from .models import Like


# class LikeCreateSerializer(serializers.ModelSerializer):
#
#     class Meta:
#         model = Like
#         fields = [
#             'user',
#             'post',
#         ]
#
#     def validated_data(self):
#         data = super(LikeCreateSerializer, self).validated_data()
#
#
#     def create(self, validated_data):
#         like, created = Like.objects.get_or_create(**validated_data)
#         if not created:
#             like.delete()
#         return validated_data
