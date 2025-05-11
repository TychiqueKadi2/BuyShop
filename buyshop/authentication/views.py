import logging
from datetime import timedelta

from django.utils.timezone import now
from django.contrib.auth.hashers import check_password
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import PermissionDenied

from .models import OTP, User
from .utils import IsBuyer, IsSeller
from .serializers import (
    BuyerSignupSerializer,
    EmailVerificationSerializer,
    BuyerLoginSerializer,
    ResendOTPSerializer,
    BuyerProfileSerializer,
    SellerProfileSerializer,
    SellerSignupSerializer,
    SellerLoginSerializer,
    KYCUpdateSerializer,
    SellerKYCUpdateSerializer,
    BaseSignupSerializer,
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

        # Validate the new role
        if new_role not in ['buyer', 'seller']:
            return Response({"error": "Invalid role"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is already in the requested role
        if user.role == new_role:
            return Response({"message": f"You are already a {new_role}"}, status=status.HTTP_200_OK)

        # Update the user's role
        user.role = new_role

        user.save()

        # Issue new JWT tokens with the updated role
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # Return the response with the new tokens
        return Response({
            'message': f'Role switched to {new_role}',
            'access_token': str(access_token),
            'refresh_token': str(refresh)
        }, status=status.HTTP_200_OK)

###############################################################################
# Base Views for Signup, Login, Forgot & Reset Password
###############################################################################

class BaseSignupView(APIView):
    serializer_class = None
    role = None
    permission_classes = []  # Allow unauthenticated access
    success_message = "Signup successful. Check your email for OTP."

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            serializer.validated_data['role'] = self.role

            # Check if email already exists in the User model
            if User.objects.filter(email=email).exists():
                return Response({"error": "An account with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

            # Generate OTP but don’t save to DB yet
            otp_code = generate_otp()

            # Store signup data in session
            request.session['signup_email'] = email
            request.session['signup_data'] = serializer.validated_data
            request.session['signup_otp'] = otp_code

            # Send OTP
            email_sent = send_verification_otp_email(email, otp_code)
            if email_sent:
                return Response({"message": self.success_message}, status=status.HTTP_201_CREATED)
            else:
                # Clean up session on failure
                for key in ['signup_email', 'signup_data', 'signup_otp']:
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

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            response = Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=status.HTTP_200_OK)

            # Dynamically set the user_type cookie based on the user's role
            response.set_cookie(
                key='user_type',
                value=user.role,
                httponly=True,  # Prevent JavaScript access
                secure=True,    # Use HTTPS (set to False for local development if HTTPS is not enabled)
                samesite='Lax', # Prevent CSRF in cross-site requests
                max_age=7 * 24 * 60 * 60  # Set cookie expiration to 7 days (in seconds)
            )
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###############################################################################
# Buyer Endpoints
###############################################################################

class BuyerSignupView(BaseSignupView):
    serializer_class = BuyerSignupSerializer
    role = 'buyer'  

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

from rest_framework.generics import RetrieveUpdateAPIView

class BuyerProfileView(RetrieveUpdateAPIView):
    """
    Endpoint for retrieving and updating a buyer's profile.
    Updates are allowed only if the authenticated user is the owner of the profile.
    """
    queryset = User.objects.filter(role='buyer')  # Ensure only buyers are queried
    serializer_class = BuyerProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'  # Use 'id' as the lookup field

    def get_object(self):
        """
        Override to ensure the authenticated user is the owner of the profile.
        """
        obj = super().get_object()
        if self.request.user != obj:
            raise PermissionDenied("You do not have permission to access this profile.")
        return obj

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Profile retrieved successfully.",
                schema=BuyerProfileSerializer
            ),
            403: "You do not have permission to access this profile.",
            404: "Profile not found."
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve the buyer's profile.
        """
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        request_body=BuyerProfileSerializer,
        responses={
            200: "Profile updated successfully.",
            400: "Invalid input.",
            403: "You do not have permission to update this profile.",
            404: "Profile not found."
        }
    )
    def patch(self, request, *args, **kwargs):
        """
        Update the buyer's profile.
        """
        return super().patch(request, *args, **kwargs)

###############################################################################
# Seller Endpoints
###############################################################################

class SellerSignupView(BaseSignupView):
    serializer_class = SellerSignupSerializer
    role = 'seller'  # Set the role to 'seller'
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
    """
    Validates email and password, and returns JWT tokens.
    """
    serializer_class = SellerLoginSerializer
    role = 'seller'  # Set the role to 'seller'

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


class SellerProfileView(RetrieveUpdateAPIView):
    """
    Endpoint for client users to retrieve and update their profile.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SellerProfileSerializer
    queryset = User.objects.filter(role='seller')  # Ensure only sellers are queried
    lookup_field = 'id'  # Use 'id' as the lookup field
    def get_object(self):
        """
        Override to ensure the authenticated user is the owner of the profile.
        """
        obj = super().get_object()
        if self.request.user != obj:
            raise PermissionDenied("You do not have permission to access this profile.")
        return obj

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        responses={
            200: openapi.Response(
                description="Profile retrieved successfully.",
                schema=SellerProfileSerializer
            ),
            403: "You do not have permission to access this profile.",
            404: "Profile not found."
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve the seller's profile.
        """
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        security=[{'Bearer': []}],
        request_body=SellerProfileSerializer,
        responses={
            200: "Profile updated successfully.",
            400: "Invalid input."
        }
    )
    def patch(self, request, *args, **kwargs):
        """
        Update the seller's profile.
        """
        return super().patch(request, *args, **kwargs)

###############################################################################
# Common Endpoints for Both Buyers & Sellers
###############################################################################

class ForgotPasswordView(APIView):
    """
    Base view for handling forgot password.
    Works with the unified User model and generates an OTP for password reset.
    """
    permission_classes = []  # Allow unauthenticated access

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch the user by email
            user = User.objects.get(email=email)

            # Generate OTP
            reset_otp = generate_otp()

            # Create or update the OTP instance for the user
            otp_instance, created = OTP.objects.get_or_create(user=user)
            otp_instance.code = reset_otp
            otp_instance.created_at = now()
            otp_instance.is_verified = False
            otp_instance.save()

            # Send the OTP via email
            send_password_reset_otp_email(user.email, reset_otp, validity_minutes=60)

            return Response({"message": "OTP sent to email for password reset."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

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

class CommonVerifyEmailView(APIView):
    """
    Endpoint to verify a user's email using an OTP.
    Works for both buyers and sellers during the signup process.
    """
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
            200: "Email verified successfully and user created.",
            400: "Invalid or expired OTP, or invalid data.",
            404: "Signup data not found for this email."
        }
    )
    def post(self, request):
        email = request.data.get("email")
        otp_input = request.data.get("otp")

        # Validate input
        if not email or not otp_input:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the email matches the session data
        if request.session.get('signup_email') != email:
            return Response({"error": "Signup data not found for this email."}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve OTP and signup data from the session
        signup_otp = request.session.get('signup_otp')
        signup_data = request.session.get('signup_data')

        if not signup_otp or not signup_data:
            return Response({"error": "Signup data not found or expired."}, status=status.HTTP_404_NOT_FOUND)

        # Validate OTP
        if signup_otp != otp_input:
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the user
        if signup_data.get('role') == 'buyer':
            serializer = BuyerSignupSerializer(data=signup_data)
        elif signup_data.get('role') == 'seller':
            serializer = SellerSignupSerializer(data=signup_data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = True  # Activate the user after successful verification
            user.save()

            # Clear session data
            for key in ['signup_email', 'signup_data', 'signup_otp']:
                request.session.pop(key, None)

            return Response({"message": "Email verified successfully and user created."}, status=status.HTTP_200_OK)
        else:
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

class ResetPasswordView(APIView):
    """
    Base view for handling password reset using OTP.
    """
    permission_classes = []  # Allow unauthenticated access
    
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
    def post(self, request):
        email = request.data.get("email")
        provided_otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        try:
            obj = User.objects.get(email=email)
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
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

###############################################################################
# KYC Update Endpoint
###############################################################################


class BuyerKYCUpdateView(generics.UpdateAPIView):
    """
    Endpoint for updating KYC details for the authenticated client user.
    Allows updating first name, last name, address, phone number, and profile picture.
    """
    serializer_class = KYCUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuyer]

    def get_object(self):
        """
        Return the authenticated user (must be a buyer).
        """
        user = self.request.user
        if user.role != 'buyer':
            raise PermissionDenied("You do not have permission to update this profile.")
        return user

    @swagger_auto_schema(
        operation_description="Update KYC details for the authenticated buyer.",
        request_body=KYCUpdateSerializer,
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
    queryset = User.objects.filter(role='seller')  # Ensure only sellers are queried
    serializer_class = SellerKYCUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'  # Use 'id' as the lookup field

    def get_object(self):
        """
        Override to ensure the authenticated user is the owner of the profile.
        """
        obj = super().get_object()
        print(obj.seller.is_verified_seller)
        if self.request.user != obj:
            raise PermissionDenied("You do not have permission to access this profile.")
        return obj 

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

