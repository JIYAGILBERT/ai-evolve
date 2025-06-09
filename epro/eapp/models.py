from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils.translation import gettext_lazy as _
from .constants import PaymentStatus

class Gallery(models.Model):
    feedimage = models.ImageField(upload_to='gallery_images/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    model=models.CharField(max_length=400)
    
    discription=models.TextField(max_length=400, null=True, blank=True)
    offers=models.CharField(max_length=400, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
     
    # delivary = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    
    image1=models.FileField(upload_to='gallery_images/', null=True, blank=True)
    image2=models.FileField(upload_to='gallery_images/', null=True, blank=True)
    image3=models.FileField(upload_to='gallery_images/', null=True, blank=True)


    rating=models.FloatField(default=0)
    vector_data=models.TextField(null=True)

    def __str__(self):
        return self.name
class users(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vector_data=models.TextField(null=True)
    
    def __str__(self):
        return self.user.username


class ViewHistory(models.Model):
    product=models.ForeignKey(Gallery,on_delete=models.CASCADE)
    user=models.ForeignKey(users,on_delete=models.CASCADE)
    
class SearchHistory(models.Model):
    query = models.CharField(max_length=255)
    user = models.ForeignKey(users, on_delete=models.CASCADE)


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.quantity} of {self.product.name}'
    
    
class Order(models.Model):
    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('ONLINE', 'Online Payment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Gallery, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()  # Address input
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='COD')
    status = models.CharField(max_length=50, default="Pending")  # Status: Pending, Completed, Cancelled
    created_at = models.DateTimeField(auto_now_add=True)
    
   
    
    # status = models.CharField(
    #     max_length=50,
    #     default=PaymentStatus.PENDING,
    #     choices=[
    #         (PaymentStatus.PENDING, 'Pending'),
    #         (PaymentStatus.COMPLETED, 'Completed'),
    #         (PaymentStatus.CANCELLED, 'Cancelled'),
    #     ]
    # )
    
    provider_order_id=models.CharField(
        _(" Order ID"),max_length=40,blank=True,null=True
        )
    payment_id=models.CharField(
        _("Payment ID"),max_length=36,blank=True,null=True
    )
    signature_id=models.CharField(
        _("Signature ID"),max_length=128,blank=True,null=True
    )

    def __str__(self):
        return f'Order {self.id} - {self.product.name} - {self.status}'
    
    
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     address = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return self.user.username


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=225)
    address=models.TextField()
    phone=models.CharField(max_length=12)



class reviews(models.Model):
    rating=models.IntegerField()
    description=models.TextField()
    uname=models.ForeignKey(users,on_delete=models.CASCADE)
    pname=models.ForeignKey(Gallery,on_delete=models.CASCADE)    
    
    
    
    
    
    

    
    
    