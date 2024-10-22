from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.contrib.auth.models import User
from product.models import Product, ProductImage, Cart, Favorite, Category
from django.utils.html import format_html, format_html_join

class ProductChangeList(ChangeList):
    def __init__(self, request, model, list_display, list_display_links, list_filter, date_hierarchy,
                 search_fields, list_select_related, list_per_page, list_max_show_all, list_editable,
                 model_admin, sortable_by, search_help_text):
        super().__init__(request, model, list_display, list_display_links, list_filter, date_hierarchy,
                        search_fields, list_select_related, list_per_page, list_max_show_all,
                        list_editable, model_admin, sortable_by, search_help_text)
        self.selected_category = request.GET.get('category', None)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'quantity', 'images', 'action')
    search_fields = ('title', 'description')
    actions = None

    def action(self, request):
        return format_html(
            '<button class="delete-btn" data-product-id="{}">Delete</button>',
            request.id
        )

    def images(self, request):
        images = ProductImage.objects.filter(product=request)
        return format_html_join(
            ' ',
            '<a href="javascript:void(0)" onclick="showImage(\'/media/{}\')"><img src="/media/{}" width="50" height="50" style="cursor: pointer"/></a>',
            ((image.image, image.image) for image in images)
        )
    images.short_description = 'Images'
    images.allow_tags = True

    def get_changelist(self, request):
        return ProductChangeList

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        category_id = request.GET.get('category', None)
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        categories = Category.objects.all()
        extra_context['categories'] = categories
        extra_context['selected_category'] = request.GET.get('category', None)
        return super().changelist_view(request, extra_context)

    class Media:
        css = {
            'all': ('admin/css/product_tabs.css',)
        }

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'product_count')
    search_fields = ('title',)

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Number of Products'

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductImage)
admin.site.register(Cart)
admin.site.register(Favorite)