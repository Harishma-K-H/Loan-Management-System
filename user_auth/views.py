from django.conf import settings
from django.core.mail import send_mail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import OTPVerification
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
import random
User = get_user_model()

class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        username = request.data.get("username")
        role = request.data.get("role", "user") 

        if not email or not password or not username:
            return Response({"error": "Email, username, and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User already exists"}, status=status.HTTP_400_BAD_REQUEST)

        otp_code = str(random.randint(100000, 999999))
        OTPVerification.objects.create(email=email, otp=otp_code)

        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP is: {otp_code}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to email"}, status=status.HTTP_201_CREATED)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        password = request.data.get("password")
        username = request.data.get("username")
        role = request.data.get("role", "user")
        try:
            otp_record = OTPVerification.objects.get(email=email, otp=otp)

            if User.objects.filter(email=email).exists():
                return Response({"error": "User already registered"}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(email=email, username=username, password=password)

            otp_record.delete()

            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User registered successfully",
                # "access": str(refresh.access_token),
                # "refresh": str(refresh)
            }, status=status.HTTP_201_CREATED)

        except OTPVerification.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        


class LoginAPIView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

