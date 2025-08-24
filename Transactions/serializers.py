from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'account', 'transaction_type', 'amount', 'timestamp', 'reference_account']

class TransactionFlatSerializer(serializers.ModelSerializer):
    account_number = serializers.CharField(source="account.account_number", read_only=True)
    user_id = serializers.IntegerField(source="account.user.id", read_only=True)
    user_name = serializers.CharField(source="account.user.username", read_only=True)
    user_email = serializers.EmailField(source="account.user.email", read_only=True)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_type",
            "amount",
            "timestamp",
            "account_number",
            "user_id",
            "user_name",
            "user_email",
        ]