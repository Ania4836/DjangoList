from .views import product_list, product_detail
from django.urls import path

urlpatterns = [
    path('api/products/', product_list, name='product_list'),
    path('api/products/<int:product_id>/', product_detail, name='product_detail'),
]
