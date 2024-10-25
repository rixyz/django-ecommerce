"""
URL configuration for Ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from product.views import ProductView
from user.views import Login, Register, Profile, EditProfile, EditPassword

urlpatterns = [
    path('', ProductView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('shop/', include('product.urls')),

    path('register/', Register.as_view(), name='user-register'),
    path('login/', Login.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', Profile.as_view(), name='profile'),
    path('profile/edit/', EditProfile.as_view(), name='edit-profile'),
    path('profile/password/edit/', EditPassword.as_view(), name='edit-password'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
