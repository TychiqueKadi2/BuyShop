from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer, ProductDetailSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q, Case, When, IntegerField
from authentication.utils import IsSeller, IsBuyer
from django.contrib.contenttypes.models import ContentType
from authentication.models import Address


class ProductCreateView(generics.CreateAPIView):
    """
    View for sellers to create a new product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]

    @swagger_auto_schema(
        operation_summary="Create a new product",
        operation_description="Allows authenticated sellers to create a new product by providing details like name, description, price, condition, categories, and images.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name', 'description', 'price', 'quantity', 'condition', 'categories'],
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
                'city': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="City where the product is located"
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
                    description="List of image files to upload"
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
        
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Product created successfully",
            "product": response.data
        }, status=status.HTTP_201_CREATED)

class ProductUpdateView(generics.RetrieveUpdateAPIView):
    """
    View for sellers to update an existing product.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

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
        print("KWARGS:", kwargs)
        try:
            instance = self.get_object()
        except Exception as e:
            print("DEBUG: get_object() failed:", str(e))
            raise  # Let it bubble to see full stack
        if instance.seller != request.user:
            return Response(
                {'error': 'You do not have permission to update this product'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Product updated successfully",
            "product": serializer.data
        }, status=status.HTTP_200_OK)


class DeleteProductView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsSeller]
    lookup_field = 'id'

    @swagger_auto_schema(
        operation_description="Delete a product by its ID.",
        responses={
            204: openapi.Response(description="Product deleted successfully"),
            404: openapi.Response(description="Product not found"),
            401: openapi.Response(description="Authentication required")
        }
    )
    def delete(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            if product.seller != request.user:
                return Response(
                    {'error': 'You do not have permission to delete this product'},
                    status=status.HTTP_403_FORBIDDEN
                )
            product.delete()
            return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuyer]
    

    @swagger_auto_schema(
        operation_summary="List all products with pagination",
        operation_description="Returns a paginated list of products. Use `?page=1`, `?page=2` etc. in the URL.",
        responses={
            200: openapi.Response("Paginated list of products", ProductSerializer(many=True)),
        }
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class ProductByBuyerLocationView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuyer]

    def get_queryset(self):
        user = self.request.user
        user_type = ContentType.objects.get_for_model(user.__class__)

        try:
            address = Address.objects.get(user_type=user_type, object_id=user.id)
            buyer_city = address.city
            buyer_state = address.state
            buyer_country = address.country
        except Address.DoesNotExist:
            return Product.objects.none()

        # Filter by availability and same country and state
        queryset = Product.objects.filter(
            is_available=True,
            country=buyer_country,
            state=buyer_state
        ).annotate(
            priority=Case(
                When(city=buyer_city, then=0),  # Products in the same city come first
                default=1,
                output_field=IntegerField()
            )
        ).order_by('priority', '-created_at')

        return queryset

    @swagger_auto_schema(
        operation_summary="List products in the same city/state as the buyer",
        operation_description="Returns available products ordered by priority: same city first, then same state within the same country.",
        responses={
            200: openapi.Response("List of products", ProductSerializer(many=True)),
            401: "Unauthorized",
            403: "Forbidden - Only buyers can access this view",
        }
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

class SearchItemsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsBuyer]

    def get_queryset(self):
        """
        Optionally restricts the returned products to those matching the search parameters.
        """
        queryset = Product.objects.all()

        search_query = self.request.query_params.get('search', None)
        category_query = self.request.query_params.get('category', None)
        
        # Filtering based on search terms (name, category)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        if category_query:
            queryset = queryset.filter(categories__name__icontains=category_query)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        Handles GET requests and returns the filtered products list.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductInfoView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related("seller").prefetch_related("categories", "images")
    serializer_class = ProductDetailSerializer
    lookup_field = "id"
    permission_classes = [permissions.IsAuthenticated, IsBuyer]
    lookup_url_kwarg = "id"
    @swagger_auto_schema(
        operation_summary="Get product details",
        operation_description="Retrieve detailed information about a specific product by its ID.",
        responses={
            200: openapi.Response("Product details", ProductDetailSerializer),
            404: "Product not found",
            401: "Unauthorized - Authentication required",
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and returns the product details.
        """
        return self.retrieve(request, *args, **kwargs)