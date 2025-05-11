# trade/utils.py

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from product.models import Product
from .models import Bid

def mark_expired_bids():
    now = timezone.now()
    expired_products = Product.objects.filter(
        is_available=True,
        bid_start_time__isnull=False,
        is_bidding_over=False,
    ).filter(bid_start_time__lte=now - timezone.timedelta(hours=48))

    for product in expired_products:
        # Mark the auction expired
        product.is_available = False
        product.is_bidding_over = True
        product.save()
        bid_count = Bid.objects.filter(product=product).count()
        print(f"this is bid count: {bid_count}")

        # Send email notification to the seller
        subject = f"Auction Ended: Bids on \"{product.name}\" Have Expired"
        message = (
            f"Hello {product.seller.first_name},\n\n"
            f"Your auction for the product \"{product.name}\" has just expired after 48 hours with no accepted bid.\n"
            f"You have received a total of {bid_count} bid{'s' if bid_count != 1 else ''} on this product.\n"
            f"Please log in to your dashboard to review any outstanding bids and decide whether to relist or accept a bid.\n\n"
            f"View your product here: https://your-domain.com/products/{product.slug}/\n\n"
            f"Thank you for using BuyShop!"
        )
        send_mail(
            subject,
            message,
            'noreply@buyshop.com',
            [product.seller.email],
            fail_silently=False,
        )
