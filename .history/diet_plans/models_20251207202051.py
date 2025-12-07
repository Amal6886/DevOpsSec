from django.db import models
from accounts.models import User


class DietPlan(models.Model):
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('weight_gain', 'Weight Gain'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='diet_plans')
    goal_type = models.CharField(max_length=20, choices=GOAL_CHOICES)
    daily_calories = models.IntegerField()
    meals = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s {self.goal_type} Plan"
