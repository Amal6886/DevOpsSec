"""
Django signals for product stock monitoring.

Automatically sends email alerts when product stock goes low.
Implements smart alert logic that resets when stock recovers.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from products.models import Supplement, ProteinBar
from .models import StockAlert
from .tasks import send_stock_alert_email_async


@receiver(post_save, sender=Supplement)
@receiver(post_save, sender=ProteinBar)
def check_stock_level(instance, **kwargs):
    """
    Signal handler that checks if product stock is low and sends email alert.

    Logic:
    1. If stock is LOW: Check if alert already sent
       - If NOT sent: Send email and mark as sent
       - If already sent: Do nothing (prevent duplicates)
    2. If stock is ABOVE threshold: Reset alert_sent flag
       - This allows re-alerting if stock goes low again later

    Args:
        instance: The product instance (Supplement or ProteinBar) being saved
        **kwargs: Additional signal arguments
    """
        content_type = ContentType.objects.get_for_model(instance)
    is_low = instance.is_low_stock()

    # Get or create stock alert record
        alert, created = StockAlert.objects.get_or_create(
            content_type=content_type,
            object_id=instance.pk,
            defaults={
            'message': (
                f"{instance.name} stock is low "
                f"({instance.stock_quantity} remaining). "
                f"Threshold: {instance.threshold}"
            ),
            }
        )

    if is_low:
        # Stock is low - send email if not already sent
        if created or not alert.alert_sent:
            # Send email in background thread (non-blocking)
            send_stock_alert_email_async(instance.pk, content_type.id)
            alert.alert_sent = True
            alert.save()
    else:
        # Stock is above threshold - reset flag for future alerts
        if alert.alert_sent:
            alert.alert_sent = False
            alert.save()
