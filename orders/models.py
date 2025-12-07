from django.db import models
from accounts.models import User
from products.models import Supplement, ProteinBar


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    phone = models.CharField(max_length=15)

    class Meta:
        ordering = ['-order_date']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    supplement = models.ForeignKey(Supplement, on_delete=models.SET_NULL, null=True, blank=True)
    protein_bar = models.ForeignKey(ProteinBar, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def product(self):
        return self.supplement or self.protein_bar

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        product_name = self.supplement.name if self.supplement else self.protein_bar.name
        return f"{product_name} x{self.quantity}"
