from django.contrib import admin
from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    """
    تنظیمات ادمین برای مشاهده لاگ‌های درخواست
    """
    list_display = ('method', 'path', 'status_code', 'ip_address', 'user', 'response_time', 'timestamp')
    list_filter = ('method', 'status_code', 'timestamp', 'user')
    search_fields = ('path', 'ip_address', 'user__username', 'query_string')
    readonly_fields = ('method', 'path', 'query_string', 'ip_address', 'user_agent', 
                      'referer', 'status_code', 'response_time', 'timestamp', 'user')
    date_hierarchy = 'timestamp'
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('اطلاعات درخواست', {
            'fields': ('method', 'path', 'query_string', 'timestamp')
        }),
        ('اطلاعات کلاینت', {
            'fields': ('ip_address', 'user_agent', 'referer', 'user')
        }),
        ('اطلاعات پاسخ', {
            'fields': ('status_code', 'response_time')
        }),
    )

    def has_add_permission(self, request):
        """غیرفعال کردن امکان افزودن دستی لاگ"""
        return False

    def has_change_permission(self, request, obj=None):
        """غیرفعال کردن امکان ویرایش لاگ‌ها"""
        return False

    def has_delete_permission(self, request, obj=None):
        """فعال کردن امکان حذف لاگ‌ها"""
        return True
