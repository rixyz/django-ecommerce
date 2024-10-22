from django.contrib import admin
from django.urls import include, path

from product.views import ProductView, ProductCreateView, ProductDetailView, CartView, FavoriteView

urlpatterns = [
    path('', ProductView.as_view(), name='home'),
    path('add', ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:pk>/delete/', ProductView.as_view(), name='product-delete'),
    path('cart/', CartView.as_view(), name='cart'),
    path('favorite/', FavoriteView.as_view(), name='favorite'),
]