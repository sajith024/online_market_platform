from datetime import datetime

from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.serializers import PrimaryKeyRelatedField, CharField
from rest_framework.serializers import ValidationError

from online_market_app.models import OnlineMarketUser
from online_market_product.models import Product

from .models import CartItem, OrderManagement, Cart


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
        exclude = ("user",)


class CartItemAddSerializer(ModelSerializer):

    class Meta:
        model = CartItem
        fields = ("product", "quantity")

    def update(self, instance, validated_data):
        instance.product = validated_data.get("product", instance.product)
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save()
        return instance


class CartItemSerializer(ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = "__all__"


class CartAddSerializer(ModelSerializer):
    cart_items = CartItemAddSerializer(many=True)

    class Meta:
        model = Cart
        fields = ("name", "cart_items")

    def create(self, validated_data):
        request = self.context.get("request")
        cart_items = validated_data.pop("cart_items")
        cart = Cart.objects.create(user=request.user, **validated_data)

        for item in cart_items:
            CartItem.objects.create(cart=cart, user=request.user, **item)

        return cart

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        cart_items_data = validated_data.get("cart_items")
        request = self.context.get("request")

        if cart_items_data is not None:
            for cart_item in instance.cart_items.all():
                cart_item.delete()

            for item in cart_items_data:
                CartItem.objects.create(cart=instance, user=request.user, **item)

        instance.save()
        return instance


class CartSerializer(ModelSerializer):
    cart_items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = "__all__"


class OrderManagementSerializer(ModelSerializer):
    cart = CartSerializer(many=True)

    class Meta:
        model = OrderManagement
        fields = (
            "id",
            "total_price",
            "cart",
            "shipping_address",
            "payment_status",
            "user",
            "created_at",
            "updated_at",
        )


class OrderManagementAddSerializer(ModelSerializer):
    cart = PrimaryKeyRelatedField(queryset=Cart.objects.all(), many=True)

    class Meta:
        model = OrderManagement
        fields = ("cart", "shipping_address")

    def create(self, validated_data):
        carts = validated_data.pop("cart")
        request = self.context.get("request")
        order_management = OrderManagement.objects.create(
            user=request.user, **validated_data
        )

        total_price = 0
        for cart in carts:
            cart.order = order_management
            cart.save()
            cart_items = cart.cart_items.all()
            for item in cart_items:
                total_price += item.quantity * item.product.price

        order_management.total_price = total_price
        order_management.save()

        return order_management

    def update(self, instance, validated_data):
        instance.shipping_address = validated_data.get(
            "shipping_address", instance.shipping_address
        )

        total_price = instance.total_price
        if validated_data.get("cart") is not None:
            total_price = 0
            carts = validated_data.pop("cart")
            for cart in instance.cart.all():
                cart.delete()

            for cart in carts:
                cart.order = instance
                cart.save()
                cart_items = cart.cart_items.all()
                for item in cart_items:
                    total_price += item.quantity * item.product.price

        instance.total_price = total_price
        instance.save()
        return instance
