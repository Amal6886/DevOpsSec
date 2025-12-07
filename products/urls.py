from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('supplement/<int:pk>/', views.supplement_detail, name='supplement_detail'),
    path('protein-bar/<int:pk>/', views.protein_bar_detail, name='protein_bar_detail'),

    path('admin/', views.admin_product_list, name='admin_product_list'),
    path('admin/supplement/create/', views.create_supplement, name='create_supplement'),
    path('admin/supplement/<int:pk>/update/', views.update_supplement, name='update_supplement'),
    path('admin/supplement/<int:pk>/delete/', views.delete_supplement, name='delete_supplement'),
    path('admin/protein-bar/create/', views.create_protein_bar, name='create_protein_bar'),
    path('admin/protein-bar/<int:pk>/update/', views.update_protein_bar, name='update_protein_bar'),
    path('admin/protein-bar/<int:pk>/delete/', views.delete_protein_bar, name='delete_protein_bar'),
]
