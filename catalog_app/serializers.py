from rest_framework import serializers
from .models import Product, Category

class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'price', 'image']

class ProductDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description','price', 'image']


class CategoryDetailSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'products', 'image']

class CategoryListSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'slug']