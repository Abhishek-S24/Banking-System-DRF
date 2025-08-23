from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import BankAccount
from .serializers import BankAccountSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import random


def generate_unique_account_number():
    while True:
        number = str(random.randint(10000000, 99999999))  # 8-digit account number
        if not BankAccount.objects.filter(account_number=number).exists():
            return number


class CreateBankAccountView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'account_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Type of account (SAVINGS or CURRENT)',
                    enum=['SAVINGS', 'CURRENT']
                ),
                'currency': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Currency for the account',
                    enum=['INR', 'USD', 'GBP', 'EUR']
                )
            },
            required=[]
        ),
        responses={201: openapi.Response('Bank account created', BankAccountSerializer)}
    )
    def post(self, request):
        user = request.user
        if not user.active or user.frozen:
            return Response({'error': 'Your account is inactive or frozen.'}, status=status.HTTP_403_FORBIDDEN)

        account_type = request.data.get('account_type', 'SAVINGS')
        currency = request.data.get('currency', 'INR')
        account_number = generate_unique_account_number()

        serializer = BankAccountSerializer(
            data={
                'user': user.id,
                'account_type': account_type,
                'currency': currency,
                'account_number': account_number
            }
        )
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListBankAccountsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve all bank accounts for the authenticated user",
        responses={200: openapi.Response('List of bank accounts', BankAccountSerializer(many=True))}
    )
    def get(self, request):
        user = request.user
        if not user.active or user.frozen:
            return Response({'error': 'Your account is inactive or frozen.'}, status=status.HTTP_403_FORBIDDEN)

        accounts = BankAccount.objects.filter(user=user)
        serializer = BankAccountSerializer(accounts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
