from django.db import models
from catalog_app.models import Product
from user_app.models import User
# Create your models here.
class Cart(models.Model):
    cart_code = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cart_code


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='item')
    quantity = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} with {self.quantity} in + {self.cart.cart_code}"


# it will be more better if we add another class for wishlist item 
# and control extra informations such as quantity and date it has been added
class WishList(models.Model):
    product = models.ManyToManyField(Product, related_name='wishlists')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)