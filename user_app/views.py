from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import User
from .serializers import UserSerializer

@api_view(['GET'])
def list(request):
    user_list = User.objects.all()
    serializer = UserSerializer(user_list, many=True)
    return Response(serializer.data)