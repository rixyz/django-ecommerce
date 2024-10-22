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
            '''<a href="/admin/product/product/{}/delete/" class="delete-btn">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="white" viewBox="0 0 16 16">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/>
                    <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/>
                </svg>
            </a>''',
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