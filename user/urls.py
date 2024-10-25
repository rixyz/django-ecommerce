from django.urls import path
from django.contrib.auth.views import LogoutView
from user.views import Login, Register, Profile, EditProfile, EditPassword

app_name = 'user'

urlpatterns = [
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', Profile.as_view(), name='profile'),
    path('profile/edit/', EditProfile.as_view(), name='edit-profile'),
    path('profile/password/edit/', EditPassword.as_view(), name='edit-password'),
]