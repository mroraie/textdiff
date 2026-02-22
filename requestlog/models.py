from django.db import models
from django.utils import timezone


class RequestLog(models.Model):
    """
    مدل برای ذخیره اطلاعات درخواست‌های HTTP
    """
    method = models.CharField(max_length=10, verbose_name='متد')
    path = models.CharField(max_length=500, verbose_name='مسیر')
    query_string = models.TextField(blank=True, null=True, verbose_name='پارامترهای Query')
    ip_address = models.GenericIPAddressField(verbose_name='آدرس IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    referer = models.URLField(blank=True, null=True, verbose_name='Referer')
    status_code = models.IntegerField(blank=True, null=True, verbose_name='کد وضعیت')
    response_time = models.FloatField(blank=True, null=True, verbose_name='زمان پاسخ (میلی‌ثانیه)')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='زمان ثبت')
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='کاربر'
    )

    class Meta:
        verbose_name = 'لاگ درخواست'
        verbose_name_plural = 'لاگ‌های درخواست'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['path']),
            models.Index(fields=['method']),
            models.Index(fields=['status_code']),
        ]

    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code or 'N/A'} - {self.timestamp}"
