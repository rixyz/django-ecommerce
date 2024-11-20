from django.db import models
from django.core.exceptions import ValidationError
from Ecommerce.enums import TransactionStatus, TransactionType
from user.models import User, Location

def file_size(value):
    limit = 10 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 10 MB.')

class DateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

class Category(models.Model):
    title = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    title = models.TextField()
    description = models.TextField()
    quantity = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField()
    seller = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    def in_cart_of(self, user):
        return Cart.objects.filter(user=user, product=self).exists()

    def add_to_cart(self, user, quantity):
        cart, created = Cart.objects.get_or_create(user=user, product=self, quantity=quantity)
        if created:
            return True
        return False

    def remove_from_cart(self, user):
        cart = Cart.objects.filter(user=user, product=self).first()
        if cart:
            cart.delete()
            return True
        return False

    def in_favorites_of(self, user):
        return Favorite.objects.filter(user=user, product=self).exists()

    def add_to_favorites(self, user):
        favorite, created = Favorite.objects.get_or_create(user=user)
        favorite.product.add(self)
        return True

    def remove_from_favorites(self, user):
        favorite = Favorite.objects.filter(user=user).first()
        if favorite:
            favorite.product.remove(self)
            return True
        return False

    def __str__(self):
        return f"{self.title}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_image", validators=[file_size])

    def __str__(self):
        return f"{self.product.id} - {self.id}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='carts')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'product',)

    def complete(self, amount):
        self.quantity -= amount

        if self.quantity < 0:
            return False
        elif self.quantity == 0:
            self.delete()
        else:
            self.save()
        return True

    def __str__(self):
        return f"{self.quantity} {self.product.title} ({self.product.id}) - {self.user.first_name}"

class Order(DateModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Location, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    @classmethod
    def create(cls,product, user, address, quantity):
        order, created = Order.objects.get_or_create(product=product, user=user, address=address, quantity=quantity)
        if created:
            return True
        return False
        
    def __str__(self):
        return f"{self.user.email} {self.is_paid} {self.is_deleted}"

class ProductOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField() 

    def __str__(self):
        return f"#{self.order.id} {self.product.title} - {self.quantity}"

class PaymentHistory(DateModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payment')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buyer_payment_histories')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_payment_histories')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    transaction_id = models.TextField()
    transaction_response = models.JSONField(null=True)
    transaction_status = models.CharField(choices=TransactionStatus.choices)
    transaction_type = models.CharField(choices=TransactionType.choices)

    def __str__(self):
        return f'#{self.order.id} {self.transaction_type} ({self.transaction_status}) {self.buyer.id} {self.seller.id}'
    
    
class Favorite(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='favorite')
    product = models.ManyToManyField(Product, related_name='favorites')
    
    def __str__(self):
        return f"Favorites for {self.user.first_name}"