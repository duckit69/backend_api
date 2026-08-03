from django.db import models
from django.utils.text import slugify
# Create your models here.

from user_app.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='category_img', blank=True, null=True)
    # make sure slug is unnique after update and when first created
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            
            # while' to find the next available number
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
                
            self.slug = unique_slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    slug = models.SlugField()
    image = models.ImageField(upload_to="product_img", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            
            # while' to find the next available number
            while Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{counter}'
                counter += 1
                
            self.slug = unique_slug
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} has a price of {self.price}"

class Review(models.Model):

    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s review on this {self.product.name}"

    # this makes one relationship between user-product ( one review per user for product)
    class Meta:
        unique_together = ['user', 'product']
        # show recent reviews first
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # run this after creating
        self.update_product_rating()

    def update_product_rating(self):
        # Retrieve all reviews for this product
        reviews = Review.objects.filter(product= self.product)

        total_reviews = reviews.count()

        if total_reviews > 0:
            average_rating = sum(r.rating for r in reviews) / total_reviews
        else:
            average_rating = 0.0

        # Create or Udpate ProductRating
        product_rating, created = ProductRating.objects.get_or_create(product = self.product)
        product_rating.average_rating = round(average_rating, 2)
        product_rating.total_reviews = total_reviews
        product_rating.save()

    def delete(self, *args, **kwargs):

        super().delete(*args, **kwargs)
        reviews = Review.objects.filter(product=self.product)

        total_reviews = reviews.count()


        if total_reviews > 0:
            average_rating = sum(r.rating for r in reviews) / total_reviews
        else:
            average_rating = 0.0

        product_rating, created = ProductRating.objects.get_or_create(product = self.product)
        product_rating.average_rating = round(average_rating, 2)
        product_rating.total_reviews = total_reviews
        product_rating.save()
        



# seperate model to track the product ratings and average to reduce loading the entire product object every time
class ProductRating(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='rating')
    average_rating = models.FloatField(default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.average_rating} ({self.total_reviews} reviews)"

