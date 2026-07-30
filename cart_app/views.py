from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer

from catalog_app.models import Product

@api_view(['POST'])
def add_item_to_cart(request, cart_code):
    product_id = request.data.get('product_id')

    cart, created = Cart.objects.get_or_create(cart_code=cart_code)
    product = Product.objects.get(id=product_id)

    cart_item = CartItem.objects.create(product=product, cart=cart)
    cart_item.quantity = 1
    cart_item.save()

    serializer = CartSerializer(cart)

    return Response(serializer.data)

@api_view(['PATCH'])
def update_cart_item_quantity(request, cart_code, item_id):
    quantity = request.data.get("quantity")

    cart_item = CartItem.objects.get(id=item_id)
    cart_item.quantity = quantity
    cart_item.save()

    serializer = CartItemSerializer(cart_item)

    return Response({"data": serializer.data, "message": "CartItem updated Succefully"})