import time
from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware برای لاگ کردن درخواست‌های HTTP
    """
    
    def process_request(self, request):
        """
        ذخیره زمان شروع درخواست برای محاسبه زمان پاسخ
        """
        request._start_time = time.time()
        return None

    def process_response(self, request, response):
        """
        ثبت اطلاعات درخواست در دیتابیس
        """
        # محاسبه زمان پاسخ
        if hasattr(request, '_start_time'):
            response_time = (time.time() - request._start_time) * 1000  # به میلی‌ثانیه
        else:
            response_time = None

        # دریافت IP آدرس
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')

        # دریافت کاربر (اگر لاگین باشد)
        user = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user

        # دریافت query string
        query_string = request.GET.urlencode() if request.GET else None

        # ثبت لاگ (به صورت async یا در پس‌زمینه برای جلوگیری از کند شدن)
        try:
            RequestLog.objects.create(
                method=request.method,
                path=request.path[:500],  # محدود کردن طول مسیر
                query_string=query_string[:1000] if query_string else None,  # محدود کردن طول
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                referer=request.META.get('HTTP_REFERER', '')[:500] if request.META.get('HTTP_REFERER') else None,
                status_code=response.status_code,
                response_time=response_time,
                user=user,
            )
        except Exception as e:
            # در صورت خطا، لاگ را در console ثبت می‌کنیم تا برنامه متوقف نشود
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"خطا در ثبت لاگ درخواست: {e}")

        return response

