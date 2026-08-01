from django.urls import path

from . import views
urlpatterns = [
    path('products', views.product_list, name='product_list'),
    path('products/search', views.product_search, name='product_search'),
    path('products/<slug:slug>', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/reviews/', views.review_manager, name='add_review'),
    path('categories', views.category_list, name='category_list'),
    path('categories/<slug:slug>', views.category_detail, name='category_detail'),
]
