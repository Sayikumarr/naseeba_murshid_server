from django.contrib import admin
from .models import Image,ArtRequirement, Member,OrderStatus, PaymentScreenshot, BlogPost
# Register your models here.

admin.site.register(Image)
admin.site.register(ArtRequirement)
admin.site.register(Member)
admin.site.register(OrderStatus)
admin.site.register(PaymentScreenshot)
admin.site.register(BlogPost)
