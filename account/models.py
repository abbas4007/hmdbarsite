from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
	email = models.EmailField(unique=True, verbose_name='ایمیل')

	is_author = models.BooleanField(default=False, verbose_name="وضعیت نویسندگی")
	special_user = models.DateTimeField(default=timezone.now, verbose_name="کاربر ویژه تا")

	def is_special_user(self):
		if self.special_user > timezone.now():
			return True
		else:
			return False
	is_special_user.boolean = True


class ContactMessage(models.Model) :
    STATUS_CHOICES = [
        ('pending', 'در انتظار پاسخ'),
        ('replied', 'پاسخ داده شده'),
    ]

    full_name = models.CharField(blank = True, null = True,max_length = 200, verbose_name = 'نام کامل')
    email = models.EmailField(verbose_name = 'ایمیل')
    phone = models.CharField(max_length = 15, verbose_name = 'شماره تماس')
    subject = models.CharField(max_length = 200, verbose_name = 'موضوع')
    message = models.TextField(verbose_name = 'پیام')
    created_at = models.DateTimeField(auto_now_add = True, verbose_name = 'تاریخ ارسال')
    status = models.CharField(max_length = 10, choices = STATUS_CHOICES, default = 'pending', verbose_name = 'وضعیت')
    response = models.TextField(blank = True, null = True, verbose_name = 'پاسخ')

    class Meta :
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیامهای تماس'

    def __str__(self) :
        return f"{self.full_name} - {self.subject}"
