from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *
from user.admin import ExportExcelMixin


class GroupInline(admin.TabularInline):
    exclude = ['user', 'typ', 'scheme', 'gem_location']
    model = CartGroupScheme
    extra = 0  # 默认显示 0 个 

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False


class CartAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "user", 'product_type', 'group_type', 'quantity',
                    'is_ordered', 'order', 'create_time')
    exclude = ()
    # readonly_fields = ("id", "user", 'typ', 'component', 'quantity', 'cost',
    #                 'is_ordered', 'order', 'create_time', 'gemstone', 'bracelet', 'gift')


    list_display_links = ['id',]

    list_filter = ('product_type', 'group_type', 'is_ordered')
    search_fields = ("user__name", "order__order_number")
    
    actions = ['export_as_excel']

    # inlines = [GroupGiftInline, GroupInline]


    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False


class CartInline1(admin.TabularInline):
    exclude = ['user', 'is_ordered']
    model = Cart
    extra = 0  # 默认显示 0 个 

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

class OrderAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "user", 'order_number', 'status',
                    'recipient', 'tracking_number', 'total_cost')
    exclude = ()
    readonly_fields = ("id", "user", 'order_number',
                    'recipient', 'detailed_address', 'total_cost',
                    'ordered_dt', 'paid_dt', 'phone')


    list_display_links = ['order_number',]

    list_filter = ('status',)
    search_fields = ("user__name", 'order_number',)
    
    actions = ['export_as_excel']

    inlines = [CartInline1]

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return True


class CartInline2(admin.TabularInline):
    fields = ('id', 'product_type', 'gemstone', 'bracelet', 'stamp', 'quantity')
    # exclude = ['user', 'is_ordered', 'group_type']
    model = Cart
    extra = 0  # 默认显示 0 个 

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

class CartGroupGiftAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", 'user', 'gift')
    exclude = ()

    list_filter = ()
    search_fields = ("user__name", 'gift__name')
    
    actions = ['export_as_excel']

    inlines = [CartInline2]

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    

class CartGroupSchemeAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", 'user', 'scheme', 'gem_location')
    exclude = ()

    list_filter = ()
    search_fields = ("user__name", 'scheme__name')
    
    actions = ['export_as_excel']

    inlines = [CartInline2]

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Order, OrderAdmin)

admin.site.register(Cart, CartAdmin)

admin.site.register(CartGroupGift, CartGroupGiftAdmin)

admin.site.register(CartGroupScheme, CartGroupSchemeAdmin)