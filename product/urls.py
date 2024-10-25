from django.contrib import admin
from django.urls import include, path

from product.views import ProductView, ProductCreateView, ProductDetailView, CategoryView, CartView, FavoriteView, CheckoutView, PurchaseView

app_name = "product"
urlpatterns = [
    path('', ProductView.as_view(), name='product-home'),
    path('add', ProductCreateView.as_view(), name='create'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('product/<int:pk>/delete/', ProductView.as_view(), name='product-delete'),
    path('category/<int:pk>', CategoryView.as_view(), name='category'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:pk>/', CartView.as_view(), name='cart-add'),
    path('cart/remove/<int:pk>/', CartView.as_view(), name='cart-remove'),
    path('favorite/', FavoriteView.as_view(), name='cart'),
    path('favorite/add/<int:pk>/', FavoriteView.as_view(), name='favorites-add'),
    path('favorite/remove/<int:pk>/', FavoriteView.as_view(), name='favorites-remove'),
    path('checkout', CheckoutView.as_view(), name='checkout'),
    path('purchase', PurchaseView.as_view(), name='purchase'),
]