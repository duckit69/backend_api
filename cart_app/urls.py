from django.urls import path

from . import views

urlpatterns = [
    path('<int:cart_code>/items/', view=views.cart_item_manager, name='add_remove_item_from_cart'),
    path('checkout/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', views.my_webhook_view, name='webhook'),
    path('<int:cart_code>/items/<int:item_id>/', view=views.update_cart_item_quantity, name='udpate_cart_item_quantity'),
    path('wishlist/<int:product_id>/', view=views.toggle_wishlist, name='toggle_wishlist'),
]