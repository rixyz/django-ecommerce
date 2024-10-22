from django import forms
from product.models import Product
from product.models import Category 

class ProductForm(forms.Form):
    title = forms.CharField(max_length=255, required=True)  
    description = forms.CharField(widget=forms.Textarea, required=True)  
    quantity = forms.IntegerField(required=True)  
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)  
    price = forms.IntegerField(required=True)