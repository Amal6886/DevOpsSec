"""
URL configuration for the diet_planner project.

Defines URL patterns for all apps and handles root URL redirection.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def home_redirect(request):
    """
    Redirect root URL based on user authentication status.

    Redirects authenticated staff to admin dashboard,
    authenticated users to user dashboard,
    and unauthenticated users to login page.
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('accounts:admin_dashboard')
        return redirect('accounts:dashboard')
    return redirect('accounts:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
