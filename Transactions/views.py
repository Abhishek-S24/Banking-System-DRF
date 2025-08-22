import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404

from Accounts.models import BankAccount
from .models import Transaction
from .serializers import TransactionSerializer


def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    # Free API endpoint from exchangerate.host (no API key required)
    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
    response = requests.get(url)
    data = response.json()
    converted_amount = data['result'] * 1.01  # Apply 1% spread
    return round(converted_amount, 2)

from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

class DepositView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            if not user.active or user.frozen:
                raise PermissionDenied("Your account is inactive or frozen.")

            account_number = request.data.get('account')
            amount = float(request.data.get('amount', 0))
            account = get_object_or_404(BankAccount, account_number=account_number, user=request.user)

            if account.user != user:
                raise PermissionDenied("You can only deposit to your own accounts.")

            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)

            account.balance += amount
            account.save()

            transaction = Transaction.objects.create(account=account, transaction_type='DEPOSIT', amount=amount)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class WithdrawView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            if not user.active or user.frozen:
                raise PermissionDenied("Your account is inactive or frozen.")

            account_number = request.data.get('account')
            amount = float(request.data.get('amount', 0))
            account = get_object_or_404(BankAccount, account_number=account_number, user=request.user)

            if account.user != user:
                raise PermissionDenied("You can only withdraw from your own accounts.")

            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
            if amount > account.balance:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

            account.balance -= amount
            account.save()

            transaction = Transaction.objects.create(account=account, transaction_type='WITHDRAW', amount=amount)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
class TransferView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            if not user.active or user.frozen:
                raise PermissionDenied("Your account is inactive or frozen.")

            from_id = request.data.get('from_account')
            to_id = request.data.get('to_account')
            amount = float(request.data.get('amount', 0))

            from_account = get_object_or_404(BankAccount, account_number=from_id)
            to_account = get_object_or_404(BankAccount, account_number=to_id)

            if from_account.user != user:
                raise PermissionDenied("You can only transfer from your own accounts.")

            if amount <= 0:
                return Response({'error': 'Amount must be positive'}, status=status.HTTP_400_BAD_REQUEST)
            if amount > from_account.balance:
                return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

            # Multi-currency conversion with 1% spread
            final_amount = convert_currency(amount, from_account.currency, to_account.currency)

            # Perform transfer
            from_account.balance -= amount
            to_account.balance += final_amount
            from_account.save()
            to_account.save()

            transaction = Transaction.objects.create(
                account=from_account,
                transaction_type='TRANSFER',
                amount=amount,
                reference_account=to_account
            )
            transaction = TransactionSerializer(transaction).data

            return Response(transaction, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.utils.dateparse import parse_datetime

class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account_id = request.query_params.get('account')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        transaction_type = request.query_params.get('type')  # e.g., deposit, withdraw, transfer

        account = get_object_or_404(BankAccount, id=account_id, user=request.user)

        transactions = Transaction.objects.filter(account=account)

        if start_date:
            transactions = transactions.filter(timestamp__gte=start_date)
        if end_date:
            transactions = transactions.filter(timestamp__lte=end_date)

        # filter by transaction type
        if transaction_type:
            transactions = transactions.filter(transaction_type__iexact=transaction_type)

        transactions = transactions.order_by('-timestamp')

        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)