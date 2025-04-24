from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, Count
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation


###############################################################################
# Base Manager: Shared logic for creating users
###############################################################################
class BaseCustomUserManager(BaseUserManager):
    """
    Base manager for custom user models. It centralizes user creation logic,
    ensuring email normalization, password setting, and common validations.
    """
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email=email, password=password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email=email, password=password, **extra_fields)

###############################################################################
# Abstract Base Model: Common fields for all user types
###############################################################################
class AbstractCustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Abstract user model that holds fields and methods common to both clients and drivers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    address = GenericRelation('Address', content_type_field='user_type', object_id_field='object_id',)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = BaseCustomUserManager()


###############################################################################
# Buyer Model
###############################################################################
class Buyer(AbstractCustomUser):
    """
        Buyer model that extends the abstract custom user with client-specific fields.
    """
    is_verified_buyer = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, default='buyer')


###############################################################################
# Seller Model (updated for optional KYC fields)
###############################################################################
class Seller(AbstractCustomUser):
    """
    Seller model that extends the abstract custom user with seller-specific fields.
    """

    total_sales_completed = models.PositiveIntegerField(default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    is_verified_seller = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, default='seller')

    def update_rating(self):
        result = self.ratings.aggregate(total_value=Sum('rating'), total_count=Count('id'))
        
        # Check if there are any ratings
        if result['total_count'] > 0:
            self.average_rating = result['total_value'] / result['total_count']
            self.rating_count = result['total_count']
        self.save()


###############################################################################
# OTP Model: For handling email verification (shared by Users and Drivers)
###############################################################################
class OTP(models.Model):
    """
    Model to handle email verification via a 4-digit OTP code.
    The OTP is valid for 60 minutes.
    This model supports both client users and drivers by allowing only one of the
    relationships to be set.
    """
    buyer = models.OneToOneField(Buyer, on_delete=models.CASCADE, related_name='otp', null=True, blank=True)
    seller = models.OneToOneField(Seller, on_delete=models.CASCADE, related_name='otp', null=True, blank=True)
    code = models.CharField(max_length=4)  # 4-digit OTP code
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return f"OTP for {self.user.email}"
        elif self.driver:
            return f"OTP for {self.driver.email}"
        else:
            return "Unassigned OTP"

    def is_expired(self):
        """
        Checks if the OTP has expired (after 60 minutes).
        """
        expiration_time = timezone.now() - timezone.timedelta(minutes=60)
        return self.created_at < expiration_time


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # These two fields define the generic relation
    user_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    user = GenericForeignKey('user_type', 'object_id')

    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='South Africa')
    label = models.CharField(max_length=50, blank=True, default='Home')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} - {self.street}, {self.city}"
