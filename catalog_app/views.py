from django.shortcuts import render
from django.db.models import Q
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

@api_view(['POST', 'PUT', 'DELETE'])
def review_manager(request, product_id):
    user = request.user
    rating = request.data.get('rating')
    review = request.data.get('review')

    product = Product.objects.get(id=product_id)

    if request.method == 'POST':
        if Review.objects.filter(user=user, product=product).exists():
            return Response( 
                    {
                        'error': 'You have already reviewed this product',
                        'message': 'Duplicate review not allowed',
                    },
                    status=409  
                )
        
        review_obj = Review.objects.create(product=product, user=user, rating = rating, review = review)

    elif request.method == 'PUT':
        review_obj = Review.objects.get(product=product, user=user)
        review_obj.rating = rating
        review_obj.review = review    
        review_obj.save()

    elif request.method == 'DELETE':
        review_obj = Review.objects.get(product=product, user=user)
        review_obj.delete()

    serializer = ReviewSerializer(review_obj)
    return Response(serializer.data)


@api_view(['GET'])
def product_search(request):
    query = request.query_params.get('query')

    # maybe it does not make sense to search category and product name 
    # just testing Q object and playing with | & ~
    products = Product.objects.filter(Q(name__icontains=query)
                                      | Q(description__icontains=query)
                                      | Q(category__name__name=query))

    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)