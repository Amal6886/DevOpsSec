"""
User account models for the Diet Planner application.

Defines custom user model and user profile with fitness goals.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    Adds email uniqueness and customer flag for user management.
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    is_customer = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    """
    User profile model storing fitness and health information.

    Contains user's physical attributes, activity level, and fitness goals
    used for generating personalized diet plans.
    """
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    ACTIVITY_LEVELS = [
        ('sedentary', 'Sedentary'),
        ('light', 'Lightly Active'),
        ('moderate', 'Moderately Active'),
        ('active', 'Very Active'),
        ('very_active', 'Extra Active'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    height = models.FloatField(null=True, blank=True, help_text='Height in cm')
    current_weight = models.FloatField(null=True, blank=True, help_text='Weight in kg')
    target_weight = models.FloatField(null=True, blank=True, help_text='Target weight in kg')
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_LEVELS, default='sedentary')
    fitness_goal = models.CharField(max_length=20, choices=GOAL_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
