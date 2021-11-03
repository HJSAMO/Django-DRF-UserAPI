from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        return User.objects.update_user(instance, validated_data)


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'phone', 'nickname', 'name')
