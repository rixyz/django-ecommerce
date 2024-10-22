from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
import json

from product.forms import ProductForm
from product.models import Product, Category, ProductImage, Cart, Favorite

class ProductView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        categories = Category.objects.all()
        product_with_images = []
        for product in products:
            first_image = ProductImage.objects.filter(product=product).first() 
            product_with_images.append({
                'product': product,
                'first_image': first_image
            })
        return render(request, 'product/index.html', {'products': product_with_images, 'categories': categories})
    
    def delete(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        product = get_object_or_404(Product, id=product_id)
        if request.user == product.seller or request.user.is_staff:
            product.delete()
            return JsonResponse({'status': 'success', 'message': 'Product deleted successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized to delete this product'}, status=403)

class ProductCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all() 
        form = ProductForm()
        return render(request, 'product/product_form.html' , {'categories': categories, 'form': form})
        
    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        images = request.FILES.getlist('images')

        if form.is_valid():
            product = Product(
                title=form.cleaned_data['title'],
                description=form.cleaned_data['description'],
                quantity=form.cleaned_data['quantity'],
                category=form.cleaned_data['category'],
                price=form.cleaned_data['price'],
                seller=request.user  
            )
            product.save() 

            for image in images:
                ProductImage.objects.create(product=product, image=image)

            return redirect(reverse_lazy('home'))  
        
        categories = Category.objects.all()
        messages.error("AN ERROR OCCURED")
        return render(request, 'product/product_form.html', {'categories': categories, 'form': form})

class ProductDetailView(View):
    def get(self, request, *args, **kwargs):
        product_id = self.kwargs.get("pk")
        product = get_object_or_404(Product, id=product_id)
        images = ProductImage.objects.filter(product=product)

        return render(request, 'product/product_detail.html', {
            'product': product,
            'images': images
        })

class CartView(View, LoginRequiredMixin):
    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return JsonResponse({'status': 'success', 'cart': []})

        cart_data = []
        for cart_item in cart_items:
            product = cart_item.product
            cart_data.append({
                'id': product.id,
                'title': product.title,
                'price': product.price,
                'quantity': cart_item.quantity,
            })

        return JsonResponse({
            'status': 'success',
            'cart': cart_data,
        })

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        product_id = data.get('product_id')
        action = data.get('action')
        quantity = data.get('quantity')

        if not product_id or action not in ['add', 'remove']:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request parameters'
            }, status=400)

        product = get_object_or_404(Product, id=product_id)
        if action == 'add':
            if product.in_cart_of(request.user):
                return JsonResponse({
                'status': 'failed',
                'message': "Already in cart",
                'in_cart': True
            })
            product.add_to_cart(request.user, quantity)
            message = 'Product added to cart successfully'
            in_cart = True

        elif action == 'remove':
            if product.remove_from_cart(request.user):
                message = 'Product removed from cart successfully'
                in_cart = False
            else:
                message = 'Product was not in the cart'
                in_cart = False

        return JsonResponse({
            'status': 'success',
            'message': message,
            'in_cart': in_cart
        })

class FavoriteView(View, LoginRequiredMixin):
    def get(self, request):
        fav_items = Favorite.objects.filter(user=request.user)
        if not fav_items:
            return JsonResponse({'status': 'success', 'fav': []})

        fav_data = []
        for fav_item in fav_items:
            for product in fav_item.product.all(): 
                fav_data.append({
                    'id': product.id,
                    'title': product.title,
                    'price': product.price,
                })

        return JsonResponse({
            'status': 'success',
            'fav': fav_data,
        })

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        product_id = data.get('product_id')
        action = data.get('action')

        if not product_id or action not in ['add', 'remove']:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid request parameters'
            }, status=400)

        product = get_object_or_404(Product, id=product_id)

        if action == 'add':
            product.add_to_favorites(request.user)
            message = 'Product added to favorites successfully'
            is_in_favorites = True

        elif action == 'remove':
            product.remove_from_favorites(request.user)
            message = 'Product removed from favorites successfully'
            is_in_favorites = False

        return JsonResponse({
            'status': 'success',
            'message': message,
            'in_favorites': is_in_favorites
        })