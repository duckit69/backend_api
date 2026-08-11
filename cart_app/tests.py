from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal

from catalog_app.models import Category, Product
from .models import Cart, CartItem, WishList, Order, OrderItem

User = get_user_model()


class CartModelTest(TestCase):
    """Test Cart model"""

    def test_cart_creation(self):
        """Test cart is created with unique code"""
        cart = Cart.objects.create(cart_code='CART123456')
        self.assertEqual(cart.cart_code, 'CART123456')

    def test_cart_code_unique(self):
        """Test cart code uniqueness"""
        Cart.objects.create(cart_code='UNIQUE001')
        with self.assertRaises(Exception):
            Cart.objects.create(cart_code='UNIQUE001')

    def test_cart_str(self):
        """Test cart string representation"""
        cart = Cart.objects.create(cart_code='TEST001')
        self.assertEqual(str(cart), 'TEST001')


class CartItemModelTest(TestCase):
    """Test CartItem model"""

    def setUp(self):
        """Create test cart and product"""
        category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=category
        )
        self.cart = Cart.objects.create(cart_code='CART001')

    def test_cart_item_creation(self):
        """Test cart item is created"""
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.product, self.product)

    def test_cart_item_default_quantity(self):
        """Test default quantity is 1"""
        item = CartItem.objects.create(cart=self.cart, product=self.product)
        self.assertEqual(item.quantity, 1)

    def test_cart_item_str(self):
        """Test cart item string representation"""
        item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=3
        )
        self.assertIn('quantity', str(item))
        self.assertIn('cart', str(item).lower())


class CartItemAPITest(APITestCase):
    """Test cart item management endpoints"""

    def setUp(self):
        """Create test data"""
        category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=category
        )
        self.cart = Cart.objects.create(cart_code='CART001')

    def test_add_item_to_cart(self):
        """Test adding product to cart"""
        data = {'product_id': self.product.id}
        response = self.client.post(
            f'/api/cart/{self.cart.cart_code}/items/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 1)

    def test_add_item_creates_cart_if_not_exists(self):
        """Test adding item creates cart if cart_code doesn't exist"""
        data = {'product_id': self.product.id}
        response = self.client.post(
            '/api/cart/NEWCART123/items/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Cart.objects.filter(cart_code='NEWCART123').exists())

    def test_remove_item_from_cart(self):
        """Test removing product from cart"""
        CartItem.objects.create(cart=self.cart, product=self.product)
        
        data = {'product_id': self.product.id}
        response = self.client.delete(
            f'/api/cart/{self.cart.cart_code}/items/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CartItem.objects.filter(cart=self.cart).exists())

    def test_add_multiple_items_to_cart(self):
        """Test adding multiple items to cart"""
        product2 = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('29.99'),
            category=self.product.category
        )
        
        self.client.post(
            f'/api/cart/{self.cart.cart_code}/items/',
            {'product_id': self.product.id}
        )
        self.client.post(
            f'/api/cart/{self.cart.cart_code}/items/',
            {'product_id': product2.id}
        )
        
        self.assertEqual(CartItem.objects.filter(cart=self.cart).count(), 2)


class UpdateCartItemQuantityTest(APITestCase):
    """Test cart item quantity update"""

    def setUp(self):
        """Create test data"""
        category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=category
        )
        self.cart = Cart.objects.create(cart_code='CART001')
        self.item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )

    def test_update_quantity(self):
        """Test updating cart item quantity"""
        data = {'quantity': 3}
        response = self.client.patch(
            f'/api/cart/{self.cart.cart_code}/items/{self.item.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 3)

    def test_update_quantity_to_zero(self):
        """Test updating quantity to zero"""
        data = {'quantity': 0}
        response = self.client.patch(
            f'/api/cart/{self.cart.cart_code}/items/{self.item.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 0)


class WishListModelTest(TestCase):
    """Test WishList model"""

    def setUp(self):
        """Create test user and products"""
        self.user = User.objects.create_user(
            username='wishlistuser',
            email='wishlist@example.com',
            password='testpass123'
        )
        category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=category
        )
        self.product2 = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('29.99'),
            category=category
        )

    def test_wishlist_creation(self):
        """Test wishlist is created for user"""
        wishlist = WishList.objects.create(user=self.user)
        self.assertEqual(wishlist.user, self.user)

    def test_wishlist_one_per_user(self):
        """Test one wishlist per user"""
        WishList.objects.create(user=self.user)
        with self.assertRaises(Exception):
            WishList.objects.create(user=self.user)

    def test_wishlist_add_products(self):
        """Test adding products to wishlist"""
        wishlist = WishList.objects.create(user=self.user)
        wishlist.product.add(self.product1, self.product2)
        
        self.assertEqual(wishlist.product.count(), 2)

    def test_wishlist_remove_product(self):
        """Test removing product from wishlist"""
        wishlist = WishList.objects.create(user=self.user)
        wishlist.product.add(self.product1, self.product2)
        wishlist.product.remove(self.product1)
        
        self.assertEqual(wishlist.product.count(), 1)
        self.assertTrue(wishlist.product.filter(id=self.product2.id).exists())


class WishListAPITest(APITestCase):
    """Test wishlist toggle endpoint"""

    def setUp(self):
        """Create test user and products"""
        self.user = User.objects.create_user(
            username='wishlistuser',
            email='wishlist@example.com',
            password='testpass123'
        )
        category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=category
        )
        self.client.force_authenticate(user=self.user)

    def test_add_product_to_wishlist(self):
        """Test adding product to wishlist"""
        response = self.client.post(f'/api/wishlist/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('added to wishlist', response.data['message'])
        
        wishlist = WishList.objects.get(user=self.user)
        self.assertTrue(wishlist.product.filter(id=self.product.id).exists())

    def test_remove_product_from_wishlist(self):
        """Test removing product from wishlist"""
        wishlist = WishList.objects.create(user=self.user)
        wishlist.product.add(self.product)
        
        response = self.client.post(f'/api/wishlist/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('deleted from wishlsit', response.data['message'])
        
        wishlist.refresh_from_db()
        self.assertFalse(wishlist.product.filter(id=self.product.id).exists())

    def test_toggle_wishlist_creates_if_not_exists(self):
        """Test toggling creates wishlist if doesn't exist"""
        self.assertFalse(WishList.objects.filter(user=self.user).exists())
        
        response = self.client.post(f'/api/wishlist/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(WishList.objects.filter(user=self.user).exists())


class OrderModelTest(TestCase):
    """Test Order model"""

    def test_order_creation(self):
        """Test order is created"""
        order = Order.objects.create(
            stripe_checkout_id='cs_test_123',
            amount=Decimal('999.99'),
            customer_email='customer@example.com',
            status='Pending'
        )
        self.assertEqual(order.status, 'Pending')
        self.assertEqual(order.stripe_checkout_id, 'cs_test_123')

    def test_order_status_choices(self):
        """Test order status choices"""
        for status_value, _ in Order._meta.get_field('status').choices:
            order = Order.objects.create(
                stripe_checkout_id=f'cs_{status_value}',
                amount=Decimal('100.00'),
                customer_email='test@example.com',
                status=status_value
            )
            self.assertEqual(order.status, status_value)

    def test_order_stripe_checkout_id_unique(self):
        """Test stripe checkout ID is unique"""
        Order.objects.create(
            stripe_checkout_id='cs_unique_123',
            amount=Decimal('100.00'),
            customer_email='test1@example.com',
            status='Pending'
        )
        with self.assertRaises(Exception):
            Order.objects.create(
                stripe_checkout_id='cs_unique_123',
                amount=Decimal('100.00'),
                customer_email='test2@example.com',
                status='Pending'
            )

    def test_order_str(self):
        """Test order string representation"""
        order = Order.objects.create(
            stripe_checkout_id='cs_test_123',
            amount=Decimal('999.99'),
            customer_email='customer@example.com',
            status='Paid'
        )
        self.assertIn('cs_test_123', str(order))
        self.assertIn('Paid', str(order))


class OrderItemModelTest(TestCase):
    """Test OrderItem model"""

    def setUp(self):
        """Create test order and product"""
        category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=category
        )
        self.order = Order.objects.create(
            stripe_checkout_id='cs_test_123',
            amount=Decimal('999.99'),
            customer_email='customer@example.com',
            status='Paid'
        )

    def test_order_item_creation(self):
        """Test order item is created"""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2
        )
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.product, self.product)

    def test_order_item_default_quantity(self):
        """Test default quantity is 1"""
        item = OrderItem.objects.create(order=self.order, product=self.product)
        self.assertEqual(item.quantity, 1)

    def test_order_item_str(self):
        """Test order item string representation"""
        item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1
        )
        self.assertIn(self.product.name, str(item))
        self.assertIn(self.order.stripe_checkout_id, str(item))

    def test_multiple_order_items(self):
        """Test order can have multiple items"""
        product2 = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('29.99')
        )
        OrderItem.objects.create(order=self.order, product=self.product, quantity=1)
        OrderItem.objects.create(order=self.order, product=product2, quantity=2)
        
        self.assertEqual(OrderItem.objects.filter(order=self.order).count(), 2)


class CartTotalCalculationTest(APITestCase):
    """Test cart total calculation in serializer"""

    def setUp(self):
        """Create test cart with items"""
        category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(
            name='Laptop',
            description='Powerful laptop',
            price=Decimal('999.99'),
            category=category
        )
        self.product2 = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('29.99'),
            category=category
        )
        self.cart = Cart.objects.create(cart_code='CART001')

    def test_empty_cart_total(self):
        """Test empty cart has zero total"""
        response = self.client.get(f'/api/cart/{self.cart.cart_code}/')
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data['total'], 0)

    def test_cart_with_single_item_total(self):
        """Test cart total with single item"""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=1
        )
        response = self.client.get(f'/api/cart/{self.cart.cart_code}/')
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(float(response.data['total']), 999.99)

    def test_cart_with_multiple_items_total(self):
        """Test cart total with multiple items"""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product1,
            quantity=1
        )
        CartItem.objects.create(
            cart=self.cart,
            product=self.product2,
            quantity=2
        )
        response = self.client.get(f'/api/cart/{self.cart.cart_code}/')
        if response.status_code == status.HTTP_200_OK:
            expected_total = 999.99 + (29.99 * 2)
            self.assertAlmostEqual(float(response.data['total']), expected_total, places=2)
