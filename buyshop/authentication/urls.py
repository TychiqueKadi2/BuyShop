from django.urls import path
from .views import (
    # Buyer endpoints
    BuyerSignupView,
    BuyerLoginView,
    BuyerForgotPasswordView,
    BuyerResetPasswordView,
    ProfileView,
    KYCUpdateView,
    
    # Seller endpoints
    SellerSignupView,
    SellerLoginView,
    SellerForgotPasswordView,
    SellerResetPasswordView,
    
    # Common endpoints for both buyers and sellers
    LogoutView,
    CommonVerifyEmailView,
    ResendVerificationCodeView,
)

urlpatterns = [
    # User endpoints
    path('signup/user/', BuyerSignupView.as_view(), name='signup_buyer'),
    path('login/user/', BuyerLoginView.as_view(), name='login_buyer'),
    path('forgot-password/user/', BuyerForgotPasswordView.as_view(), name='forgot_password_buyer'),
    path('reset-password/user/', BuyerResetPasswordView.as_view(), name='reset_password_user'),
    # path('profile/user/', ProfileView.as_view(), name='profile_user'),
    # path('kyc-update/user/', KYCUpdateView.as_view(), name='kyc_update'),

    # Seller endpoints
    path('signup/seller/', SellerSignupView.as_view(), name='signup_seller'),
    path('login/seller/', SellerLoginView.as_view(), name='login_seller'),
    path('forgot-password/seller/', SellerForgotPasswordView.as_view(), name='forgot_password_seller'),
    path('reset-password/seller/', SellerResetPasswordView.as_view(), name='reset_password_seller'),
    
    # Common endpoints
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/', CommonVerifyEmailView.as_view(), name='verify_email'),
    path('resend-code/', ResendVerificationCodeView.as_view(), name='resend_code'),
]
