# trade/serializers.py

from rest_framework import serializers
from .models import Bid

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id', 'product', 'bidder', 'amount', 'is_accepted', 'created_at']
        read_only_fields = ['id', 'is_accepted', 'created_at', 'bidder']

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']

        # Check if the user has already placed a bid on this product
        if Bid.objects.filter(product=product, bidder=user).exists():
            raise serializers.ValidationError("You have already placed a bid on this product.")

        validated_data['bidder'] = user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        instance.amount = validated_data.get('amount', instance.amount)
        instance.save()
        return instance
