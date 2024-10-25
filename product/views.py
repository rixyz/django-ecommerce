from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.http import JsonResponse
import requests
import json
from django.conf import settings

from product.forms import ProductForm
from product.models import Product, Category, ProductImage, Cart, Favorite, Order, ProductOrder, PaymentHistory
from user.models import Location

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

            return redirect('product:product-home')  
        
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
        user = request.user
        checkout_type = request.GET.get('checkout_type', 'cart') 
        product_id = request.GET.get('product_id')
        quantity = int(request.GET.get('quantity', 1))
              
        if checkout_type == 'direct' and product_id:
            product = get_object_or_404(Product, id=product_id)
            
            if quantity <= 0 or quantity > product.quantity:
                return JsonResponse({
                    "status": "error",
                    "message": "Invalid quantity"
                }, status=400)
            
            cart_data = [{
                'id': product.id,
                'title': product.title,
                'price': product.price,
                'quantity': min(quantity, product.quantity),
                'item_total': product.price * quantity
            }]
            
        else:
            cart_items = Cart.objects.filter(user=user)
            if not cart_items.exists():
                return JsonResponse({
                    "status": "error",
                    "message": "Cart is empty"
                }, status=400)
            
            cart_data = [{
                'id': item.product.id,
                'title': item.product.title,
                'price': item.product.price,
                'quantity': min(item.quantity, item.product.quantity),
                'item_total': item.product.price * min(item.quantity, item.product.quantity)
            } for item in cart_items]

        total_price = sum(item['item_total'] for item in cart_data)
            
        order = Order.objects.create(
            user=user,
            is_paid=False,
            address=user.address,
        )
        
        for item in cart_data:  
            product = Product.objects.get(id=item['id'])                
            product_order = ProductOrder.objects.create(
                product=product,
                quantity=item['quantity'],
                order=order
            )

        locations = Location.objects.all()
        
        context = {
            'cart_data': cart_data,
            'total_price': total_price,
            'locations': locations,
            'order_id': order.id,
            'checkout_type': checkout_type
        }
            
        return render(request, 'product/checkout.html', context)

    def post(self, request, *args, **kwargs):
        user = request.user
        address_id = request.POST.get('address')
        payment = request.POST.get('payment')
        order_id = request.POST.get('order_id')
        payment = "Khalti"
        
        try:
            location = Location.objects.get(id=address_id)
        except Location.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Invalid location selected"
            }, status=400)

        order = Order.objects.get(id=order_id)
        
        total_amount = 0
        product_details = []
        product_order = ProductOrder.objects.filter(order=order)
        
        for product_order in product_order.all():
            product = product_order.product
            quantity = product_order.quantity
            
            if quantity > product.quantity:
                return JsonResponse({
                    "status": "error",
                    "message": f"Insufficient stock for {product.title}"
                }, status=400)
            
            item_total = product.price * 100 * quantity
            total_amount += item_total
            purchase_history = PaymentHistory.objects.create(
                seller=product_order.product.seller,
                buyer=user,
                amount=product_order.quantity * product_order.product.price,
                order=order,
                transaction_status="INITIATE",
                transaction_type=payment.upper()
            )
            
            product_details.append({
                "identity": str(product.id),
                "name": product.title,
                "total_price": item_total,
                "quantity": quantity,
                "unit_price": product.price * 100
            })

        order.address = location
        order.save()

        payment_data = {
            "return_url": settings.TRANSACTION_REDIRECT_URL,
            "website_url": "https://example.com/",
            "amount": total_amount,
            "purchase_order_id": order.id,
            "purchase_order_name": f"Order #{order.id}",
            "customer_info": {
                "name": "Khalti Bahadur",
                "email": "example@gmail.com",
                "phone": "9800000123"
            },
            "amount_breakdown": [
                {
                    "label": "Mark Price",
                    "amount": total_amount
                },
                {
                    "label": "VAT",
                    "amount": 0
                }
            ],
            "product_details": product_details,
            "merchant_username": "merchant_name",
            "merchant_extra": "merchant_extra"
        }

        url = settings.KHALTI_URL
        headers = {
            'Authorization': settings.KHALTI_AUTH,
            'Content-Type': 'application/json'
        }
        
        response = requests.request(
            "POST",
            url,
            headers=headers,
            data=json.dumps(payment_data)
        )
        
        data = response.json()
        transaction_id = data['pidx']

        PaymentHistory.objects.filter(order=order).update(transaction_response=data)
        PaymentHistory.objects.filter(order=order).update(transaction_id=transaction_id)
        
        return redirect(data['payment_url'])

class PurchaseView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pidx = request.GET.get('pidx', '')
        url = settings.KHALTI_LOOKUP_URL
        payload = json.dumps({
            "pidx": pidx
        })
        print(settings.KHALTI_AUTH)
        headers = {
            'Authorization': f'key {settings.KHALTI_AUTH}',
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if not response.status_code == 200:
            print(response)
            messages.info(request, "ERROR")
            return render(request, 'product/payment.html')
        data = response.json()

        if not data['status'] == "Completed":
            print(data)
            messages.info(request, "ERROR")
            return render(request, 'product/payment.html')
        
        payment = PaymentHistory.objects.filter(transaction_id=data['pidx']).first()
        order = payment.order
        if order.is_paid:
            messages.info(request, "Already Paid")
            return render(request, 'product/payment.html')
        
        product_order = ProductOrder.objects.filter(order=order)
        for product_order in product_order.all():
            product = product_order.product
            quantity = product_order.quantity

            if product.quantity < quantity:
                raise ValueError(f"Insufficient inventory for {product.title}")
            product.quantity -= quantity
            product.save()

            cart = Cart.objects.filter(
                user=request.user, 
                product=product
            ).first()
            
            if cart:
                cart.complete(quantity)

            order.is_paid = True
            order.save()

        payments = PaymentHistory.objects.filter(transaction_id=data['pidx'])
        for payment in payments:
            payment.transaction_status = "COMPLETE"
            
        messages.success(request, f"Payment {data["status"]}")
        return render(request, 'product/payment.html')
        