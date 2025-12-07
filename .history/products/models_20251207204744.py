"""
Product models for the Diet Planner application.

Defines base product model and specific product types (Supplements, Protein Bars).
"""
from django.db import models
from django.urls import reverse


class BaseProduct(models.Model):
    """
    Abstract base model for all products in the system.

    Provides common fields and methods for product management including
    stock tracking and low stock detection.
    """
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    threshold = models.IntegerField(default=10)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def is_low_stock(self):
        """
        Check if product stock is below or equal to threshold.

        Returns:
            bool: True if stock is low, False otherwise
        """
        return self.stock_quantity <= self.threshold

    def get_absolute_url(self):
        """
        Get the absolute URL for this product.

        Returns:
            str: URL path to product detail page
        """
        return reverse('products:product_detail', kwargs={'pk': self.pk})


class Supplement(BaseProduct):
    """
    Model representing a dietary supplement product.

    Inherits from BaseProduct and adds supplement-specific fields.
    """
    brand = models.CharField(max_length=100, blank=True)
    serving_size = models.CharField(max_length=50, blank=True)
    category = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Supplement'
        verbose_name_plural = 'Supplements'


class ProteinBar(BaseProduct):
    """
    Model representing a protein bar product.

    Inherits from BaseProduct and adds protein bar-specific fields.
    """
    flavor = models.CharField(max_length=100, blank=True)
    protein_content = models.CharField(max_length=50, blank=True)
    calories = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Protein Bar'
        verbose_name_plural = 'Protein Bars'
