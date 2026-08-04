from django.contrib import admin

# Register your models here.
from .models import Cart, CartItem, Order, OrderItem, WishList

admin.site.register([Cart, CartItem, WishList, Order, OrderItem])