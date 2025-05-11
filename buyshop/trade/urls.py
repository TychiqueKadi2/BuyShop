# trade/urls.py

from django.urls import path
from .views import SubmitBidView, AcceptBidView, BidListView

urlpatterns = [
    path('bid/', SubmitBidView.as_view(), name='submit-bid'), # for creating
    path('bid/<uuid:id>/', SubmitBidView.as_view(), name='update-bid'), # for updating
    path('<uuid:id>/accept/', AcceptBidView.as_view(), name='accept-bid'),
    path('bid/<uuid:id>/list/', BidListView.as_view(), name='bid-list'), # for listing bids by product
]
