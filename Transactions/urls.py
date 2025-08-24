from django.urls import path
from .views import DepositView, WithdrawView, TransferView, TransactionHistoryView , ViewAllTransactions

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='deposit'),
    path('withdraw/', WithdrawView.as_view(), name='withdraw'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('history/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('view-all-transaction/', ViewAllTransactions.as_view(), name='view-all-transaction')
]