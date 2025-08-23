from rest_framework import serializers
from .models import BankAccount

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [ 'user', 'account_number', 'balance', 'account_type', 'created_at', 'updated_at']
        read_only_fields = ['balance', 'created_at', 'updated_at', 'account_number']

    def create(self, validated_data):
        import random
        # Generate unique 12-digit account number
        while True:
            acc_num = str(random.randint(100000000000, 999999999999))
            if not BankAccount.objects.filter(account_number=acc_num).exists():
                break
        validated_data['account_number'] = acc_num
        return super().create(validated_data)
