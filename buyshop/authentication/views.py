import logging
from datetime import timedelta

from django.utils.timezone import now
from django.contrib.auth.hashers import check_password
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import IntegrityError

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Buyer, Seller, OTP
from .serializers import (
    BuyerSignupSerializer,
    EmailVerificationSerializer,
    BuyerLoginSerializer,
    ResendOTPSerializer,
    BuyerProfileSerializer,
    SellerSignupSerializer,
    SellerLoginSerializer,
    BuyerKYCUpdateSerializer,
    SellerKYCUpdateSerializer,
)
from .utils import generate_otp, send_password_reset_otp_email, send_verification_otp_email, IsBuyer, IsSeller 

logger = logging.getLogger(__name__)

class SwitchRoleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Switch user role",
        operation_description="Allows an authenticated user to switch between 'buyer' and 'seller' roles. Issues a new access and refresh token with the updated role.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['new_role'],
            properties={
                'new_role': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The new role to switch to. Must be either 'buyer' or 'seller'.",
                    enum=['buyer', 'seller']
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="Role switched successfully",
                examples={
                    "application/json": {
                        "message": "Role switched to seller",
                        "access_token": "jwt-access-token",
                        "refresh_token": "jwt-refresh-token"
                    }
                }
            ),
            400: openapi.Response(
                description="Invalid role",
                examples={
                    "application/json": {
                        "error": "Invalid role"
                    }
                }
            ),
        }
    )
    def post(self, request):
        user = request.user
        new_role = request.data.get('new_role')  # The new role (either 'buyer' or 'seller')
        
        # Check if the new role is valid
        if new_role not in ['buyer', 'seller']:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)
        
        # If the user is already the requested role, no need to switch
        if getattr(request.user, 'user_type', None) == new_role:
            return Response({"message": f"You are already a {new_role}"}, status=status.HTTP_200_OK)
        
        # Issue a new JWT token with the updated role (new_role)
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Send the new JWT token back to the user
        response =  Response({
            'message': f'Role switched to {new_role}',
            'access_token': str(access_token),
            'refresh_token': str(refresh)
        }, status=status.HTTP_200_OK)
        request.user.user_type = new_role
        request.user.save()
        response.set_cookie(
            key='user_type',
            value=new_role,
            httponly=True,  # Prevent JavaScript access
            secure=True,    # Use HTTPS (set to False for local development if HTTPS is not enabled)
            samesite='Lax', # Prevent CSRF in cross-site requests
            max_age=7 * 24 * 60 * 60  # Set cookie expiration to 7 days (in seconds)
        )
        return response




###############################################################################
# Base Views for Signup, Login, Forgot & Reset Password
###############################################################################

class BaseSignupView(APIView):
    serializer_class = None
    permission_classes = []  # Allow unauthenticated access
    success_message = "Signup successful. Check your email for OTP."
    user_type = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            # Check if email already exists in DB
            if self.user_type == 'buyer' and Buyer.objects.filter(email=email).exists():
                return Response({"error": "An account with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)
            elif self.user_type == 'seller' and Seller.objects.filter(email=email).exists():
                return Response({"error": "An account with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate OTP but don’t save to DB yet
            otp_code = generate_otp()
            # Store signup data in session
            request.session['signup_email'] = email
            request.session['signup_data'] = serializer.validated_data
            request.session['signup_otp'] = otp_code
            request.session['user_type'] = self.user_type

            # Send OTP
            email_sent = send_verification_otp_email(email, otp_code)
            if email_sent:
                return Response({"message": self.success_message}, status=status.HTTP_201_CREATED)
            else:
                # Clean up session on failure
                for key in ['signup_email', 'signup_data', 'signup_otp', 'user_type']:
                    request.session.pop(key, None)
                return Response({"error": "Failed to send OTP email. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaseLoginView(APIView):
    """
    Base view for handling login.
    Expects a serializer_class attribute that validates and returns a user.
    """
    serializer_class = None
    permission_classes = []
    model_class = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            response = Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)
            if self.model_class == 'buyer':
                response.set_cookie(
                    key='user_type',
                    value='buyer',
                    httponly=True,  # Prevent JavaScript access
                    secure=True,    # Use HTTPS (set to False for local development if HTTPS is not enabled)
                    samesite='Lax', # Prevent CSRF in cross-site requests
                    max_age=7 * 24 * 60 * 60  # Set cookie expiration to 7 days (in seconds)
                )

            else:
                response.set_cookie(
                    key='user_type',
                    value='seller',
                    httponly=True,  # Prevent JavaScript access
                    secure=True,    # Use HTTPS (set to False for local development if HTTPS is not enabled)
                    samesite='Lax', # Prevent CSRF in cross-site requests
                    max_age=7 * 24 * 60 * 60  # Set cookie expiration to 7 days (in seconds)
                )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaseForgotPasswordView(APIView):
    """
    Base view for handling forgot password.
    Expects a model_class attribute (Buyer or Seller) that has an OTP relation.
    """
    model_class = None
    permission_classes = [] 

    def post(self, request):
        email = request.data.get("email")
        try:
            obj = self.model_class.objects.get(email=email)
            reset_otp = generate_otp()
            otp_instance, created = OTP.objects.get_or_create(
                buyer=obj if isinstance(obj, Buyer) else None,
                seller=obj if isinstance(obj, Seller) else None
            )
            otp_instance.code = reset_otp
            otp_instance.created_at = now()
            otp_instance.is_verified = False
            otp_instance.save()
            send_password_reset_otp_email(obj.email, reset_otp, validity_minutes=60)
            return Response({"message": "OTP sent to email for password reset."}, status=status.HTTP_200_OK)
        except self.model_class.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

class BaseResetPasswordView(APIView):
    """
    Base view for handling password reset using OTP.
    """
    model_class = None
    permission_classes = []  # Allow unauthenticated access

    def post(self, request):
        email = request.data.get("email")
        provided_otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        try:
            obj = self.model_class.objects.get(email=email)
            try:
                otp_instance = obj.otp
            except Exception:
                return Response({"error": "OTP not found for this user."}, status=status.HTTP_400_BAD_REQUEST)
            otp_validity_duration = timedelta(minutes=60)
            if otp_instance.code != provided_otp or (now() - otp_instance.created_at) > otp_validity_duration:
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
            obj.set_password(new_password)
            otp_instance.delete()
            obj.save()
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        except self.model_class.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

###############################################################################
# Buyer Endpoints
###############################################################################

class BuyerSignupView(BaseSignupView):
    serializer_class = BuyerSignupSerializer
    success_message = "User signup successful. Check your email for OTP."
    user_type = 'buyer'

    @swagger_auto_schema(
        request_body=BuyerSignupSerializer,
        responses={
            201: "Signup successful. Check your email for OTP.",
            400: "Invalid input or user already exists."
        }
    )
    def post(self, request):
        return super().post(request)

class BuyerLoginView(BaseLoginView):
    serializer_class = BuyerLoginSerializer
    model_class = 'buyer'
    @swagger_auto_schema(
        request_body=BuyerLoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful. Returns JWT tokens.",
                examples={"application/json": {
                    "refresh": "refresh_token_here",
                    "access": "access_token_here"
                }}
            ),
            400: "Invalid email or password."
        }
    )
    def post(self, request):
        return super().post(request)

class BuyerForgotPasswordView(BaseForgotPasswordView):
    model_class = Buyer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email")
            },
            required=['email']
        ),
        responses={200: "OTP sent to email for password reset.", 404: "User not found."}
    )
    def post(self, request):
        return super().post(request)

class BuyerResetPasswordView(BaseResetPasswordView):
    model_class = Buyer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description="OTP received via email"),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
            },
            required=['email', 'otp', 'new_password']
        ),
        responses={
            200: "Password reset successful.",
            400: "Invalid or expired OTP.",
            404: "User not found."
        }
    )
    def post(self, request):
        return super().post(request)

class ProfileView(APIView):
    """
    Endpoint for client users to retrieve and update their profile.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        responses={200: BuyerProfileSerializer()}
    )
    def get(self, request):
        serializer = BuyerProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        request_body=BuyerProfileSerializer,
        responses={
            200: "Profile updated successfully.",
            400: "Invalid input."
        }
    )
    def patch(self, request):
        serializer = BuyerProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




###############################################################################
# Seller Endpoints
###############################################################################

class SellerSignupView(BaseSignupView):
    serializer_class = SellerSignupSerializer
    success_message = "User signup successful. Check your email for OTP."
    user_type = 'seller'

    @swagger_auto_schema(
        request_body=SellerSignupSerializer,
        responses={
            201: "User signup successful. Check your email for OTP.",
            400: "Invalid input or user already exists."
        }
    )
    def post(self, request):
        return super().post(request)

class SellerLoginView(BaseLoginView):
    serializer_class = SellerLoginSerializer
    model_class = 'seller'

    @swagger_auto_schema(
        request_body=SellerLoginSerializer,
        responses={
            200: openapi.Response(
                description="Seller login successful. Returns JWT tokens.",
                examples={"application/json": {
                    "refresh": "refresh_token_here",
                    "access": "access_token_here"
                }}
            ),
            400: "Invalid email or password."
        }
    )
    def post(self, request):
        return super().post(request)

class SellerForgotPasswordView(BaseForgotPasswordView):
    model_class = Seller

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email")
            },
            required=['email']
        ),
        responses={200: "OTP sent to email for password reset.", 404: "User not found."}
    )
    def post(self, request):
        return super().post(request)

class SellerResetPasswordView(BaseResetPasswordView):
    model_class = Seller

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description="OTP received via email"),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
            },
            required=['email', 'otp', 'new_password']
        ),
        responses={
            200: "Password reset successful.",
            400: "Invalid or expired OTP.",
            404: "User not found."
        }
    )
    def post(self, request):
        return super().post(request)

###############################################################################
# Common Endpoints for Both Buyers & Sellers
###############################################################################

class LogoutView(APIView):
    """
    Endpoint to logout an authenticated user (buyer or seller) by blacklisting the refresh token.
    """
    permission_classes = []

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token")
            },
            required=['refresh_token']
        ),
        responses={
            200: "Logout successful.",
            400: "Invalid token or already blacklisted."
        }
    )
    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error blacklisting token: {e}")
            return Response({"error": "Invalid token or already blacklisted."}, status=status.HTTP_400_BAD_REQUEST)

# class ChangePasswordView(APIView):
#     """
#     Endpoint for authenticated users (buyer or seller) to change their password.
#     """
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         request_body=openapi.Schema(
#             type=openapi.TYPE_OBJECT,
#             properties={
#                 'old_password': openapi.Schema(type=openapi.TYPE_STRING, description="Current password"),
#                 'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
#             },
#             required=['old_password', 'new_password']
#         ),
#         responses={
#             200: "Password changed successfully.",
#             400: "Invalid old password or input."
#         }
#     )
#     def post(self, request):
#         user = request.user
#         old_password = request.data.get("old_password")
#         new_password = request.data.get("new_password")
#         if not check_password(old_password, user.password):
#             return Response({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
#         user.set_password(new_password)
#         user.save()
#         return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

class CommonVerifyEmailView(APIView):
    permission_classes = []

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description="OTP code")
            },
            required=['email', 'otp']
        ),
        responses={
            200: "Email verified successfully.",
            400: "Invalid or expired OTP, or invalid data."
        }
    )
    def post(self, request):
        email = request.data.get("email")
        otp_input = request.data.get("otp")
        if not email or not otp_input:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify session data
        if (request.session.get('signup_email') != email or 
            request.session.get('signup_otp') != otp_input):
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Determine user type and serializer
        user_type = request.session.get('user_type')
        signup_data = request.session.get('signup_data')
        
        if user_type == 'buyer':
            serializer = BuyerSignupSerializer(data=signup_data)
        elif user_type == 'seller':
            serializer = SellerSignupSerializer(data=signup_data)
        else:
            return Response({"error": "Invalid user type in session."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create and save the instance only after verification
        if serializer.is_valid():
            instance = serializer.save()
            instance.is_active = True
            instance.save()
            # Clear session
            for key in ['signup_email', 'signup_data', 'signup_otp', 'user_type']:
                request.session.pop(key, None)
            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationCodeView(APIView):
    """
    Common endpoint to resend the verification OTP code for email verification
    for both client buyers and sellers. Expects 'email' in the request.
    """
    permission_classes = []
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email")
            },
            required=['email']
        ),
        responses={
            200: "Verification code resent successfully.",
            400: "Email not found in signup process.",
            500: "Failed to send verification email."
        }
    )
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if this email is in a pending signup session
        if request.session.get('signup_email') != email:
            return Response({"error": "Email not found in signup process."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate and store new OTP
        new_otp_code = generate_otp()
        request.session['signup_otp'] = new_otp_code
        
        # Send the OTP email
        email_sent = send_verification_otp_email(email, new_otp_code, validity_minutes=60)
        if email_sent:
            return Response({"message": "Verification code resent successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to send verification email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

###############################################################################
# KYC Update Endpoint
###############################################################################


class BuyerKYCUpdateView(generics.UpdateAPIView):
    """
    Endpoint for updating KYC details for the authenticated client user.
    Allows updating first name, last name, physical address, phone number, and profile picture.
    """
    queryset = Buyer.objects.all()
    serializer_class = BuyerKYCUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuyer]

    def get_object(self):
        return self.request.user
    
    @swagger_auto_schema(
        operation_description="Update KYC details for the authenticated buyer.",
        request_body=BuyerKYCUpdateSerializer,
        responses={
            200: openapi.Response(
                description="KYC updated successfully",
                examples={
                    "application/json": {"message": "KYC updated successfully."}
                }
            ),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({"message": "KYC updated successfully."}, status=status.HTTP_200_OK)


class SellerKYCUpdateView(generics.UpdateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerKYCUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    def get_object(self):
        return self.request.user 

    @swagger_auto_schema(
        operation_description="Update KYC details for the authenticated seller.",
        request_body=SellerKYCUpdateSerializer,
        responses={
            200: openapi.Response(
                description="KYC updated successfully",
                examples={
                    "application/json": {"message": "KYC updated successfully."}
                }
            ),
            400: "Bad Request",
            401: "Unauthorized"
        }
    )
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({"message": "KYC updated successfully."}, status=status.HTTP_200_OK)

