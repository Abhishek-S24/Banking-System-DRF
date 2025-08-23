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

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

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
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password')
            },
            required=['username', 'password']
        ),
        responses={200: 'OTP sent', 401: 'Invalid credentials'}
    )

    def post(self, request):
        try:
            username = request.data.get("username")
            password = request.data.get("password")

            user = authenticate(username=username, password=password)
            if not user:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

            otp = generate_otp(user.id) 

            send_mail(
                "Hey well come back",
                f"Your login OTP is {otp} and it will be valid for 5 mins",
                "noreply@bankingapp.com",
                [user.email],
            )

            return Response({"message": "OTP sent to your email. Verify to complete login."})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'otp': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['username', 'otp']
        ),
        responses={200: 'JWT token', 401: 'Invalid OTP'}
    )
    def post(self, request):
        try:
            username = request.data.get("username")
            otp = request.data.get("otp")

            user = get_object_or_404(User, username=username)
            otp_verified , message = verify_otp(user_id=user.id , otp_input=otp)
            if not otp_verified:
                return Response({'error' : message} , status=status.HTTP_401_UNAUTHORIZED)

            refresh = RefreshToken.for_user(user)
            cache.delete(f"otp_{user.id}") 

            return Response({"refresh": str(refresh), "access": str(refresh.access_token)})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['username', 'email', 'password']
        ),
        responses={201: UserSerializer, 400: 'Validation errors'}
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class UserView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "count", openapi.IN_QUERY, description="Number of users per page", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "page", openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                "search", openapi.IN_QUERY, description="Search by name", type=openapi.TYPE_STRING
            ),
        ],
        responses={200: "List of users or single user"}
    )
    def get(self, request, email=None):
        try:
            if email:
                user = get_object_or_404(User, email=email)
                serializer = UserSerializer(user)
                return Response(serializer.data , status=status.HTTP_200_OK)
            else:
                data = request.GET
                count = int(data.get("count", 0))
                page = int(data.get("page", 0))
                search = data.get("search")

                offset = count * page if count else 0

                users = User.objects.filter(active=True).order_by("-updated_at")
                if search:
                    users = users.filter(username__icontains=search)
                total_count = users.count()

                if count:
                    page_end = offset + count
                    users = users[offset:page_end]
                    if page_end > total_count:
                        page_end = total_count
                else:
                    page_end = total_count
                    
                serializer = UserSerializer(users, many=True).data
                return Response(
                    {
                        "data": serializer,
                        "pageStart": offset + 1 if len(serializer) else 0,
                        "pageEnd": page_end,
                        "totalCount": total_count,
                    }
                )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                # add other UserSerializer fields here
            },
            required=['username', 'email', 'password']
        ),
        responses={200: openapi.Response('Updated user', UserSerializer)}
    )
    def put(self, request, email):
        try:
            user = get_object_or_404(User, email=email)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data , status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                # add any optional fields for patch
            },
            required=[]
        ),
        responses={200: openapi.Response('Patched user', UserSerializer)}
    )

    
    def patch(self, request, email):
        try:
            user = get_object_or_404(User, email=email)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data , status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        responses={200: 'User deactivated successfully'}
    )
    def delete(self, request, email):
        try:
            user = get_object_or_404(User, email=email)
            user.active = False
            user.save()
            return Response({"detail": "User deactivated"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
