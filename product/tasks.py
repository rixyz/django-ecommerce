from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from Ecommerce.enums import TransactionStatus
from product.models import Order, PaymentHistory

@shared_task(name="process_unpaid_orders")
def process_unpaid_orders():
    """
    Task to mark unpaid orders older than a week as deleted
    """

    duration = timezone.now() - timedelta(hours=12)

    updated_count = Order.objects.filter(
        id__in=PaymentHistory.objects.filter(
            created_at__lt=duration,
            order__is_deleted=False
        ).exclude(
            transaction_status=TransactionStatus.COMPLETE
        ).values_list("order", flat=True)
    ).update(is_deleted=True)
    
    return f"Updated {updated_count} orders"

# @shared_task(name="process_deleted_orders")
# def process_deleted_orders(days):
#     """
#     Task to permanently delete orders that are marked as is_deleted 
#     and are older than a month
#     `process_deleted_orders.apply_async(args=[30], countdown=60)`
#     """
#     time_diff = timezone.now() - timedelta(days=days)
    
#     old_deleted_orders = Order.objects.filter(
#         is_deleted=True,
#         created_at__lt=time_diff
#     )
    
#     deletion_count = old_deleted_orders.count()
    
#     old_deleted_orders.delete()
    
#     return f"Deleted {deletion_count} orders"
    