# trade/serializers.py

from rest_framework import serializers
from .models import Bid

class BidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ['id', 'product', 'bidder', 'amount', 'is_accepted', 'created_at']
        read_only_fields = ['id', 'is_accepted', 'created_at', 'bidder']

    def create(self, validated_data):
        validated_data['bidder'] = self.context['request'].user
        return super().create(validated_data)
