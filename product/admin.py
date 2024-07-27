from django.contrib import admin
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from openpyxl import Workbook
from .models import *
from user.admin import ExportExcelMixin

class GemAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "name", 'typ', 'thumbnail', 'loc',
                    'price',)
    exclude = ()
    readonly_fields = ()


    list_display_links = ['name']

    list_filter = ('typ',)
    search_fields = ("name",)
    
    actions = ['export_as_excel']
    
    def thumbnail(self, obj):
        if obj.pic:
            return mark_safe(f'<img src="{obj.pic.url}" height="80" />')
        else:
            return '-'
    thumbnail.short_description = '缩略图'
    
    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


class BraceAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "name", 'typ', 'thumbnail', 'loc',
                    'price',)
    exclude = ()
    readonly_fields = ()


    list_display_links = ['name']

    list_filter = ('typ',)
    search_fields = ("name",)
    
    actions = ['export_as_excel']
    
    def thumbnail(self, obj):
        if obj.pic:
            return mark_safe(f'<img src="{obj.pic.url}" height="80" />')
        else:
            return '-'
    thumbnail.short_description = '缩略图'
    
    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


class GiftAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "name", 'typ', 'thumbnail', 'component', 'price',
                    'sales',)
    exclude = ()
    readonly_fields = ()


    list_display_links = ['name']

    list_filter = ('typ',)
    search_fields = ("name",)
    
    actions = ['export_as_excel']
    
    def thumbnail(self, obj):
        if obj.pic:
            return mark_safe(f'<img src="{obj.pic.url}" height="80" />')
        else:
            return '-'
    thumbnail.short_description = '缩略图'


    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


admin.site.register(Gemstone, GemAdmin)

admin.site.register(Bracelet, BraceAdmin)

admin.site.register(Gift, GiftAdmin)