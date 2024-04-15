
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

class Image(models.Model):
    image = models.FileField(upload_to='images/instaPosts/')
    alt_text = models.CharField(max_length=255)

    def __str__(self):
        return self.alt_text



class ArtRequirement(models.Model):
  name = models.CharField(max_length=255)
  email = models.EmailField()
  phone_number = models.CharField(max_length=20)
  background_image = models.ImageField(upload_to='images/backgrounds/')
  combined_description = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.id} - {self.name}"


class Member(models.Model):
  requirement = models.ForeignKey(ArtRequirement, on_delete=models.CASCADE)
  photo = models.ImageField(upload_to='images/members/')  # Optional photo
  dress = models.ImageField(upload_to='images/dresses/')  # Optional dress image
  description = models.TextField(blank=True)  # Optional description


import random
import string
from django.db import models
import string
import random

class OrderStatus(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Due', 'Due'),
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
    ]

    PRODUCT_STATUS_CHOICES = [
        ('Not Yet Confirmed','Not Yet Confirmed'),
        ('Confirmed', 'Confirmed'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    ]

    requirement = models.ForeignKey(ArtRequirement, on_delete=models.CASCADE)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    expected_date = models.DateField(blank=True,null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.DecimalField(max_digits=10, decimal_places=2)
    product_status = models.CharField(max_length=20, choices=PRODUCT_STATUS_CHOICES,default='Not Yet Confirmed')
    tracking_number = models.CharField(max_length=100, unique=True)
    remark = models.TextField(blank=True)

    def __str__(self):
        return f"OrderStatus for {self.requirement.id}"
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the object is being created
            self.tracking_number = self.generate_tracking_number()

        # Update payment status based on paid and total
        if self.paid == self.total:
            self.payment_status = 'Paid'
        elif self.paid < self.total:
            self.payment_status = 'Pending'
        elif self.paid == 0:
            self.payment_status = 'Due'

        super().save(*args, **kwargs)

    def generate_tracking_number(self):
        letters_and_digits = string.ascii_letters + string.digits
        tracking_number = ''.join(random.choice(letters_and_digits) for _ in range(10))
        return tracking_number


class PaymentScreenshot(models.Model):
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    payment_screenshot = models.ImageField(upload_to='images/payment_screenshots/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment Screenshot by {self.order_status.tracking_number} for Status: {self.order_status.product_status}"


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    message = models.TextField()

    def __str__(self):
        return self.name
