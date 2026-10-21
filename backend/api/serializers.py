from rest_framework import serializers
from .models import BlogItem


class BlogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogItem
        fields = '__all__'

class BlogItemShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogItem
        exclude = ['text']
