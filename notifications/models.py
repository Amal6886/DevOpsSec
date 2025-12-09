"""
Notification models for stock alerts.

Tracks low stock alerts and prevents duplicate email notifications.
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class StockAlert(models.Model):
    """
    Model to track stock alerts for products.

    Uses generic foreign key to work with any product type.
    Prevents duplicate email alerts using the alert_sent flag.
    """
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    alert_sent = models.BooleanField(default=False)
    alert_date = models.DateTimeField(auto_now_add=True)
    message = models.TextField()

    class Meta:
        ordering = ['-alert_date']
        unique_together = ['content_type', 'object_id']

    def __str__(self):
        return f"Alert for {self.product} - {self.alert_date}"
