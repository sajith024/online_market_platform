from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import PrimaryKeyRelatedField

from online_market_app.models import OnlineMarketUser
from online_market_product.models import Product

from .models import CartItem, OrderManagement


class ProductUser(ModelSerializer):
    class Meta:
        model = OnlineMarketUser
        fields = ("id", "username")


class ProductSerializer(ModelSerializer):
    user = ProductUser()

    class Meta:
        model = Product
        fields = "__all__"


class ProductAddSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"


class CartItemAddSerializer(ModelSerializer):

    class Meta:
        model = CartItem
        fields = ("product", "quantity", "user")


class CartItemSerializer(ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = "__all__"


class OrderManagementSerializer(ModelSerializer):
    items = CartItemSerializer(many=True)

    class Meta:
        model = OrderManagement
        fields = "__all__"


class OrderManagementAddSerializer(ModelSerializer):
    items = PrimaryKeyRelatedField(queryset=CartItem.objects.all(), many=True)

    class Meta:
        model = OrderManagement
        fields = ("items", "shipping_address", "user", "payment_status")

    def create(self, validated_data):
        items = validated_data.pop("items")
        order_management = OrderManagement.objects.create(**validated_data)

        total_price = 0
        for item in items:
            total_price += item.quantity * item.product.price
            order_management.items.add(item)

        order_management.total_price = total_price
        order_management.save()

        return order_management
