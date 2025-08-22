import random
import hashlib

from django.contrib.auth import authenticate
from django.core.mail import send_mail
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializers import UserSerializer


def generate_otp(user_id):
    otp = str(random.randint(100000, 999999))
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()
    cache.set(f"otp_{user_id}", otp_hash, timeout=300)
    cache.set(f"otp_attempts_{user_id}", 0, timeout=300)
    return otp

def verify_otp(user_id, otp_input):
    otp_hash = cache.get(f"otp_{user_id}")
    attempts_key = f"otp_attempts_{user_id}"

    if otp_hash is None:
        return False, "OTP expired or not found"

    attempts = cache.get(attempts_key, 0)

    if attempts >= 5:
        return False, "Too many attempts. Try again later."

    if hashlib.sha256(otp_input.encode()).hexdigest() == otp_hash:
        cache.delete(f"otp_{user_id}")
        cache.delete(attempts_key)
        return True, "OTP verified"
    else:
        cache.incr(attempts_key)
        return False, f"Invalid OTP. Attempts left: {5 - (attempts + 1)}"


class LoginView(APIView):
    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            user = authenticate(username=username, password=password)
            if not user:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            otp = generate_otp(user.id) 

            send_mail(
                "Your OTP",
                f"Your login OTP is {otp}",
                "noreply@bankingapp.com",
                [user.email],
            )

            return Response({"message": "OTP sent to your email. Verify to complete login."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    def post(self, request):
        try:
            username = request.data.get("username")
            otp = request.data.get("otp")

            user = get_object_or_404(User, username=username)
            otp_verified , message = verify_otp(user_id=user.id)
            if not otp_verified:
                return Response({'error' : message} , status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            cache.delete(f"otp_{user.id}") 

            return Response({"refresh": str(refresh), "access": str(refresh.access_token)})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, email=None):
        try:
            if email:
                user = get_object_or_404(User, email=email)
                serializer = UserSerializer(user)
            else:
                users = User.objects.filter(active=True)
                serializer = UserSerializer(users, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, email):
        try:
            user = get_object_or_404(User, email=email)
            serializer = UserSerializer(user, data=request.data, partial=False)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, email):
        try:
            user = get_object_or_404(User, email=email)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, email):
        try:
            user = get_object_or_404(User, email=email)
            user.active = False
            user.save()
            return Response({"detail": "User deactivated"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
