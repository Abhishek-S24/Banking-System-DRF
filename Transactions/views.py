import requests
from io import BytesIO
from decimal import Decimal

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

import polars as pl

from Accounts.models import BankAccount
from .models import Transaction
from .serializers import TransactionSerializer , TransactionFlatSerializer


def convert_currency(amount, from_currency, to_currency):
    if from_currency == to_currency:
        return amount
    # Free API endpoint from exchangerate.host (no API key required)
    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
    response = requests.get(url)
    data = response.json()
    converted_amount = data['result'] * 1.01  # Apply 1% spread
    return round(converted_amount, 2)

class DepositView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Deposit money into a user's bank account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['account', 'amount'],
            properties={
                'account': openapi.Schema(type=openapi.TYPE_STRING, description='Account number to deposit into'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount to deposit'),
            },
        ),
        responses={201: openapi.Response("Transaction created", TransactionSerializer)}
    )

    def post(self, request):
        try:
            user = request.user
            if not user.active or user.frozen:
                raise PermissionDenied("Your account is inactive or frozen.")

            account_number = request.data.get('account')
            amount = Decimal(request.data.get('amount', 0))
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
    
    @swagger_auto_schema(
        operation_description="Withdraw money from a user's bank account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['account', 'amount'],
            properties={
                'account': openapi.Schema(type=openapi.TYPE_STRING, description='Account number to withdraw from'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount to withdraw'),
            },
        ),
        responses={201: openapi.Response("Transaction created", TransactionSerializer)}
    )
    def post(self, request):
        try:
            user = request.user
            if not user.active or user.frozen:
                raise PermissionDenied("Your account is inactive or frozen.")

            account_number = request.data.get('account')
            amount = Decimal(request.data.get('amount', 0))
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

    @swagger_auto_schema(
        operation_description="Transfer money between two accounts",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['from_account', 'to_account', 'amount'],
            properties={
                'from_account': openapi.Schema(type=openapi.TYPE_STRING, description='Source account number'),
                'to_account': openapi.Schema(type=openapi.TYPE_STRING, description='Destination account number'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount to transfer'),
            },
        ),
        responses={201: openapi.Response("Transaction created", TransactionSerializer)}
    )
    def post(self, request):
        try:
            user = request.user
            if not user.active or user.frozen:
                raise PermissionDenied("Your account is inactive or frozen.")

            from_id = request.data.get('from_account')
            to_id = request.data.get('to_account')
            amount = Decimal(request.data.get('amount', 0))

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


class TransactionHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(
        operation_description="Get transaction history for a specific account",
        manual_parameters=[
            openapi.Parameter('account', openapi.IN_QUERY, description="Bank account ID", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('type', openapi.IN_QUERY, description="Filter by transaction type: deposit, withdraw, transfer", type=openapi.TYPE_STRING),
            openapi.Parameter('count', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
        ],
        responses={200: openapi.Response("Transaction list", TransactionSerializer(many=True))}
    )

    def get(self, request):
        try:
            data = request.GET
            account_id = data.get('account')
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            transaction_type = data.get('type')  # e.g., deposit, withdraw, transfer
            count = int(data.get("count", 0))
            page = int(data.get("page", 0))

            offset = count * page if count else 0

            account = get_object_or_404(BankAccount, account_number=account_id, user=request.user)

            transactions = Transaction.objects.filter(account=account)

            if start_date:
                transactions = transactions.filter(timestamp__gte=start_date)
            if end_date:
                transactions = transactions.filter(timestamp__lte=end_date)

            # filter by transaction type
            if transaction_type:
                transactions = transactions.filter(transaction_type__iexact=transaction_type)
            
            total_count = transactions.count()

            transactions = transactions.order_by('-timestamp')

            if count:
                page_end = offset + count
                transactions = transactions[offset:page_end]
                if page_end > total_count:
                    page_end = total_count
            else:
                page_end = total_count


            serializer = TransactionSerializer(transactions, many=True).data
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


class ViewAllTransactions(APIView):
    permission_classes = [IsAuthenticated] 
    @swagger_auto_schema(
        operation_description="Get transaction history (JSON or Excel if ?excel=true)",
        manual_parameters=[
            openapi.Parameter('account', openapi.IN_QUERY, description="Bank account number (optional)", type=openapi.TYPE_STRING),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('type', openapi.IN_QUERY, description="Filter by transaction type: DEPOSIT, WITHDRAW, TRANSFER", type=openapi.TYPE_STRING),
            openapi.Parameter('count', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number (starting from 0)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('excel', openapi.IN_QUERY, description="Export as Excel if true", type=openapi.TYPE_BOOLEAN),
        ],
        responses={200: openapi.Response("Transaction list", TransactionFlatSerializer(many=True))}
    )
    def get(self, request):
            try:
                data = request.GET
                account_id = data.get("account")
                start_date = data.get("start_date")
                end_date = data.get("end_date")
                transaction_type = data.get("type")
                count = int(data.get("count", 0))
                page = int(data.get("page", 0))
                excel = data.get('excel' , None)

                offset = count * page if count else 0

                if not request.user.has_permission("view_all_transactions"):
                    return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

                transactions = Transaction.objects.all()

                if account_id:
                    transactions = transactions.filter(account__account_number=account_id)

                if start_date:
                    transactions = transactions.filter(timestamp__date__gte=start_date)
                if end_date:
                    transactions = transactions.filter(timestamp__date__lte=end_date)

                if transaction_type:
                    transactions = transactions.filter(transaction_type__iexact=transaction_type)

                total_count = transactions.count()
                transactions = transactions.order_by("-timestamp")

                if count:
                    page_end = offset + count
                    transactions = transactions[offset:page_end]
                    if page_end > total_count:
                        page_end = total_count
                else:
                    page_end = total_count

                serializer = TransactionFlatSerializer(transactions, many=True)
                if excel:
                    cleaned_array = serializer.data

                    if cleaned_array:
                        pretty_headers = {
                            k: k.replace("_", " ").title()
                            for k in cleaned_array[0].keys()
                        }
                        transformed = [
                            {pretty_headers[k]: v for k, v in row.items()}
                            for row in cleaned_array
                        ]
                    else:
                        transformed = []

                    df = pl.DataFrame(transformed)
                    buffer = BytesIO()
                    df.write_excel(workbook=buffer, autofit=True)
                    buffer.seek(0)

                    response = HttpResponse(
                        buffer.getvalue(),
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                    response["Content-Disposition"] = 'attachment; filename="transactions.xlsx"'
                    return response

                return Response(
                    {
                        "data": serializer.data,
                        "pageStart": offset + 1 if serializer.data else 0,
                        "pageEnd": page_end,
                        "totalCount": total_count,
                    },
                    status=status.HTTP_200_OK,
                )

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    