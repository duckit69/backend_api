from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from catalog_app.models import Category, Product
from .models import Cart, CartItem


class CartItemManagerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            description='A test product',
            price='10.00',
            slug='test-product',
            category=self.category,
        )
        self.cart = Cart.objects.create(cart_code='21')
        self.url = reverse('add_item_to_cart', kwargs={'cart_code': 21})

    def test_post_to_cart_items_creates_cart_item(self):
        response = self.client.post(self.url, {'product_id': self.product.id}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 1)
        self.assertEqual(CartItem.objects.get(cart=self.cart).product, self.product)

    def test_delete_to_cart_items_removes_cart_item(self):
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=1)

        response = self.client.delete(self.url, {'product_id': self.product.id}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(CartItem.objects.filter(cart=self.cart, product=self.product).exists())
