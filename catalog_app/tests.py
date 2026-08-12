from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from catalog_app.models import Category, Product, Review
from user_app.models import User


class CatalogAppAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='catalog_user',
            email='catalog@example.com',
            password='TestPass123!'
        )
        self.category = Category.objects.create(name='Gaming', slug='gaming')
        self.featured_product = Product.objects.create(
            name='Mechanical Keyboard',
            description='Compact mechanical keyboard for gaming.',
            price=Decimal('89.99'),
            slug='mechanical-keyboard',
            category=self.category,
            featured=True,
        )
        self.regular_product = Product.objects.create(
            name='Gaming Mouse',
            description='Ergonomic mouse with RGB lighting.',
            price=Decimal('49.99'),
            slug='gaming-mouse',
            category=self.category,
            featured=False,
        )

    def test_product_list_returns_featured_products(self):
        product_response = self.client.get(reverse('product_list'))
        self.assertEqual(product_response.status_code, 200)
        self.assertEqual(product_response.data[0]['name'], 'Mechanical Keyboard')

    def test_category_list_and_detail_return_expected_data(self):
        category_list_response = self.client.get(reverse('category_list'))
        self.assertEqual(category_list_response.status_code, 200)
        self.assertEqual(len(category_list_response.data), 1)

        category_detail_response = self.client.get(
            reverse('category_detail', kwargs={'slug': self.category.slug})
        )
        self.assertEqual(category_detail_response.status_code, 200)
        self.assertEqual(category_detail_response.data['name'], 'Gaming')
        self.assertIn(self.featured_product.id, category_detail_response.data['products'])

    def test_product_search_filters_by_keyword(self):
        search_response = self.client.get(reverse('product_search'), {'query': 'mechanical'})

        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.data[0]['name'], 'Mechanical Keyboard')

    def test_review_lifecycle_works_with_jwt(self):
        token_response = self.client.post(
            reverse('token_obtain_pair'),
            {'username': self.user.username, 'password': 'TestPass123!'},
            format='json',
        )
        self.assertEqual(token_response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")

        create_response = self.client.post(
            reverse('add_review', kwargs={'product_id': self.featured_product.id}),
            {'rating': 5, 'review': 'Excellent quality'},
            format='json',
        )
        self.assertEqual(create_response.status_code, 200)
        review = Review.objects.get(product=self.featured_product, user=self.user)
        self.assertEqual(review.rating, 5)

        update_response = self.client.put(
            reverse('add_review', kwargs={'product_id': self.featured_product.id}),
            {'rating': 4, 'review': 'Still very good'},
            format='json',
        )
        self.assertEqual(update_response.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)

        delete_response = self.client.delete(
            reverse('add_review', kwargs={'product_id': self.featured_product.id}),
            {'rating': 4, 'review': 'Still very good'},
            format='json',
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Review.objects.filter(product=self.featured_product, user=self.user).exists())
