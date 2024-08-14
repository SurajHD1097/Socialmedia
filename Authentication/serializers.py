from rest_framework import serializers
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.validators import validate_email
from django.contrib.auth import get_user_model, authenticate
User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[validate_email])

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name']

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email is already registered.")
        return email

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'].lower(),
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email').lower()
        password = data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise exceptions.AuthenticationFailed('Invalid credentials')
        else:
            raise exceptions.ValidationError('Must include "email" and "password".')

        refresh = RefreshToken.for_user(user)
        data['user_id'] = user.id
        data['email'] = user.email
        data['first_name'] = user.first_name
        data['last_name'] = user.last_name
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data
