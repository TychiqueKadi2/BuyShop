from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProductCreateView(generics.CreateAPIView):
    """
    View for sellers to create a new product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Create a new product",
        operation_description="Allows authenticated sellers to create a new product by providing details like name, description, price, condition, categories, and images.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'description', 'price', 'quantity', 'condition'],
            properties={
                'name': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Name of the product"
                ),
                'description': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Detailed description of the product"
                ),
                'price': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    format="float",
                    description="Price of the product in Naira"
                ),
                'quantity': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Number of items in stock"
                ),
                'condition': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["new", "fairly used", "old"],
                    description="Condition of the product"
                ),
                'categories': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="List of category names (e.g. ['Electronics', 'Home'])"
                ),
                'new_images': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_FILE),
                    description="Optional: List of image files to upload"
                )
            }
        ),
        responses={
            201: openapi.Response(description="Product created successfully"),
            400: openapi.Response(description="Invalid data"),
            401: openapi.Response(description="Unauthorized - Seller authentication required"),
        }
    )
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)


class ProductUpdateView(generics.RetrieveUpdateAPIView):
    """
    View for sellers to update an existing product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Update an existing product",
        operation_description="Allows sellers to update an existing product by providing updated details such as name, description, price, quantity, and images.",
        responses={
            200: openapi.Response("Product updated successfully", ProductSerializer),
            400: "Bad Request - Invalid data",
            401: "Unauthorized - Authentication required",
            404: "Not Found - Product does not exist",
        },
    )
    def update(self, request, *args, **kwargs):
        """
        Override update to handle custom response.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Product updated successfully",
            "product": serializer.data
        }, status=status.HTTP_200_OK)
