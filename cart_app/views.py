from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Cart, CartItem, WishList
from .serializers import CartItemSerializer, CartSerializer, WishListSerializer

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

@api_view(['POST'])
def toggle_wishlist(request, product_id):
    product = Product.objects.get(id=product_id)
    user = request.user
    wishlist, created = WishList.objects.get_or_create(user=user)

    if wishlist.product.filter(id=product.id).exists():
        wishlist.product.remove(product)
        message = 'product deleted from wishlsit'
    else:
        wishlist.product.add(product)
        message = 'product added to wishlist'
    serializer = WishListSerializer(wishlist)
    return Response(
        {
            'message': message,
            'data': serializer.data
        }
    )