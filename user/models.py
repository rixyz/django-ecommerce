from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models

class CustomUserModel(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        user = self.model(
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save()
        print("Created User")
        return user

    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True ")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self.create_user(email,password, 
            first_name= "ADMIN",
            last_name = email, 
            **extra_fields
        )

class Location(models.Model):
    title = models.TextField()

    def __str__(self):
        return self.title

class User(AbstractUser):
    email = models.EmailField(unique=True)
    address = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    username = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserModel()
    
    def __str__(self):
        return f"({self.id}) {self.email}"

