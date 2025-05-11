from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from .models import User, Address, SellerProfile, BuyerProfile


###############################################################################
# Base Serializers
###############################################################################

class BaseSignupSerializer(serializers.ModelSerializer):
    """
    Base serializer for signup operations.
    Expects inheriting serializers to specify the model and fields.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )

    class Meta:
        model = None 
        fields = ('email', 'password', 'role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.Meta.model:
            self.fields['email'].validators = [
                UniqueValidator(queryset=self.Meta.model.objects.all(), message="This email is already in use.")
            ]

    def create(self, validated_data):
        return self.Meta.model.objects.create_user(**validated_data)

class BaseLoginSerializer(serializers.Serializer):
    """
    Base serializer for login operations.
    Validates email and password, returning the authenticated user.
    """
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

class BuyerSignupSerializer(BaseSignupSerializer):
    """
    Serializer for buyer signup.
    Automatically sets the role to 'buyer' during user creation.
    """
    class Meta(BaseSignupSerializer.Meta):
        model = User  # Use the unified User model
        fields = BaseSignupSerializer.Meta.fields

    def create(self, validated_data):
        # Set the role to 'buyer' before creating the user
        validated_data['role'] = 'buyer'
        return super().create(validated_data)

class BuyerLoginSerializer(BaseLoginSerializer):
    """
    Serializer for user login.
    Validates email and password directly against the User model and ensures the user is a buyer.
    """
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")
        if user.role != 'buyer':
            raise serializers.ValidationError("This account is not registered as a buyer.")
        if not user.is_active:
            raise serializers.ValidationError("Account is not active or verified.")

        data['user'] = user
        return data

class BuyerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating client user profiles.
    The email field is read-only.
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'address', 'phone_number', 'role')
        read_only_fields = ('email', 'role')

class SellerSignupSerializer(BaseSignupSerializer):
    """
    Serializer for seller signup.
    Automatically sets the role to 'seller' during user creation.
    """
    class Meta(BaseSignupSerializer.Meta):
        model = User  # Use the unified User model
        fields = BaseSignupSerializer.Meta.fields

    def create(self, validated_data):
        # Set the role to 'seller' before creating the user
        validated_data['role'] = 'seller'
        return super().create(validated_data)

class SellerLoginSerializer(BaseLoginSerializer):
    """
    Serializer for seller login.
    Validates email and password directly against the User model and ensures the user is a seller.
    """
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")
        if user.role != 'seller':
            raise serializers.ValidationError("This account is not registered as a seller.")
        if not user.is_active:
            raise serializers.ValidationError("Account is not active or verified.")

        data['user'] = user
        return data

class SellerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating client user profiles.
    The email field is read-only.
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'address', 'phone_number', 'role', 'account_name', 'account_number', 'bank_name')
        read_only_fields = ('email', 'role')

class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    Expects an email and a 4-digit OTP.
    """
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=4)

class ResendOTPSerializer(serializers.Serializer):
    """
    Serializer for resending an OTP.
    Only requires the user's email.
    """
    email = serializers.EmailField()

class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for the address model.
    """
    street = serializers.CharField(max_length=255, required=True)
    city = serializers.CharField(max_length=100, required=True)
    state = serializers.CharField(max_length=100, required=True)
    country = serializers.CharField(max_length=100, required=True)
    label = serializers.CharField(max_length=50, required=True)
    class Meta:
        model = Address
        fields = ['street', 'city', 'state', 'country', 'label']
    
class KYCUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating KYC details for a user.
    Validates first name, last name, phone number, and address.
    Dynamically handles role-specific fields.
    """
    phone_number = PhoneNumberField(required=True)
    address = AddressSerializer(write_only=True)

    class Meta:
        model = User  # Use the unified User model
        fields = ['first_name', 'last_name', 'address', 'phone_number']

    def validate_first_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("First name must contain only alphabetic characters.")
        return value

    def validate_last_name(self, value):
        if not value.isalpha():
            raise serializers.ValidationError("Last name must contain only alphabetic characters.")
        return value

    def validate_phone_number(self, value):
        if len(str(value)) < 10 or len(str(value)) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits.")
        return value

    def update(self, instance, validated_data):
        address_data = validated_data.pop('address', None)

        # Update base user fields
        instance = super().update(instance, validated_data)

        # Handle address update
        if address_data:
            Address.objects.update_or_create(
                user=instance,
                defaults=address_data
            )

        # Create or update role-specific profile
        if instance.role == 'seller':
            seller_profile, _ = SellerProfile.objects.get_or_create(user=instance)
            seller_profile.is_verified_seller = True
            seller_profile.save()

        elif instance.role == 'buyer':
            buyer_profile, _ = BuyerProfile.objects.get_or_create(user=instance)
            buyer_profile.is_verified_buyer = True
            buyer_profile.save()

        return instance


class SellerKYCUpdateSerializer(KYCUpdateSerializer):
    account_name = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()
    bank_name = serializers.SerializerMethodField()

    class Meta(KYCUpdateSerializer.Meta):
        model = User
        fields = KYCUpdateSerializer.Meta.fields + [
            'account_name', 'account_number', 'bank_name'
        ]

    def get_account_name(self, obj):
        return getattr(obj.seller, 'account_name', None)

    def get_account_number(self, obj):
        return getattr(obj.seller, 'account_number', None)

    def get_bank_name(self, obj):
        return getattr(obj.seller, 'bank_name', None)

    def update(self, instance, validated_data):
        account_name = validated_data.pop('account_name', None)
        account_number = validated_data.pop('account_number', None)
        bank_name = validated_data.pop('bank_name', None)

        seller_profile, _ = SellerProfile.objects.get_or_create(user=instance)
        if account_name: seller_profile.account_name = account_name
        if account_number: seller_profile.account_number = account_number
        if bank_name: seller_profile.bank_name = bank_name
        seller_profile.is_verified_seller = True
        seller_profile.save()

        return super().update(instance, validated_data)


