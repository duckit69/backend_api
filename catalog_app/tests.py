from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal

from api_config import api_url
from .models import Category, Product, Review, ProductRating

User = get_user_model()


class CategoryModelTest(TestCase):
    """Test Category model with slug generation"""

    def setUp(self):
        """Create test category"""
        self.category = Category.objects.create(
            name='Electronics',
            image=None
        )

    def test_category_creation(self):
        """Test category is created successfully"""
        self.assertEqual(self.category.name, 'Electronics')

    def test_category_slug_auto_generation(self):
        """Test slug is auto-generated from name"""
        self.assertEqual(self.category.slug, 'electronics')

    def test_category_slug_uniqueness(self):
        """Test slug is unique with counter suffix"""
        category2 = Category.objects.create(name='Electronics')
        self.assertEqual(category2.slug, 'electronics-1')
        
        category3 = Category.objects.create(name='Electronics')
        self.assertEqual(category3.slug, 'electronics-2')

    def test_category_slug_with_spaces(self):
        """Test slug generation handles spaces"""
        category = Category.objects.create(name='Home & Garden')
        self.assertIn('-', category.slug)
        self.assertNotIn(' ', category.slug)

    def test_category_str(self):
        """Test category string representation"""
        self.assertEqual(str(self.category), 'Electronics')

    def test_category_products_relation(self):
        """Test category can have multiple products"""
        product1 = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=self.category
        )
        product2 = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('29.99'),
            category=self.category
        )
        self.assertEqual(self.category.products.count(), 2)


class ProductModelTest(TestCase):
    """Test Product model with slug and featured flag"""

    def setUp(self):
        """Create test category and products"""
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=self.category,
            featured=True
        )

    def test_product_creation(self):
        """Test product is created successfully"""
        self.assertEqual(self.product.name, 'Laptop')
        self.assertEqual(self.product.price, Decimal('999.99'))
        self.assertTrue(self.product.featured)

    def test_product_slug_auto_generation(self):
        """Test slug is auto-generated"""
        self.assertEqual(self.product.slug, 'laptop')

    def test_product_slug_uniqueness(self):
        """Test product slug uniqueness with counter"""
        product2 = Product.objects.create(
            name='Laptop',
            description='Another laptop',
            price=Decimal('1299.99'),
            category=self.category
        )
        self.assertEqual(product2.slug, 'laptop-1')

    def test_product_featured_default_false(self):
        """Test featured defaults to False"""
        product = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('29.99')
        )
        self.assertFalse(product.featured)

    def test_product_without_category(self):
        """Test product can be created without category"""
        product = Product.objects.create(
            name='Standalone Item',
            description='Item without category',
            price=Decimal('50.00')
        )
        self.assertIsNone(product.category)

    def test_product_str(self):
        """Test product string representation"""
        expected = f'Laptop has a price of {Decimal("999.99")}'
        self.assertEqual(str(self.product), expected)


class ReviewModelTest(TestCase):
    """Test Review model with rating and constraints"""

    def setUp(self):
        """Create test user, category, product"""
        self.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=self.category
        )

    def test_review_creation(self):
        """Test review is created successfully"""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            review='Excellent product!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review, 'Excellent product!')

    def test_review_rating_choices(self):
        """Test all rating choices are valid"""
        for rating_value, _ in Review.RATING_CHOICES:
            review = Review.objects.create(
                product=self.product,
                user=self.user,
                rating=rating_value,
                review=f'Rating {rating_value}'
            )
            self.assertEqual(review.rating, rating_value)

    def test_review_unique_per_user_product(self):
        """Test one review per user per product constraint"""
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            review='First review'
        )
        with self.assertRaises(Exception):
            Review.objects.create(
                product=self.product,
                user=self.user,
                rating=3,
                review='Duplicate review'
            )

    def test_review_different_users_same_product(self):
        """Test different users can review same product"""
        user2 = User.objects.create_user(
            username='reviewer2',
            email='reviewer2@example.com',
            password='testpass123'
        )
        review1 = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            review='Great!'
        )
        review2 = Review.objects.create(
            product=self.product,
            user=user2,
            rating=4,
            review='Good!'
        )
        self.assertEqual(Review.objects.filter(product=self.product).count(), 2)

    def test_review_str(self):
        """Test review string representation"""
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            review='Excellent!'
        )
        self.assertIn(self.user.username, str(review))
        self.assertIn(self.product.name, str(review))


class ProductRatingModelTest(TestCase):
    """Test ProductRating auto-update functionality"""

    def setUp(self):
        """Create test user, category, product"""
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=self.category
        )

    def test_product_rating_created_on_review(self):
        """Test ProductRating is created when first review added"""
        self.assertFalse(ProductRating.objects.filter(product=self.product).exists())
        
        Review.objects.create(
            product=self.product,
            user=self.user1,
            rating=5,
            review='Excellent!'
        )
        
        self.assertTrue(ProductRating.objects.filter(product=self.product).exists())

    def test_product_rating_average_single_review(self):
        """Test average rating with single review"""
        Review.objects.create(
            product=self.product,
            user=self.user1,
            rating=5,
            review='Perfect!'
        )
        
        rating = ProductRating.objects.get(product=self.product)
        self.assertEqual(rating.average_rating, 5.0)
        self.assertEqual(rating.total_reviews, 1)

    def test_product_rating_average_multiple_reviews(self):
        """Test average rating with multiple reviews"""
        Review.objects.create(
            product=self.product,
            user=self.user1,
            rating=5,
            review='Excellent!'
        )
        Review.objects.create(
            product=self.product,
            user=self.user2,
            rating=3,
            review='Average'
        )
        
        rating = ProductRating.objects.get(product=self.product)
        self.assertEqual(rating.average_rating, 4.0)
        self.assertEqual(rating.total_reviews, 2)

    def test_product_rating_update_on_review_update(self):
        """Test rating updates when review is updated"""
        review = Review.objects.create(
            product=self.product,
            user=self.user1,
            rating=5,
            review='Great!'
        )
        
        rating = ProductRating.objects.get(product=self.product)
        self.assertEqual(rating.average_rating, 5.0)
        
        review.rating = 3
        review.save()
        
        rating.refresh_from_db()
        self.assertEqual(rating.average_rating, 3.0)

    def test_product_rating_update_on_review_delete(self):
        """Test rating updates when review is deleted"""
        review1 = Review.objects.create(
            product=self.product,
            user=self.user1,
            rating=5,
            review='Good!'
        )
        Review.objects.create(
            product=self.product,
            user=self.user2,
            rating=3,
            review='Average'
        )
        
        review1.delete()
        
        rating = ProductRating.objects.get(product=self.product)
        self.assertEqual(rating.average_rating, 3.0)
        self.assertEqual(rating.total_reviews, 1)

    def test_product_rating_str(self):
        """Test ProductRating string representation"""
        Review.objects.create(
            product=self.product,
            user=self.user1,
            rating=5,
            review='Excellent!'
        )
        
        rating = ProductRating.objects.get(product=self.product)
        self.assertIn(self.product.name, str(rating))
        self.assertIn('5.0', str(rating))


class ProductListAPITest(APITestCase):
    """Test Product list endpoint"""

    def setUp(self):
        """Create test products"""
        category = Category.objects.create(name='Electronics')
        
        self.featured_product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=category,
            featured=True
        )
        
        self.not_featured = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('29.99'),
            category=category,
            featured=False
        )

    def test_product_list_only_featured(self):
        """Test product list returns only featured products"""
        response = self.client.get(api_url('products/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Laptop')

    def test_featured_product_fields(self):
        """Test featured product contains required fields"""
        response = self.client.get(api_url('products/'))
        product = response.data[0]
        self.assertIn('id', product)
        self.assertIn('name', product)
        self.assertIn('price', product)
        self.assertIn('slug', product)


class ProductDetailAPITest(APITestCase):
    """Test Product detail endpoint"""

    def setUp(self):
        """Create test product"""
        category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop computer',
            price=Decimal('999.99'),
            category=category
        )

    def test_get_product_detail(self):
        """Test retrieving product by slug"""
        response = self.client.get(api_url(f'products/{self.product.slug}/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Laptop')
        self.assertEqual(response.data['slug'], 'laptop')

    def test_product_detail_includes_description(self):
        """Test product detail includes description"""
        response = self.client.get(api_url(f'products/{self.product.slug}/'))
        self.assertIn('description', response.data)
        self.assertEqual(response.data['description'], 'A powerful laptop computer')

    def test_product_detail_nonexistent(self):
        """Test 404 for nonexistent product"""
        response = self.client.get(api_url('products/nonexistent-product/'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class CategoryListAPITest(APITestCase):
    """Test Category list endpoint"""

    def setUp(self):
        """Create test categories"""
        self.category1 = Category.objects.create(name='Electronics')
        self.category2 = Category.objects.create(name='Books')

    def test_category_list(self):
        """Test listing all categories"""
        response = self.client.get(api_url('categories/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_category_list_fields(self):
        """Test category list contains required fields"""
        response = self.client.get(api_url('categories/'))
        category = response.data[0]
        self.assertIn('id', category)
        self.assertIn('name', category)
        self.assertIn('slug', category)


class CategoryDetailAPITest(APITestCase):
    """Test Category detail endpoint"""

    def setUp(self):
        """Create test category with products"""
        self.category = Category.objects.create(name='Electronics')
        self.product1 = Product.objects.create(
            name='Laptop',
            description='Powerful laptop',
            price=Decimal('999.99'),
            category=self.category
        )
        self.product2 = Product.objects.create(
            name='Mouse',
            description='Wireless mouse',
            price=Decimal('29.99'),
            category=self.category
        )

    def test_get_category_detail(self):
        """Test retrieving category by slug"""
        response = self.client.get(api_url(f'categories/{self.category.slug}/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Electronics')

    def test_category_detail_includes_products(self):
        """Test category detail includes product IDs"""
        response = self.client.get(api_url(f'categories/{self.category.slug}/'))
        self.assertIn('products', response)
        self.assertEqual(len(response.data['products']), 2)


class ReviewAPITest(APITestCase):
    """Test Review creation, update, delete endpoints"""

    def setUp(self):
        """Create test user, category, product"""
        self.user = User.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Laptop',
            description='A powerful laptop',
            price=Decimal('999.99'),
            category=self.category
        )
        self.client.force_authenticate(user=self.user)

    def test_create_review(self):
        """Test creating a review"""
        data = {
            'rating': 5,
            'review': 'Excellent product!'
        }
        response = self.client.post(
            api_url(f'products/{self.product.id}/review/'),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Review.objects.filter(product=self.product).exists())

    def test_create_duplicate_review_fails(self):
        """Test creating duplicate review returns 409"""
        data = {
            'rating': 5,
            'review': 'Great product!'
        }
        self.client.post(api_url(f'products/{self.product.id}/review/'), data)
        response = self.client.post(api_url(f'products/{self.product.id}/review/'), data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_update_review(self):
        """Test updating a review"""
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=3,
            review='Good'
        )
        
        data = {
            'rating': 5,
            'review': 'Changed my mind, excellent!'
        }
        response = self.client.put(
            api_url(f'products/{self.product.id}/review/'),
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        review = Review.objects.get(product=self.product, user=self.user)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.review, 'Changed my mind, excellent!')

    def test_delete_review(self):
        """Test deleting a review"""
        Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            review='Excellent'
        )
        
        response = self.client.delete(api_url(f'products/{self.product.id}/review/'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Review.objects.filter(product=self.product).exists())


class ProductSearchAPITest(APITestCase):
    """Test Product search endpoint"""

    def setUp(self):
        """Create test products"""
        category = Category.objects.create(name='Electronics')
        
        self.product1 = Product.objects.create(
            name='Laptop Computer',
            description='Powerful computing device',
            price=Decimal('999.99'),
            category=category
        )
        
        self.product2 = Product.objects.create(
            name='Wireless Mouse',
            description='Laptop accessory - precision mouse',
            price=Decimal('29.99'),
            category=category
        )

    def test_search_by_name(self):
        """Test searching product by name"""
        response = self.client.get(api_url('products/search/?query=Laptop'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_search_by_description(self):
        """Test searching product by description"""
        response = self.client.get(api_url('products/search/?query=computing'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_search_no_results(self):
        """Test search with no matching results"""
        response = self.client.get(api_url('products/search/?query=nonexistent'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_search_case_insensitive(self):
        """Test search is case insensitive"""
        response = self.client.get(api_url('products/search/?query=laptop'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
