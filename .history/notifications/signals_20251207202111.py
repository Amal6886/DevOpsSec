from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from products.models import Supplement, ProteinBar
from .models import StockAlert
from .tasks import send_stock_alert_email


@receiver(post_save, sender=Supplement)
@receiver(post_save, sender=ProteinBar)
def check_stock_level(instance, **kwargs):
    if instance.is_low_stock():
        content_type = ContentType.objects.get_for_model(instance)

        alert, created = StockAlert.objects.get_or_create(
            content_type=content_type,
            object_id=instance.pk,
            defaults={
                'message': f"{instance.name} stock is low ({instance.stock_quantity} remaining). Threshold: {instance.threshold}",
            }
        )

        if created or not alert.alert_sent:
            send_stock_alert_email.delay(instance.pk, content_type.id)
            alert.alert_sent = True
            alert.save()
