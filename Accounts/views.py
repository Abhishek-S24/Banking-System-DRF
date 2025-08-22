from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import BankAccount
from .serializers import BankAccountSerializer

class CreateBankAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        # Check if user is active and not frozen
        if not user.active or user.frozen:
            return Response({'error': 'Your account is inactive or frozen.'}, status=status.HTTP_403_FORBIDDEN)

        account_type = request.data.get('account_type', 'SAVINGS')
        serializer = BankAccountSerializer(data={'user': user.id, 'account_type': account_type})
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListBankAccountsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.active or user.frozen:
            return Response({'error': 'Your account is inactive or frozen.'}, status=status.HTTP_403_FORBIDDEN)

        accounts = BankAccount.objects.filter(user=user)
        serializer = BankAccountSerializer(accounts, many=True)
        return Response(serializer.data)
