from django.urls import path
from .views import RegisterUserView, VerifyOTPView,LoginAPIView

urlpatterns = [
    path("api/register/", RegisterUserView.as_view(), name="register"),
    path("api/login/", LoginAPIView.as_view(), name="login"),
    path("api/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
]