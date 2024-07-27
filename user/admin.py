from django.contrib import admin
from django.http import HttpResponse

from openpyxl import Workbook
from .models import *


admin.site.site_header = 'Asoka 后台管理'
admin.site.index_title = 'Asoka 后台管理'
admin.site_title = 'Asoka 后台管理'

# 导出Excel
class ExportExcelMixin(object):
    def export_as_excel(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='application/msexcel')
        response['Content-Disposition'] = f'attachment; filename={meta.object_name}.xlsx'
        wb = Workbook()
        ws = wb.active
        ws.append(field_names)
        for obj in queryset:
            for field in field_names:
                data = [f'{getattr(obj, field)}' for field in field_names]
            row = ws.append(data)

        wb.save(response)
        return response
    export_as_excel.short_description = '导出Excel'


class UserAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "name", 'gender', 'identity', 'is_active', 'phone',
                    'create_time',)
    exclude = ()
    readonly_fields = ('openid', "id", "name", 'gender', 'phone', 'birthdt', 'birthloc', 
                       'liveloc', 'job', 'belief', 'mbti', 'create_time',
                       'update_time')


    list_display_links = ['name']

    list_filter = ('gender', "identity", "is_active")
    search_fields = ("name", "phone")
    
    actions = ['export_as_excel', 'make_vip', 'cancel_vip']

    def make_vip(modeladmin, request, queryset):
        queryset.update(identity=1)
    make_vip.short_description = "批量设置 VIP"

    def cancel_vip(modeladmin, request, queryset):
        queryset.update(identity=1)
    cancel_vip.short_description = "批量取消 VIP"

    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_add_permission(self, request, obj=None):
        return False


class AddressAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "user", 'recipient', 'phone', 'detailed_address')
    exclude = ()
    # readonly_fields = ('openid', "id", "name", 'gender', 'phone', 'birthdt', 'birthloc', 
    #                    'liveloc', 'job', 'belief', 'mbti', 'create_time',
    #                    'update_time')


    list_display_links = ['recipient']

    search_fields = ('user', "recipient", "phone")
    
    actions = ['export_as_excel']

    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_add_permission(self, request, obj=None):
        return False


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Address, AddressAdmin)