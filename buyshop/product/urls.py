from .views import ProductCreateView, ProductUpdateView, DeleteProductView, ProductListView, ProductByBuyerCityView
from django.urls import path

urlpatterns = [
    path('create/', ProductCreateView.as_view(), name="product-create"),
    path('update/<uuid:id>/', ProductUpdateView.as_view(), name="product-update"),
    path('delete/<uuid:id>/', DeleteProductView.as_view(), name="product-delete"),
    path('', ProductListView.as_view(), name="product-list"),
    path('city/', ProductByBuyerCityView.as_view(), name="product-by-city"),
]