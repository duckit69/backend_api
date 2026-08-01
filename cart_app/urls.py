from django.urls import path

from . import views

urlpatterns = [
    path('<int:cart_code>/items/', view=views.cart_item_manager, name='add_item_to_cart'),
    path('<int:cart_code>/items/<int:item_id>/', view=views.update_cart_item_quantity, name='udpate_cart_item_quantity'),
    path('wishlist/<int:product_id>/', view=views.toggle_wishlist, name='toggle_wishlist')
]