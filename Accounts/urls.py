from django.urls import path
from .views import CreateBankAccountView, ListBankAccountsView

urlpatterns = [
    path('create/', CreateBankAccountView.as_view(), name='create-account'),
    path('list/', ListBankAccountsView.as_view(), name='list-accounts'),
]