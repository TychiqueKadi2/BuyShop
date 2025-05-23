# trade/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.core.mail import send_mail
from product.models import Product
from .models import Bid
from .serializers import BidSerializer

class SubmitBidView(generics.CreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

class AcceptBidView(generics.UpdateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        bid = self.get_object()
        product = bid.product

        if request.user != product.seller:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)

        # 🔒 Restrict multiple acceptances
        if Bid.objects.filter(product=product, is_accepted=True).exists():
            return Response(
                {'error': 'A bid has already been accepted for this product.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Accept bid
        bid.is_accepted = True
        bid.save()

        # Close bidding
        product.is_bidding_over = True
        product.is_available = False
        product.save()

        # Notify buyer (accepted)
        send_mail(
            subject="Your bid was accepted!",
            message=f"🎉 Your bid of ₦{bid.amount} for '{product.name}' was accepted!",
            from_email="noreply@buyshop.com",
            recipient_list=[bid.buyer.email],
            fail_silently=False,
        )

        # Notify seller
        send_mail(
            subject="Bid accepted",
            message=f"You accepted a bid of ₦{bid.amount} for '{product.name}'. We've notified the buyer.",
            from_email="noreply@buyshop.com",
            recipient_list=[product.owner.email],
            fail_silently=False,
        )

        # Notify rejected bidders
        other_bids = Bid.objects.filter(product=product).exclude(id=bid.id)
        for other_bid in other_bids:
            send_mail(
                subject="Bid update",
                message=f"Your bid of ₦{other_bid.amount} for '{product.name}' was not accepted.",
                from_email="noreply@buyshop.com",
                recipient_list=[other_bid.buyer.email],
                fail_silently=False,
            )

        return Response({'message': 'Bid accepted and notifications sent.'})
