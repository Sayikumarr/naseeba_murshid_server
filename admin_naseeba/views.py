from rest_framework import viewsets
from rest_framework.views import APIView
from .models import Image, BlogPost
from .serializers import ImageSerializer, BlogPostSerializer

class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = serializer.data
        response_data['image_url'] = request.build_absolute_uri(instance.image.url)
        return Response(response_data)

class BlogPostAPIView(APIView):
    def get(self, request, format=None):
        blog_posts = BlogPost.objects.all()
        serializer = BlogPostSerializer(blog_posts, many=True, context={'request': request})
        return Response(serializer.data)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ArtRequirement, Member, OrderStatus
from django.conf import settings
import asyncio
from django.core.mail import EmailMessage 

import base64

def generate_token(tracking_id):
    encoded_id = base64.b64encode(tracking_id.encode()).decode()
    return encoded_id

def decode_token(token):
    try:
        decoded_id = base64.b64decode(token.encode()).decode()
        return decoded_id
    except:
        return None


import threading
from django.core.mail import EmailMessage  # Use EmailMessage for flexibility

def send_email_async(subject, message, to_emails, from_email=settings.DEFAULT_FROM_EMAIL):
    try:
        def send_email_task():
            print("started!")
            email = EmailMessage(subject, message, from_email, to_emails)
            email.send(fail_silently=False)
            print("Mail sent!")

        thread = threading.Thread(target=send_email_task)
        thread.start()
        print("trying to send mail!")
    except Exception as e:
        print("Failed to send email. Error:", e)
    

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
        members_data = []
        count = 0
        for key, value in request.POST.items():
            if key.startswith('members'):
                member = Member.objects.create(
                    requirement=art_requirement,
                    photo=request.FILES.get(f'members[{count}][photo]'),
                    dress=request.FILES.get(f'members[{count}][dress]'),
                    description = request.POST.get(key))
                members_data.append(member)
                count+=1
        total = count*2000
        order_status=OrderStatus(requirement=art_requirement,total=total,paid=0)
        order_status.save()
        try:
            token = generate_token(order_status.tracking_number)
            # Send email to Customer
            send_email_async(
                subject="Confirmation: Your Request has been Received",
                message=f'''Dear {name},

We have received your request and will process it shortly.

Details:

Order ID: {art_requirement.id}
Tracking No. / Reference Number: {order_status.tracking_number}
For Complete Details Click on this Link : {settings.SERVER_URL}/api/customer/?token={token}
Thank you for choosing our service.

Sincerely,
Naseeba Murshid..''',to_emails=[email])
        
            # Send email to Admin
            send_email_async(
                subject=f"New Request Received #{order_status.tracking_number}",
                message=f'''Dear Naseeba,

A new request has been submitted online:

Details:

Order ID: {art_requirement.id}
Tracking No. / Reference Number: {order_status.tracking_number}
For Complete Details Click on this Link : {settings.SERVER_URL}/api/admin/{art_requirement.id}
Please review and take necessary actions.''',to_emails=[settings.ADMIN_EMAIL])
        except Exception as e:
            print(e)
        return JsonResponse({'message': 'Form submitted successfully!','tracking_id':order_status.tracking_number})
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

        art_requirement = order_status.requirement
        try:
            token = generate_token(order_status.tracking_number)
            # Send email to customer
            send_email_async(
                subject="Thank you for your Payment ScreenShot Submission",
                message=f'''Dear {art_requirement.name},

We have received your request and will process it shortly.

Details:

Order ID: {art_requirement.id}
Tracking No. / Reference Number: {order_status.tracking_number}
For Complete Details Click on this Link : {settings.SERVER_URL}/api/customer/?token={token}
Thank you for choosing our service.

Sincerely,
Naseeba Murshid..''',to_emails=[art_requirement.email])
        
            # Send email to Admin
            send_email_async(
                subject=f"New Payment ScreenShot Submission #{order_status.tracking_number}",
                message=f'''Dear Naseeba,

A new request has been submitted online:

Details:

Order ID: {art_requirement.id}
Tracking No. / Reference Number: {order_status.tracking_number}
For Complete Details Click on this Link : {settings.SERVER_URL}/api/admin/{art_requirement.id}
Please review and take necessary actions.''',to_emails=[settings.ADMIN_EMAIL])
        except Exception as e:
            print(e)
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


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def sendtoAdmin(request,id):
    try:
        art = ArtRequirement.objects.get(id=id)
        order_status = OrderStatus.objects.get(requirement = art)
        members_data = Member.objects.filter(requirement=art)
        screenshots = PaymentScreenshot.objects.filter(order_status=order_status)

        return render(request,"admin_order_template.html", {'art_requirement': art, 'order_status': order_status, 'members_data': members_data,'screenshots':screenshots,'SERVER_URL':settings.SERVER_URL})
    except:
        return render(request,"no-data-found.html")
    
    
@login_required
def admin_board(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        # Assuming you have a URL pattern named 'order_detail' for displaying order details
        return redirect('order_detail', id=order_id)  # Redirect to order detail page
    return render(request,'admin_board.html',{'SERVER_URL':settings.SERVER_URL})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('admin_board')


def sendCustomer(request):
    try:
        token = request.GET.get('token')
        tracking_id = decode_token(token)
        order_status = OrderStatus.objects.get(tracking_number=tracking_id)
        art = ArtRequirement.objects.get(id=order_status.requirement.id)
        members_data = Member.objects.filter(requirement=art)
        screenshots = PaymentScreenshot.objects.filter(order_status=order_status)
    except:
        return render(request,"no-data-found.html")

    return render(request,"user_order_template.html", {'art_requirement': art, 'order_status': order_status, 'members_data': members_data,'screenshots':screenshots,'SERVER_URL':settings.SERVER_URL})
