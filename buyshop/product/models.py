from django.db import models
import uuid
from django.utils.text import slugify
from authentication.models import Buyer, Seller
from cloudinary.models import CloudinaryField


class Category(models.Model):
    """
    Model representing a product category.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Model representing a product.
    """
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('fairly_used', 'Fairly Used'),
        ('old', 'Old')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    seller = models.ForeignKey(Seller, related_name="product_listed", on_delete=models.SET_NULL, null=True)
    buyer = models.ForeignKey(Buyer, related_name="product_bought", on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='fairly_used')
    is_available = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, related_name="products")
    city = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_bidding_over = models.BooleanField(default=False)
    bid_start_time = models.DateTimeField(blank=True, null=True)


    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return f"{self.name} ({self.condition})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            count = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    """
    Model representing an image for a product.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    image = CloudinaryField('image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.product.name}"
