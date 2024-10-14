from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import *
from user.admin import ExportExcelMixin


# ----------------------------------------------------------------
class GemstonePicInline(admin.TabularInline):
    fields = ('pic','thumbnail',)
    model = GemstonePic
    extra = 0  # 默认显示 0 个 
    
    readonly_fields = ('thumbnail',)
    @admin.display(description="缩略图")
    def thumbnail(self, obj):
        if obj.pic:
            return mark_safe(f'<img src="{obj.pic.url}" height="80" />')
        else:
            return '-'

    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


class GemAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "name", "thumbnailpic", 'position', 'size', 'inventory',
                    'price', 'sales')
    exclude = ()
    readonly_fields = ("id", 'create_time', 'update_time')


    list_display_links = ['name']

    list_filter = ('typ',)
    search_fields = ("name",)
    
    actions = ['export_as_excel']
    
    inlines = [GemstonePicInline]

    @admin.display(description="封面")
    def coverpic(self, obj):
        if obj.cover:
            return mark_safe(f'<img src="{obj.cover.url}" width="40%" height="auto" />')
        else:
            return '-'
    
    @admin.display(description="缩略图")
    def thumbnailpic(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" width="40%" height="auto" />')
        else:
            return '-'


    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


# ----------------------------------------------------------------
class BraceletPicInline(admin.TabularInline):
    fields = ('pic','thumbnail',)
    model = BraceletPic
    extra = 0  # 默认显示 0 个 
    
    readonly_fields = ('thumbnail',)
    @admin.display(description="缩略图")
    def thumbnail(self, obj):
        if obj.pic:
            return mark_safe(f'<img src="{obj.pic.url}" height="80" />')
        else:
            return '-'

    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True

class BraceAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "name", "thumbnailpic", 'coverpic', 'typ', 'inventory',
                    'price', 'sales')
    exclude = ()
    readonly_fields = ("id", 'create_time', 'update_time')


    list_display_links = ['name']

    list_filter = ('typ',)
    search_fields = ("name",)
    
    actions = ['export_as_excel']
    
    inlines = [BraceletPicInline]
    
    @admin.display(description="封面")
    def coverpic(self, obj):
        if obj.cover:
            return mark_safe(f'<img src="{obj.cover.url}" width="40%" height="auto" />')
        else:
            return '-'
    
    @admin.display(description="缩略图")
    def thumbnailpic(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" width="40%" height="auto" />')
        else:
            return '-'


    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


# ----------------------------------------------------------------
class StampPicInline(admin.TabularInline):
    fields = ('pic','thumbnail',)
    model = StampPic
    extra = 0  # 默认显示 0 个 
    
    readonly_fields = ('thumbnail',)
    @admin.display(description="缩略图")
    def thumbnail(self, obj):
        if obj.pic:
            return mark_safe(f'<img src="{obj.pic.url}" height="80" />')
        else:
            return '-'

    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


class StampAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "name", "thumbnailpic", 'coverpic', 'typ', 'material', 'inventory',
                    'price', 'sales')
    exclude = ()
    readonly_fields = ("id", 'create_time', 'update_time')


    list_display_links = ['name']

    list_filter = ('typ',)
    search_fields = ("name",)
    
    actions = ['export_as_excel']
    
    inlines = [StampPicInline]

    @admin.display(description="封面")
    def coverpic(self, obj):
        if obj.cover:
            return mark_safe(f'<img src="{obj.cover.url}" width="40%" height="auto" />')
        else:
            return '-'
    
    @admin.display(description="缩略图")
    def thumbnailpic(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" width="40%" height="auto" />')
        else:
            return '-'


    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


# ----------------------------------------------------------------
class GiftPicInline(admin.TabularInline):
    fields = ('pic','thumbnail',)
    model = GiftPic
    extra = 0  # 默认显示 0 个 
    
    readonly_fields = ('thumbnail',)
    @admin.display(description="缩略图")
    def thumbnail(self, obj):
        if obj.pic:
            return mark_safe(f'<img src="{obj.pic.url}" height="80" />')
        else:
            return '-'

    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True

class GiftAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "name", 'coverpic', 'component', 'price',
                    'sales',)
    exclude = ()
    readonly_fields = ("id", 'create_time', 'update_time')


    list_display_links = ['name']

    list_filter = ()
    search_fields = ("name",)
    
    actions = ['export_as_excel']
    
    inlines = [GiftPicInline]

    @admin.display(description="封面")
    def coverpic(self, obj):
        if obj.cover:
            return mark_safe(f'<img src="{obj.cover.url}" width="100" height="auto" />')
        else:
            return '-'


    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True



# ---------------------------------------------------------------------
class SchemeAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "name", 'thumbnailpic', 'structure', 'is_user_defined', 'user')
    exclude = ()
    readonly_fields = ("id", 'create_time', 'update_time', 'user', 'is_user_defined')


    list_display_links = ['name']

    list_filter = ()
    search_fields = ("name",)
    
    actions = ['export_as_excel']
    

    @admin.display(description="示意图")
    def thumbnailpic(self, obj):
        if obj.thumbnail:
            return mark_safe(f'<img src="{obj.thumbnail.url}" width="100" height="auto" />')
        else:
            return '-'


    def has_add_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True


admin.site.register(Gemstone, GemAdmin)

admin.site.register(Bracelet, BraceAdmin)

admin.site.register(Gift, GiftAdmin)

admin.site.register(Stamp, StampAdmin)

admin.site.register(Scheme_Template, SchemeAdmin)
