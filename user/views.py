from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from user.forms import CustomRegistrationForm  

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
            return redirect('user-login')
        else:
            messages.error(request, 'Registration failed. Please check the errors below.')
        return render(request, self.template_name, {'form': form})
