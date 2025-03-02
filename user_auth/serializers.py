from rest_framework import serializers
from .models import CustomUser, OTPVerification
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password','role']
        extra_kwargs = {'password': {'write_only': True}}
    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username_or_email = attrs.get("username") or attrs.get("email")
        password = attrs.get("password")

        if not username_or_email:
            raise serializers.ValidationError({"error": "Either 'username' or 'email' is required."})

        if not password:
            raise serializers.ValidationError({"error": "Password is required."})

        # Get user by email or username
        try:
            user = User.objects.get(email=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                raise serializers.ValidationError({"error": "Invalid credentials"})

        # Authenticate user using email
        authenticated_user = authenticate(username=user.email, password=password)

        if not authenticated_user:
            raise serializers.ValidationError({"error": "Invalid credentials"})

        # Generate JWT tokens
        refresh = self.get_token(authenticated_user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "email": authenticated_user.email,
            "username": authenticated_user.username,
            "role": authenticated_user.role,
        }