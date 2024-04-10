from rest_framework import viewsets
from .models import Image
from .serializers import ImageSerializer

class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = serializer.data
        response_data['image_url'] = request.build_absolute_uri(instance.image.url)
        return Response(response_data)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ArtRequirement, Member, OrderStatus

@csrf_exempt
def submit_art_requirement(request):
    if request.method == 'POST':
        # Access form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phoneNumber')
        combined_description = request.POST.get('combinedDescription')
        background_image = request.FILES.get('backgroundImage')

        # Create ArtRequirement instance
        art_requirement = ArtRequirement.objects.create(
            name=name,
            email=email,
            phone_number=phone_number,
            combined_description=combined_description,
            background_image=background_image
        )
        # Process members data
        count = 0
        for key, value in request.POST.items():
            if key.startswith('members'):
                member = Member.objects.create(
                    photo=request.FILES.get(f'members[{count}][photo]'),
                    dress=request.FILES.get(f'members[{count}][dress]'),
                    description = request.POST.get(key))
                art_requirement.members.add(member)
                count+=1
        total = count*2000
        oder_status=OrderStatus(requirement=art_requirement,total=total,paid=0)
        oder_status.save()

        # Return a JSON response indicating success
        return JsonResponse({'message': 'Form submitted successfully!','tracking_id':oder_status.tracking_number})
    else:
        # Return an error response if request method is not POST
        return JsonResponse({'error': 'Only POST requests are allowed!'}, status=405)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import OrderStatus,PaymentScreenshot, Contact
from .serializers import OrderStatusSerializer, ContactSerializer
import json

class OrderStatusByTrackingAPIView(APIView):
    def get(self, request, tracking_number):
        try:
            order_status = OrderStatus.objects.get(tracking_number=tracking_number)
            serializer = OrderStatusSerializer(order_status)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OrderStatus.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request):
        body=json.loads(request.body)
        order = body.get("orderId")
        mobile = body.get("mobileNumber")
        try:
            verifyObject = ArtRequirement.objects.get(id=order)
            if verifyObject.phone_number == mobile:
                track_status = OrderStatus.objects.get(requirement=verifyObject)
                try:
                    order_status = OrderStatus.objects.get(tracking_number=track_status.tracking_number)
                    serializer = OrderStatusSerializer(order_status)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                except OrderStatus.DoesNotExist:
                    return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt   
def paymentScreenShot(request):
    if request.method == 'POST':
        # Get the form data
        screenshot = request.FILES.get("screenshot")
        tracker_id = request.POST.get("tracker_id")
        # Create a new OrderStatus object
        if (screenshot is None) or (tracker_id is None):
            print("not sent Files")
            return JsonResponse({'success': False}, status=status.HTTP_404_NOT_FOUND)
        try:
            order_status = OrderStatus.objects.get(tracking_number=tracker_id)
        except:
            return JsonResponse({'success': False},  status=status.HTTP_404_NOT_FOUND)
        payscreenshot = PaymentScreenshot(order_status=order_status)
        payscreenshot.payment_screenshot = screenshot
        payscreenshot.save()

        # Return a success response
        return JsonResponse({'success': True})

    # Return an error response if the request method is not POST
    return JsonResponse({'success': False}, status=status.HTTP_404_NOT_FOUND)


class ContactCreateView(APIView):
    def post(self, request, format=None):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
