from django.db import models
import uuid
from authentication.models import Buyer, Seller
# Create your models here.


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
    CATEGORIES_CHOICES = (
        ('general', 'General'),
        ('electronics', 'Electronics'),
        ('fashion', 'Fashion'),
        ('home_appliances', 'Home Appliances'),
        ('books', 'Books'),
        ('toys', 'Toys & Games'),
        ('sports', 'Sports & Outdoors'),
        ('beauty', 'Beauty & Personal Care'),
        ('automotive', 'Automotive'),
        ('groceries', 'Groceries'),
        ('furniture', 'Furniture'),
        ('phones', 'Mobile Phones'),
        ('computers', 'Computers & Accessories'),
        ('jewelry', 'Jewelry & Watches'),
        ('tools', 'Tools & Hardware'),
        ('music', 'Musical Instruments'),
        ('baby', 'Baby Products'),
        ('pets', 'Pet Supplies'),
        ('health', 'Health & Wellness'),
        ('gaming', 'Gaming'),
        ('stationery', 'Stationery & Office Supplies'),
    )

    CONDITION_CHOICES = (
        ('new', 'New'),
        ('fairly_used', 'Fairly Used'),
        ('old', 'Old')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    seller = models.ForeignKey(Seller, related_name="product_listed", on_delete=models.SET_NULL, null=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, related_name="product_bought", blank=True, null=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='fairly_used')
    is_available = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, related_name="products", default="general", choices=CATEGORIES_CHOICES)  # Add ManyToManyField for categories
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
    def __str__(self):
        return f"product is {self.name} and it's {self.condition}"



class ProductImage(models.Model):
    """
    Model representing an image for a product.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Image for {self.product.name if self.product else 'Unknown product'}"




