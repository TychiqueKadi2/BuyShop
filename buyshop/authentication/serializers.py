from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from .models import Buyer, Seller, Address
from django.contrib.contenttypes.models import ContentType


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
        fields = ('email', 'password')

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

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request=self.context.get('request'), email=email, password=password)
        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")
        data['user'] = user
        return data

class BuyerSignupSerializer(BaseSignupSerializer):
    """
    Serializer for client user signup.
    Only includes email and password; additional fields are handled during KYC.
    """
    class Meta(BaseSignupSerializer.Meta):
        model = Buyer
        fields = BaseSignupSerializer.Meta.fields

class BuyerLoginSerializer(BaseLoginSerializer):
    """
    Serializer for user login.
    Validates email and password directly against the User model.
    """
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            user = Buyer.objects.get(email=email)
        except Buyer.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials for a user.")
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials for a user.")
        if not user.is_active:
            raise serializers.ValidationError("Account not verified.")
        data['user'] = user
        return data

class BuyerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and updating client user profiles.
    The email field is read-only.
    """
    class Meta:
        model = Buyer
        fields = ('email', 'first_name', 'last_name', 'physical_address', 'phone_number')
        read_only_fields = ('email',)

class SellerSignupSerializer(BaseSignupSerializer):
    """
    Serializer for Seller signup.
    For Sellers, only email and password are required.
    """
    class Meta(BaseSignupSerializer.Meta):
        model = Seller
        fields = ('email', 'password')

class SellerLoginSerializer(BaseLoginSerializer):
    """
    Serializer for Seller login.
    Validates that the authenticated user is a Seller instance.
    """
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        try:
            seller = Seller.objects.get(email=email)
        except Seller.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials for a seller.")
        if not seller.check_password(password):
            raise serializers.ValidationError("Invalid credentials for a seller.")
        data['user'] = seller
        return data

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
    Validates first name, last name, physical address, phone number, and profile picture.
    """
    phone_number = PhoneNumberField(required=True)
    address = AddressSerializer(write_only=True)

    class Meta:
        model = None
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
        
        # Update the main model instance
        instance = super().update(instance, validated_data)
        if isinstance(instance, Buyer):
            instance.is_verified_buyer = True
        elif isinstance(instance, Seller):
            instance.is_verified_seller = True
        instance.save()
        
        # Handle address data if provided
        if address_data:
            content_type = ContentType.objects.get_for_model(instance)

            Address.objects.update_or_create(
                user_type=content_type,
                object_id=instance.id,
                defaults=address_data
            )

        return instance
    
class BuyerKYCUpdateSerializer(KYCUpdateSerializer):
    """
    Serializer for updating KYC details for a Buyer.
    Inherits from the base KYCUpdateSerializer.
    """
    class Meta(KYCUpdateSerializer.Meta):
        model = Buyer
        fields = KYCUpdateSerializer.Meta.fields

class SellerKYCUpdateSerializer(KYCUpdateSerializer):
    """
    Serializer for updating KYC details for a Seller.
    Inherits from the base KYCUpdateSerializer.
    """
    account_name = serializers.CharField(max_length=100, required=True)
    account_number = serializers.CharField(max_length=20, required=True)
    bank_name = serializers.CharField(max_length=100, required=True)
    class Meta(KYCUpdateSerializer.Meta):
        model = Seller
        fields = KYCUpdateSerializer.Meta.fields + ['account_name', 'account_number', 'bank_name']