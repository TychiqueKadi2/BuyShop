from django.urls import path
from .views import (
    # Buyer endpoints
    BuyerSignupView,
    BuyerLoginView,
    BuyerProfileView,
    BuyerKYCUpdateView,
    
    # Seller endpoints
    SellerSignupView,
    SellerLoginView,
    SellerProfileView,
    SellerKYCUpdateView,
    
    # Common endpoints for both buyers and sellers
    LogoutView,
    CommonVerifyEmailView,
    ResendVerificationCodeView,
    SwitchRoleAPIView,
    ForgotPasswordView,
    ResetPasswordView
)

urlpatterns = [
    # User endpoints
    path('signup/user/', BuyerSignupView.as_view(), name='signup_buyer'),
    path('login/user/', BuyerLoginView.as_view(), name='login_buyer'),
    path('buyer/kyc/<uuid:id>/', BuyerKYCUpdateView.as_view(), name='buyer_kyc_update'),
    # path('profile/user/', ProfileView.as_view(), name='profile_user'),

    # Seller endpoints
    path('signup/seller/', SellerSignupView.as_view(), name='signup_seller'),
    path('login/seller/', SellerLoginView.as_view(), name='login_seller'),
    path('seller/kyc/<uuid:id>/', SellerKYCUpdateView.as_view(), name='seller_kyc_update'),
  
    # Common endpoints
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/', CommonVerifyEmailView.as_view(), name='verify_email'),
    path('resend-code/', ResendVerificationCodeView.as_view(), name='resend_code'),
    path('switch-role/', SwitchRoleAPIView.as_view(), name='switch_role'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
]
