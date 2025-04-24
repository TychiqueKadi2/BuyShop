# trade/urls.py

from django.urls import path
from .views import SubmitBidView, AcceptBidView

urlpatterns = [
    path('', SubmitBidView.as_view(), name='submit-bid'),
    path('<uuid:id>/accept/', AcceptBidView.as_view(), name='accept-bid'),
]
