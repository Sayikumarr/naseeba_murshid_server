from rest_framework import serializers
from .models import Image, BlogPost, OrderStatus, Contact
from django.utils import timezone

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['image', 'alt_text']

class OrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatus
        fields = '__all__'


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'email', 'phone_number', 'message']


class BlogPostSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    author_photo = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ['art', 'author', 'content', 'image', 'author_photo', 'rating', 'created_at']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_author_photo(self, obj):
        request = self.context.get('request')
        if obj.author_photo:
            return request.build_absolute_uri(obj.author_photo.url)
        return None
    
    def get_created_at(self, obj):
        # Convert UTC time to Indian Standard Time (IST)
        created_at_ist = obj.created_at.astimezone(timezone.get_current_timezone())
        # Format the datetime as desired (Indian style)
        return created_at_ist.strftime('%d-%m-%Y %I:%M %p')