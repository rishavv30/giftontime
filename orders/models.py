from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('purchased', 'Purchased'),
        ('delivered', 'Delivered'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    product_link = models.URLField()
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    address = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"
