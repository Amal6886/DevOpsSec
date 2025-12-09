import os
import django
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diet_planner.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

try:
    send_mail(
        'Test Email',
        'This is a test email from Diet Planner.',
        settings.DEFAULT_FROM_EMAIL,  # Use Django's setting instead of hardcoded
        ['amalpaulgdr@gmail.com'],  # Change this to your actual email
        fail_silently=False,
    )
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error: {e}")