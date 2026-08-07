from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Cart, CartItem, WishList, Order, OrderItem
from .serializers import CartItemSerializer, CartSerializer, WishListSerializer

from catalog_app.models import Product

# Stripe related imports
import stripe
client = stripe.StripeClient(settings.STRIPE_SECRET_KEY)
endpoint_secret = settings.STRIPE_WEBHOOK_SEC


@api_view(['POST', 'DELETE'])
def cart_item_manager(request, cart_code):
    # this function can be cleaned for now we are in MAKE IT WORK PHASE
    if request.method == 'POST':
        product_id = request.data.get('product_id')

        cart, created = Cart.objects.get_or_create(cart_code=cart_code)
        product = Product.objects.get(id=product_id)

        cart_item = CartItem.objects.create(product=product, cart=cart)
        cart_item.quantity = 1
        cart_item.save()

        serializer = CartSerializer(cart)

        return Response(serializer.data)
    if request.method == 'DELETE':
        product_id = request.data.get('product_id')
        cart = Cart.objects.get(cart_code=cart_code)
        cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
        cart_item.delete()
        serializer = CartItemSerializer(cart_item)
        return Response (
            {
                'message': 'Item removed',
                'data': serializer.data
            }
        )

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



@api_view(['POST'])
def create_checkout_session(request):

    # for now get the cart code from the body
    cart_code = request.data.get('cart_code')
    cart = Cart.objects.get(cart_code=cart_code)
    cart_items = cart.cart_items.all()

    processed_cart = []
    for item in cart_items:
        processed_cart.append({
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.product.name,
                },
                'unit_amount': int(item.product.price * 100),
            },
            'quantity': item.quantity 
        })
    
    try:
        checkout_session = client.v1.checkout.sessions.create(params={
            'customer_email': request.user.email,
            'mode': 'payment',
            'line_items': processed_cart,
            'success_url': 'http://127.0.0.1:8000/success',
            'metadata' : {'cart_code':cart_code}
        })
    except Exception as e:
        return Response({'error': str(e)}, status=400)

    return Response({'id':checkout_session.id, 'url': checkout_session.url}, status=303)

@csrf_exempt
def my_webhook_view(request):
  payload = request.body
  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
  event = None

  try:
    event = client.construct_event(payload, sig_header, endpoint_secret)
  except ValueError as e:
    # Invalid payload
    return HttpResponse(status=400)
  except stripe.error.SignatureVerificationError as e:
    # Invalid signature
    return HttpResponse(status=400)

  if (event['type'] == 'checkout.session.completed' or event['type'] == 'checkout.session.async_payment_succeeded'):
    session = event['data']['object']
    cart_code = session.to_dict().get('metadata', {}).get('cart_code')
    print('BEFORE calling fulfill')
    fulfill_checkout(session, cart_code)
  return HttpResponse(status=200)

def fulfill_checkout(session, cart_code):
    order = Order.objects.create(
      stripe_checkout_id = session['id'],
      amount = session['amount_total'],
      customer_email = session['customer_email'],
      status = 'Paid'
      )

    cart = Cart.objects.get(cart_code=cart_code)
    cart_items = cart.cart_items.all()

    for item in cart_items:
       OrderItem.objects.create(
          order=order,
          product = item.product,
          quantity = item.quantity
       )

    # after this cart is paid we can delete it 
    # may be keep it for future statistics ?
    cart.delete()
    print('FROM FULFILL')
    print(session)