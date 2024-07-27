from django.contrib import admin
from django.http import HttpResponse
from django.utils.safestring import mark_safe

from .models import *
from user.admin import ExportExcelMixin


class EvalcontentAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", 'name', "user", 'forself', 'create_time')
    exclude = ()
    readonly_fields = ("id", "user", 'name', 'gender', 'birthdt', 'birthloc',
                    'liveloc', 'job', 'belief', 'mood', 'question1', 'question2',
                    'question3', 'question4', 'wish', 'create_time', 'update_time')


    list_display_links = ['name',]

    list_filter = ('forself', )
    search_fields = ("user", 'name')
    
    actions = ['export_as_excel']

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False


class EvalcontentInline(admin.TabularInline):
    exclude = ['user', ]
    model = Evalcontent
    extra = 0  # 默认显示 0 个 

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

class EvalreportAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", 'name', "user", 'title', 'create_time')
    exclude = ()
    readonly_fields = ("id", "user", 'evalcontent', 'title', 'overall', 'wish',
                    'advice', 'create_time', 'update_time')

    list_display_links = ['name',]

    search_fields = ("user", 'name')
    
    actions = ['export_as_excel']

    
    def name(self, obj):
        if obj.evalcontent:
            return obj.evalcontent.name
        else:
            return '-'
    name.short_description = '被测人姓名'

    
    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False


class ChathistoryAdmin(admin.ModelAdmin, ExportExcelMixin):
    list_display = ("id", "user", 'talker', 'msg', 'create_time')
    exclude = ()

    list_display_links = ['id',]

    list_filter = ('talker', )
    search_fields = ("user", )
    
    actions = ['export_as_excel']

    def has_add_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(Evalcontent, EvalcontentAdmin)

admin.site.register(Chathistory, ChathistoryAdmin)

admin.site.register(Evalreport, EvalreportAdmin)
