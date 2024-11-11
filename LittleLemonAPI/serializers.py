from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Cart, MenuItem, Order, OrderItem


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"  # Or specify the fields explicitly


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "groups"]


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = [
            "user",
            "menuitem",
            "quantity",
            "unit_price",
            "price",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True) # to display the related order_items

    class Meta:
        model = Order
        fields = ['id','user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['user', 'total', 'date', 'order_items']