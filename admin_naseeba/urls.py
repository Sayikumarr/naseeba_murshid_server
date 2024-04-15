# urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ImageViewSet,submit_art_requirement,OrderStatusByTrackingAPIView,paymentScreenShot,ContactCreateView,sendtoAdmin,logout_view,admin_board,sendCustomer

router = DefaultRouter()
router.register(r'images', ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('submit-form/', ArtRequirementsFormAPIView.as_view(), name='submit_form'),
    path('submit-form/', submit_art_requirement, name='submit_art_requirement'),
    path('confirmation/<str:tracking_number>/',OrderStatusByTrackingAPIView.as_view()),
    path('confirmation/',OrderStatusByTrackingAPIView.as_view()),
    path('payment-screen-short/',paymentScreenShot,name='payment-screen-short'),
    path('contact/', ContactCreateView.as_view(), name='contact-create'),
    path('admin/',admin_board,name="admin_board"),
    path('admin/<int:id>',sendtoAdmin,name="order_detail"),
    path('admin/logout/', logout_view, name='logout'),
    path('customer/',sendCustomer)
    # path("sai",home),
]
