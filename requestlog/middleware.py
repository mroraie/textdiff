import time
import logging
from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog
from comparator.algorithms.constants import (
    MAX_PATH_LENGTH,
    MAX_QUERY_STRING_LENGTH,
    MAX_USER_AGENT_LENGTH,
    MAX_REFERER_LENGTH,
)

logger = logging.getLogger(__name__)


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
        # استفاده از logging به جای دیتابیس برای لاگ‌های معمولی
        # یا می‌توان از Celery برای async logging استفاده کرد
        try:
            # Log to database (can be optimized with async queue in production)
            RequestLog.objects.create(
                method=request.method,
                path=request.path[:MAX_PATH_LENGTH],
                query_string=query_string[:MAX_QUERY_STRING_LENGTH] if query_string else None,
                ip_address=ip_address,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:MAX_USER_AGENT_LENGTH],
                referer=request.META.get('HTTP_REFERER', '')[:MAX_REFERER_LENGTH] if request.META.get('HTTP_REFERER') else None,
                status_code=response.status_code,
                response_time=response_time,
                user=user,
            )
        except Exception as e:
            # در صورت خطا، لاگ را در console ثبت می‌کنیم تا برنامه متوقف نشود
            logger.error(f"Error logging request to database: {e}", exc_info=True)

        return response

