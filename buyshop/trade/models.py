from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import uuid
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class Rating(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    buyer = models.ForeignKey('authentication.Buyer', on_delete=models.CASCADE, related_name='reviews')
    seller = models.ForeignKey('authentication.Seller', on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('buyer', 'seller')


@receiver(post_save, sender=Rating)
def update_seller_rating_on_save(sender, instance, **kwargs):
    instance.seller.update_rating()

@receiver(post_delete, sender=Rating)
def update_seller_rating_on_delete(sender, instance, **kwargs):
    instance.seller.update_rating()


class Bid(models.Model):
    """
    Bids made on a product by Buyers.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey('authentication.Buyer', on_delete=models.CASCADE, related_name='bids')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bidder.email} - {self.amount}"


@receiver(post_save, sender=Bid)
def start_bidding_timer_and_notify(sender, instance, created, **kwargs):
    product = instance.product

    if created:
        # Start 48-hour countdown if it's the first bid
        if not product.bid_start_time:
            product.bid_start_time = timezone.now()
            product.save()

        # Send email to seller
        subject = f"New Bid for Your Product: {product.name}"
        message = f"""
        A new bid has been placed on your product: {product.name}
        Bid Amount: ${instance.amount}
        Bidder: {instance.bidder.email}
        View your product to accept or reject bids.
        """
        send_mail(
            subject,
            message,
            'no-reply@buyshop.com',
            [product.seller.email],
            fail_silently=False,
            reply_to=[]
        )

class Order(models.Model):
    """
    Model representing an order placed by a buyer.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    buyer = models.ForeignKey('authentication.Buyer', related_name="orders", on_delete=models.CASCADE)
    product = models.ForeignKey('product.Product', related_name="orders", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.ForeignKey('authentication.Address', on_delete=models.SET_NULL, null=True, blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.buyer}"

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)
