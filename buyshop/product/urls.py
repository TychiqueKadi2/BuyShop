from .views import (ProductCreateView, ProductUpdateView, DeleteProductView,
                    ProductListView, ProductByBuyerLocationView,
                    SearchItemsView)
from django.urls import path

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name="product-create"),
    path('update/<uuid:id>/', ProductUpdateView.as_view(), name="product-update"),
    path('delete/<uuid:id>/', DeleteProductView.as_view(), name="product-delete"),
    path('all/', ProductListView.as_view(), name="product-list"),
    path('city/', ProductByBuyerLocationView.as_view(), name="product-by-city"),
    path('search/', SearchItemsView.as_view(), name="product-search"),
]