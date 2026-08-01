from rest_framework import serializers
from .models import CartItem, Cart, WishList
from catalog_app.serializers import ProductListSerializer, ProductDetailSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    sub_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'sub_total']

    def get_sub_total(self, cart_item):
        return (cart_item.product.price * int(cart_item.quantity))


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(read_only=True, many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'cart_items', 'cart_code', 'total']

    def get_total(self, cart):
        items = cart.cart_items.all()        
        return sum((item.quantity * item.product.price) for item in items)

class WishListSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = WishList
        fields = ['id', 'product', 'user', 'created_at', 'updated_at']