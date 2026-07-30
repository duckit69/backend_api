from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Product, Category, Review
from .serializers import ProductListSerializer, ProductDetailSerializer, CategoryListSerializer, CategoryDetailSerializer, ReviewSerializer

@api_view(['GET'])
def product_list(request):
    featured_products = Product.objects.filter(featured = True)
    serializer = ProductListSerializer(featured_products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail(request, slug):
    product = Product.objects.get(slug=slug)
    serializer = ProductDetailSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
def category_list(request):
    category_list = Category.objects.all()
    serializer = CategoryListSerializer(category_list, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def category_detail(request, slug):
    category = Category.objects.get(slug=slug)
    serializer = CategoryDetailSerializer(category)
    return Response(serializer.data)

@api_view(['POST'])
def add_review(request, product_id):
    user = request.user
    rating = request.data.get('rating')
    review = request.data.get('review')

    product = Product.objects.get(id=product_id)

    review_obj = Review.objects.create(product=product, user=user, rating = rating, review = review)
    serializer = ReviewSerializer(review_obj)

    return Response(serializer.data)
