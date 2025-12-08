"""
Account views for user authentication, registration, and profile management.

Handles user registration, login, logout, profile editing, and admin dashboard.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F, Sum

from diet_plans.services import DietPlanGenerator
from orders.models import Order
from products.models import Supplement, ProteinBar

from .forms import UserRegistrationForm, ProfileForm
from .models import Profile, User


@require_http_methods(["GET", "POST"])
def register(request):
    """
    Handle user registration.

    Creates new user account and sends welcome email.
    Redirects authenticated users to dashboard.
    """
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')

            try:
                welcome_message = (
                    f'Hi {username},\n\n'
                    'Welcome to Diet Planner! '
                    'Your account has been successfully created.'
                )
                send_mail(
                    'Welcome to Diet Planner',
                    welcome_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except (ConnectionError, TimeoutError, OSError):
                # Email sending failed, but don't block user registration
                pass

            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@require_http_methods(["GET", "POST"])
def user_login(request):
    """
    Handle user login.

    Authenticates user and redirects to appropriate dashboard
    (admin or regular user dashboard).
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('accounts:admin_dashboard')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('accounts:admin_dashboard')
            return redirect('accounts:dashboard')
        messages.error(request, 'Invalid username or password.')

    return render(request, 'accounts/login.html')


@login_required
def dashboard(request):
    """
    Display user dashboard with profile and diet plan information.

    Shows user's profile details and generated diet plan if available.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)
    diet_plan = None

    if profile.fitness_goal:
        diet_plan = request.user.diet_plans.filter(goal_type=profile.fitness_goal).first()
        if not diet_plan:
            generator = DietPlanGenerator(profile)
            diet_plan = generator.generate()

    context = {
        'profile': profile,
        'diet_plan': diet_plan,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def select_goal(request):
    """
    Allow user to select fitness goal and generate diet plan.

    Creates or updates user's fitness goal and generates personalized diet plan.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        goal = request.POST.get('goal')
        if goal in ['weight_loss', 'weight_gain']:
            profile.fitness_goal = goal
            profile.save()

            generator = DietPlanGenerator(profile)
            diet_plan = generator.generate()

            if diet_plan:
                goal_display = goal.replace("_", " ").title()
                messages.success(
                    request,
                    f'Your {goal_display} diet plan has been generated!'
                )
                return redirect('accounts:dashboard')
            messages.error(
                request,
                'Please complete your profile information first.'
            )
            return redirect('accounts:edit_profile')

    return render(request, 'accounts/select_goal.html', {'profile': profile})


@login_required
@require_http_methods(["GET", "POST"])
def edit_profile(request):
    """
    Handle user profile editing.

    Allows users to update their profile information including
    physical attributes and fitness goals.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')

            if profile.fitness_goal:
                generator = DietPlanGenerator(profile)
                generator.generate()

            return redirect('accounts:dashboard')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'form': form, 'profile': profile})


@login_required
@require_http_methods(["POST"])
def user_logout(request):
    """
    Handle user logout.

    Logs out the current user and redirects to login page.
    """
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')


def is_admin(user):
    """
    Check if user is an admin.

    Args:
        user: User instance to check

    Returns:
        bool: True if user is authenticated and staff, False otherwise
    """
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Display admin dashboard with system statistics.

    Shows total users, products, orders, revenue, and low stock alerts.
    """
    total_users = User.objects.filter(is_customer=True).count()
    total_products = Supplement.objects.count() + ProteinBar.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()

    low_stock_supplements = Supplement.objects.filter(stock_quantity__lte=F('threshold'))
    low_stock_bars = ProteinBar.objects.filter(stock_quantity__lte=F('threshold'))
    total_low_stock = low_stock_supplements.count() + low_stock_bars.count()

    recent_orders = Order.objects.order_by('-order_date')[:5]

    order_statuses = ['processing', 'shipped', 'delivered']
    total_revenue = Order.objects.filter(
        status__in=order_statuses
    ).aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    context = {
        'total_users': total_users,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_low_stock': total_low_stock,
        'recent_orders': recent_orders,
        'total_revenue': total_revenue,
        'low_stock_supplements': low_stock_supplements[:5],
        'low_stock_bars': low_stock_bars[:5],
    }
    return render(request, 'accounts/admin_dashboard.html', context)


#