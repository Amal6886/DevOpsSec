import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diet_planner.settings')
django.setup()

from django.core.mail import send_mail

try:
    send_mail(
        'Test Email',
        'This is a test email from Diet Planner.',
        'noreply@dietplanner.com',
        ['your-email@example.com'],
        fail_silently=False,
    )
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")