from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
import json

from product.forms import ProductForm
from product.models import Product, Category, ProductImage, Cart, Favorite, Order

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
        product_id = kwargs.get("pk")
        product = get_object_or_404(Product, id=product_id)
        images = ProductImage.objects.filter(product=product)

        return render(request, 'product/product_detail.html', {
            'product': product,
            'images': images
        })

class CategoryView(View):
    def get(self, request, *args, **kwargs):
        category_id = kwargs.get("pk")
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
        categories_product = []
        for product in products:
            product_image = ProductImage.objects.filter(product=product).first() 
            categories_product.append({
                'id': product.id,
                'title': product.title,
                'description': product.description,
                'price': product.price,
                'image': product_image.image,
            })
        return render(request, 'product/categories.html', {'products': categories_product, 'category': category})

class CartView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return JsonResponse({'status': 'success', 'cart': []})
        
        cart_data = [{
            'id': item.product.id,
            'title': item.product.title,
            'price': item.product.price,
            'quantity': item.quantity,
        } for item in cart_items]
        
        return JsonResponse({
            'status': 'success',
            'cart': cart_data,
        })

    def post(self, request, *args, **kwargs):
        product_id = kwargs.get("pk") 
        data = json.loads(request.body)
        quantity = data.get('quantity')

        if not product_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Product ID is required'
            }, status=400)

        product = get_object_or_404(Product, id=product_id)
        
        if product.in_cart_of(request.user):
            return JsonResponse({
                'status': 'error',
                'message': "Already in cart",
                'in_cart': True
            }, status=400)

        product.add_to_cart(request.user, quantity)
        return JsonResponse({
            'status': 'success',
            'message': 'Product added to cart successfully',
            'in_cart': True
        })

    def delete(self, request, *args, **kwargs):
        product_id = kwargs.get("pk") 

        if not product_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Product ID is required'
            }, status=400)

        product = get_object_or_404(Product, id=product_id)
        
        if product.remove_from_cart(request.user):
            return JsonResponse({
                'status': 'success',
                'message': 'Product removed from cart successfully',
                'in_cart': False
            })
        
        return JsonResponse({
            'status': 'error',
            'message': 'Product was not in the cart',
            'in_cart': False
        }, status=404)

class FavoriteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        favorites = Favorite.objects.filter(user=request.user)
        if not favorites:
            return JsonResponse({'status': 'success', 'fav': []})
        
        fav_data = []
        for fav_item in favorites:
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
        product_id = kwargs.get("pk") 

        if not product_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Product ID is required'
            }, status=400)

        product = get_object_or_404(Product, id=product_id)
        
        if product.in_favorites_of(request.user):
            return JsonResponse({
                'status': 'error',
                'message': "Already in favorites",
                'in_favorites': True
            }, status=400)

        product.add_to_favorites(request.user)
        return JsonResponse({
            'status': 'success',
            'message': 'Product added to favorites successfully',
            'in_favorites': True
        })

    def delete(self, request, *args, **kwargs):
        product_id = kwargs.get("pk") 

        if not product_id:
            return JsonResponse({
                'status': 'error',
                'message': 'Product ID is required'
            }, status=400)

        product = get_object_or_404(Product, id=product_id)
        
        if product.remove_from_favorites(request.user):
            return JsonResponse({
                'status': 'success',
                'message': 'Product removed from favorites successfully',
                'in_favorites': False
            })
        
        return JsonResponse({
            'status': 'error',
            'message': 'Product was not in favorites',
            'in_favorites': False
        }, status=404)

class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart_items = Cart.objects.filter(user=request.user)
        
        cart_data = [{
            'product': item.product,
            'id': item.product.id,
            'title': item.product.title,
            'price': item.product.price,
            'quantity': min(item.quantity, item.product.quantity),
        } for item in cart_items]

        return render(request, 'product/checkout.html', {'cart_data': cart_data})

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        address = data.get('address')
        items = data.get('items')

        user = request.user

        for item in items:
            product = Product.objects.get(id=item['id'])
            Order.create(product, user, address, item['quantity'])
        return redirect(reverse_lazy('checkout'))  
        # return JsonResponse({"status": "success", "message": "Checkout processed successfully"})

class PurchaseView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        orders = Order.objects.filter(user=user)
        for order in orders:
            order.complete(request.POST.get('address'))
            cart = Cart.objects.get(user=user, product=order.product)
            cart.complete(order.quantity)
        return redirect(reverse_lazy('checkout'))  
        # return JsonResponse({"status": "success", "message": "Purchased successfully"})
