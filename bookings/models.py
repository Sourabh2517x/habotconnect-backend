from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel

class Parent(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="parent_profile",)
    phone_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username
    
    
class Skill(TimeStampedModel):
    name = models.CharField(max_length=100,unique=True,)

    def __str__(self):
        return self.name
    
    
class LSAProfile(TimeStampedModel):
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill,related_name="lsa_profiles",blank=True,)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    
class BookingStatus(models.TextChoices):
    PENDING_PAYMENT = "pending_payment", "Pending Payment"
    CONFIRMED = "confirmed", "Confirmed"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    FAILED = "failed", "Failed"
    
    
class BookingRequest(TimeStampedModel):
    parent = models.ForeignKey(Parent,on_delete=models.PROTECT,related_name="bookings",)
    lsa = models.ForeignKey(LSAProfile,on_delete=models.PROTECT,related_name="bookings",)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=30,choices=BookingStatus.choices,default=BookingStatus.PENDING_PAYMENT,)
    notes = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(
                fields=["lsa", "start_time", "end_time"],
                name="booking_lsa_time_idx",
            ),
            models.Index(
                fields=["parent", "start_time"],
                name="booking_parent_time_idx",
            ),
            models.Index(
                fields=["status"],
                name="booking_status_idx",
            ),
        ]

    def __str__(self):return (
            f"{self.parent} - "
            f"{self.lsa} - "
            f"{self.start_time}"
        )
    
class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SUCCESS = "success", "Success"
    FAILED = "failed", "Failed"
    

class Payment(TimeStampedModel):
    booking = models.OneToOneField(BookingRequest,on_delete=models.PROTECT,related_name="payment",)
    transaction_id = models.CharField(max_length=100,unique=True,)
    amount = models.DecimalField(max_digits=10,decimal_places=2,)
    currency = models.CharField(max_length=3,default="INR",)
    status = models.CharField(max_length=20,choices=PaymentStatus.choices,default=PaymentStatus.PENDING,)
    gateway_response = models.JSONField(default=dict,blank=True,)

    class Meta:
        indexes = [
            models.Index(
                fields=["status"],
                name="payment_status_idx",
            ),
        ]

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"
    
