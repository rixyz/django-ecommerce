from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse,HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
import json

from product.models import Cart, Favorite
from user.forms import CustomRegistrationForm  
from user.models import Location

class Login(View):
    template_name = 'user/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return render(request, self.template_name)

class Register(View):
    template_name = 'user/register.html'

    def get(self, request, *args, **kwargs):
        form = CustomRegistrationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login with your credentials.')
            return redirect('user:login')
        else:
            messages.error(request, 'Registration failed. Please check the errors below.')
        return render(request, self.template_name, {'form': form})

class Profile(View):
    template_name = 'user/profile.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        carts = Cart.objects.filter(user=user)
        favorites = Favorite.objects.filter(user=user)

        return render(request, self.template_name, {'cart': carts, 'favorite': favorites})

class EditProfile(LoginRequiredMixin, View):
    template_name = 'user/edit.html'
    
    def get(self, request, *args, **kwargs):
        locations = Location.objects.all()
        context = {
            'locations': locations,
            'user': request.user
        }
        return render(request, self.template_name, context)
    
    def put(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            user = request.user
            
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.email = data.get('email', user.email)
            
            location_id = data.get('location')
            if location_id:
                try:
                    location = Location.objects.get(id=location_id)
                    user.address = location
                except Location.DoesNotExist:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid location selected'
                    }, status=400)
            
            user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated successfully'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid data format'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

class EditPassword(LoginRequiredMixin, View):
    template_name = 'user/edit.html'
    
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.POST
        
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not password or not confirm_password:
            messages.error(request,"Both password fields are required")
            return redirect('user:edit-password')
            
        if password != confirm_password:
            messages.error(request,"Passwords do not match")
            return redirect('user:edit-password')
        user.set_password(password)
        user.save()
        return redirect('user:edit-password')
