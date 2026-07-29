from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
def list(request):
    featured_products = Product.objects.filter(features = True)
    serializer = ProductSerializer(featured_products, many=True)
    return Response(serializer.data)
    