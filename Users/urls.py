from django.urls import path
from .views import LoginView, VerifyOTPView, UserView  , RegisterView , BulkUserCreateView

urlpatterns = [
    # User registration, list, update, deactivate
    path('register/' , RegisterView.as_view() , name='registeration'),
    path('users/', UserView.as_view(), name='user-list-create'),           # GET all active users, POST create user
    path('users/<str:email>/', UserView.as_view(), name='user-detail'),    # GET/PUT/PATCH/DELETE specific user by email
    path('bulk-create/', BulkUserCreateView.as_view(), name='bulk-user-create'), # Create user in bulk

    # Authentication
    path('login/', LoginView.as_view(), name='login'),                      # POST login + send OTP
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),       # POST verify OTP and get JWT
]