from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Product, Category
from .serializers import ProductListSerializer, ProductDetailSerializer, CategoryListSerializer, CategoryDetailSerializer

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