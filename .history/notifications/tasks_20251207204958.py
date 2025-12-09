"""
Email notification tasks for stock alerts.

Uses threading to send emails asynchronously without blocking the main request.
No Celery or Redis required - simple and lightweight solution for MVP.
"""
import threading
import logging
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.conf import settings
from products.models import Supplement, ProteinBar

User = get_user_model()
logger = logging.getLogger(__name__)


def send_stock_alert_email(product_id, content_type_id):
    """
    Send stock alert email to all admin users.

    This function runs in a separate thread to avoid blocking the main request.

    Args:
        product_id: ID of the product with low stock
        content_type_id: ContentType ID for the product model
    """
    try:
        content_type = ContentType.objects.get(id=content_type_id)
        model_class = content_type.model_class()

        if model_class == Supplement:
            product = Supplement.objects.get(id=product_id)
        elif model_class == ProteinBar:
            product = ProteinBar.objects.get(id=product_id)
        else:
            logger.warning(
                f"Unknown product type for content_type_id: {content_type_id}"
            )
            return

        subject = f'Stock Alert: {product.name} is running low'
        message = f"""Dear Admin,

This is an automated stock alert notification.

Product: {product.name}
Current Stock: {product.stock_quantity}
Threshold: {product.threshold}
Status: LOW STOCK - Please restock as soon as possible.

You can manage products in the admin panel.

Best regards,
Diet Planner System""".strip()

        # Get all admin user emails
        admin_emails = [
            user.email for user in User.objects.filter(is_staff=True)
        ]

        if not admin_emails:
            logger.warning("No admin users found to send stock alert email")
            return

        # Send email to all admins
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            admin_emails,
            fail_silently=False,
        )

        logger.info(
            f"Stock alert email sent successfully for product: {product.name} "
            f"to {len(admin_emails)} admin(s)"
        )

    except (ContentType.DoesNotExist, Supplement.DoesNotExist,
            ProteinBar.DoesNotExist) as e:
        logger.error(f"Product or content type not found: {e}")
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.error(f"Network error sending stock alert email: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected error sending stock alert email: {e}",
            exc_info=True
        )


def send_stock_alert_email_async(product_id, content_type_id):
    """
    Send stock alert email in a background thread to avoid blocking the request.

    This is a wrapper function that creates a thread for email sending.
    The thread is daemon, so it will die when the main process exits.

    Args:
        product_id: ID of the product with low stock
        content_type_id: ContentType ID for the product model
    """
    thread = threading.Thread(
        target=send_stock_alert_email,
        args=(product_id, content_type_id),
        daemon=True  # Thread will die when main process exits
    )
    thread.start()
    logger.debug(
        f"Started background thread for sending stock alert email "
        f"(product_id: {product_id})"
    )
