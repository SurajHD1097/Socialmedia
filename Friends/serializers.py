from rest_framework import serializers

from Authentication.models import FriendRequest, Friends

from django.contrib.auth import get_user_model
User = get_user_model()

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'timestamp', 'status']

    def create(self, validated_data):
        validated_data['from_user'] = self.context['request'].user
        return super().create(validated_data)

class FriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friends
        fields = ['id', 'user', 'friend', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name']