from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import F, Sum

from diet_plans.services import DietPlanGenerator
from orders.models import Order
from products.models import Supplement, ProteinBar

from .forms import UserRegistrationForm, ProfileForm
from .models import Profile, User


def register(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')

            try:
                send_mail(
                    'Welcome to Diet Planner',
                    f'Hi {username},\n\nWelcome to Diet Planner! Your account has been successfully created.',
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


def user_login(request):
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
def select_goal(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        goal = request.POST.get('goal')
        if goal in ['weight_loss', 'weight_gain']:
            profile.fitness_goal = goal
            profile.save()

            generator = DietPlanGenerator(profile)
            diet_plan = generator.generate()

            if diet_plan:
                messages.success(request, f'Your {goal.replace("_", " ").title()} diet plan has been generated!')
                return redirect('accounts:dashboard')
            messages.error(request, 'Please complete your profile information first.')
            return redirect('accounts:edit_profile')

    return render(request, 'accounts/select_goal.html', {'profile': profile})


@login_required
def edit_profile(request):
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
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('accounts:login')


def is_admin(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = User.objects.filter(is_customer=True).count()
    total_products = Supplement.objects.count() + ProteinBar.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()

    low_stock_supplements = Supplement.objects.filter(stock_quantity__lte=F('threshold'))
    low_stock_bars = ProteinBar.objects.filter(stock_quantity__lte=F('threshold'))
    total_low_stock = low_stock_supplements.count() + low_stock_bars.count()

    recent_orders = Order.objects.order_by('-order_date')[:5]

    total_revenue = Order.objects.filter(status__in=['processing', 'shipped', 'delivered']).aggregate(
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
