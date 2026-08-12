from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from catalog_app.models import Category, Product
from user_app.models import User
from cart_app.models import Cart, CartItem, Order, OrderItem, WishList


class CartAppAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='TestPass123!'
        )
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            name='Wireless Mouse',
            description='Ergonomic mouse for everyday use.',
            price=Decimal('19.99'),
            slug='wireless-mouse',
            category=self.category,
        )

    def test_cart_item_manager_creates_cart_and_item(self):
        url = reverse('add_remove_item_from_cart', kwargs={'cart_code': 123})

        response = self.client.post(url, {'product_id': self.product.id}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Cart.objects.filter(cart_code=123).exists())

        cart = Cart.objects.get(cart_code=123)
        self.assertEqual(cart.cart_items.count(), 1)

        cart_item = cart.cart_items.first()
        self.assertEqual(cart_item.product.id, self.product.id)
        self.assertEqual(cart_item.quantity, 1)

    def test_update_cart_item_quantity_updates_and_removes_item_when_zero(self):
        cart = Cart.objects.create(cart_code=456)
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
        )

        update_url = reverse(
            'udpate_cart_item_quantity',
            kwargs={'cart_code': cart.cart_code, 'item_id': cart_item.id},
        )

        response = self.client.patch(update_url, {'quantity': 5}, format='json')

        self.assertEqual(response.status_code, 200)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)

        response = self.client.patch(update_url, {'quantity': 0}, format='json')

        self.assertEqual(response.status_code, 204)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

    def test_toggle_wishlist_adds_and_removes_product_for_user(self):
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(
            token_url,
            {'username': self.user.username, 'password': 'TestPass123!'},
            format='json',
        )

        self.assertEqual(token_response.status_code, 200)
        access_token = token_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        url = reverse('toggle_wishlist', kwargs={'product_id': self.product.id})
        # Toggle On
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 200)

        # Get wishlist for this user and check 
        wishlist = WishList.objects.get(user=self.user)
        self.assertTrue(wishlist.product.filter(id=self.product.id).exists())

        # Toggle OFF
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, 200)
        # Refresh db and check if product is out of wishlist
        wishlist.refresh_from_db()
        self.assertFalse(wishlist.product.filter(id=self.product.id).exists())

    def test_create_checkout_session_returns_stripe_checkout_data(self):
        token_url = reverse('token_obtain_pair')
        token_response = self.client.post(
            token_url,
            {'username': self.user.username, 'password': 'TestPass123!'},
            format='json',
        )
        self.assertEqual(token_response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")

        cart = Cart.objects.create(cart_code=789)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        # create  a fake Stripe checkout session object
        class StripeSession:
            id = 'cs_test_123'
            url = 'https://checkout.stripe.com/test_123'

        session = StripeSession()
        # mimic the call of create_checkout_session from stripe and make the return value to be session object 
        with patch('cart_app.views.client.v1.checkout.sessions.create', return_value=session) as mock_create:
            response = self.client.post(
                reverse('create_checkout_session'),
                {'cart_code': cart.cart_code},
                format='json',
            )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.data['id'], 'cs_test_123')
        self.assertEqual(response.data['url'], 'https://checkout.stripe.com/test_123')
        mock_create.assert_called_once()

