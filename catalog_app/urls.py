from django.urls import path

from . import views
urlpatterns = [
    path('products', views.product_list, name='product_list'),
    path('products/<slug:slug>', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/reviews/', views.add_review, name='add_review'),
    path('categories', views.category_list, name='category_list'),
    path('categories/<slug:slug>', views.category_detail, name='category_detail'),
]
