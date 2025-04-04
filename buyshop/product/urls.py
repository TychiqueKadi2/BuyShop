from .views import ProductCreateView, ProductUpdateView
from django.urls import path

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name="product-create"),
    path('update/', ProductUpdateView.as_view(), name="product-update")
]