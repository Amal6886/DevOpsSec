from celery import shared_task
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.conf import settings
from products.models import Supplement, ProteinBar

User = get_user_model()


@shared_task
def send_stock_alert_email(product_id, content_type_id):
    try:
        content_type = ContentType.objects.get(id=content_type_id)
        model_class = content_type.model_class()

        if model_class == Supplement:
            product = Supplement.objects.get(id=product_id)
        elif model_class == ProteinBar:
            product = ProteinBar.objects.get(id=product_id)
        else:
            return

        subject = f'Stock Alert: {product.name} is running low'
        message = f"""
        Product: {product.name}
        Current Stock: {product.stock_quantity}
        Threshold: {product.threshold}

        Please restock this product as soon as possible.
        """

        admin_emails = [user.email for user in User.objects.filter(is_staff=True)]

        if admin_emails:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=False,
            )
    except (ContentType.DoesNotExist, Supplement.DoesNotExist, ProteinBar.DoesNotExist):
        # Product or content type not found, skip email
        pass
    except (ConnectionError, TimeoutError, OSError) as e:
        # Email sending failed
        print(f"Error sending stock alert email: {e}")
