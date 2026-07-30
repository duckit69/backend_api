from django.db import models
from catalog_app.models import Product
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



