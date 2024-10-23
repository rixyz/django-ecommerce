from django.urls import path
from django.contrib.auth.views import LogoutView
from user.views import Login, Register

urlpatterns = [
    path('register/', Register.as_view(), name='user-register'),
    path('login/', Login.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]