from rest_framework import serializers
from .models import Product, ProductImage, Category
from authentication.models import Seller, Address
from django.contrib.contenttypes.models import ContentType


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProductImage model.
    """
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        model = Category
        fields = ['name']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    city = serializers.CharField(
        max_length=255,
        required=True,
        help_text="City where the product is located")
    new_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        help_text="List of new images to upload for the product"
    )
    # Accept a list of category names
    categories = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text="List of category names to associate with the product"
    )
    category_details = CategorySerializer(source='categories', many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'quantity',
            'condition',
            'categories',  # write-only
            'images',  # read-only
            'is_available',
            'category_details',  # read-only
            'new_images',
            'city',
            'state',
            'country',
        ]
        read_only_fields = ['id', 'images', 'category_details']

    def create(self, validated_data):
        category_names = validated_data.pop('categories', [])
        new_images = validated_data.pop('new_images', [])

        product = Product.objects.create(**validated_data)

        for name in category_names:
            category, _ = Category.objects.get_or_create(name=name)
            product.categories.add(category)

        for image in new_images:
            ProductImage.objects.create(product=product, image=image)

        return product

    def update(self, instance, validated_data):
        category_names = validated_data.pop('categories', [])
        new_images = validated_data.pop('new_images', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if category_names:
            categories = []
            for name in category_names:
                category, _ = Category.objects.get_or_create(name=name)
                categories.append(category)
            instance.categories.set(categories)

        for image in new_images:
            ProductImage.objects.create(product=instance, image=image)

        return instance

class SellerInfoSerializer(serializers.ModelSerializer):
    city    = serializers.SerializerMethodField()
    state   = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()

    class Meta:
        model = Seller
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "email",
            "city",
            "state",
            "country",
        ]

    def _get_primary_address(self, obj):
        # Assumes you defined on Seller:
        #   address = GenericRelation('Address', content_type_field='user_type', object_id_field='object_id')
        return obj.address.first()  # None if they haven’t set any

    def get_city(self, obj):
        addr = self._get_primary_address(obj)
        return addr.city if addr else None

    def get_state(self, obj):
        addr = self._get_primary_address(obj)
        return addr.state if addr else None

    def get_country(self, obj):
        addr = self._get_primary_address(obj)
        return addr.country if addr else None


class ProductDetailSerializer(serializers.ModelSerializer):
    seller_info = SellerInfoSerializer(source="seller", read_only=True)
    category_details = CategorySerializer(source="categories", many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "category_details",
            "images",
            "seller_info",
        ]
