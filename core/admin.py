from django.contrib import admin
from .models import Product, Category,Order,Banner
from django.contrib.admin import ModelAdmin

# Inline form for adding products inside the category page
class ProductInline(admin.TabularInline):
    model = Product
    extra = 1  # Number of empty forms to display when adding a product inside category
    fields = ['name', 'price', 'discount_price', 'product_available_count']
    autocomplete_fields = ['category']  # Auto-complete the category field

# ProductAdmin to customize list view behavior for products
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'discount_price', 'product_available_count', 'edit_discount_price')
    list_editable = ('price', 'discount_price', 'product_available_count')  # Allow direct edit of these fields in the list view
    search_fields = ('name__icontains', 'desc__icontains', 'category__category_name__icontains')
    list_filter = ('category','price')  # Allow filtering by category
    

    def edit_discount_price(self, obj):
        if obj.discount_price:
            return obj.discount_price
        return "No Discount"
    edit_discount_price.short_description = 'Discount Price'  # Customize the column name for better clarity

# CategoryAdmin to manage categories and products inline
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name',)  # Display category name
    search_fields = ('category_name',)  # Allow search by category name
    inlines = [ProductInline]  # Allow products to be managed directly within categories


class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'order_status', 'ordered_date')
    list_filter = ('order_status',)
    search_fields = ('order_id',)

    # Allow the admin to change the order status
    list_editable = ('order_status',)

admin.site.register(Order, OrderAdmin)


# Registering Product and Category models with their respective custom admin classes
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)


class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'image', 'created_at')
    search_fields = ('title', 'subtitle')

admin.site.register(Banner, BannerAdmin) 