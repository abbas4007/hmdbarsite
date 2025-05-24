import os
import uuid
from io import BytesIO
from django.conf import settings
from taggit.managers import TaggableManager
from django_jalali.db import models as jmodels

from autoslug import AutoSlugField
from ckeditor.fields import RichTextField

import arabic_reshaper
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display
from django.core.files.base import ContentFile
from django.core.files.storage import DefaultStorage, default_storage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from slugify import slugify
from django_ckeditor_5.fields import CKEditor5Field

from account.models import User
from djangohmdbar import settings
from djangohmdbar.settings import BASE_DIR
from extensions.utils import jalali_converter


# from comment.models import Comment

# my managers
class ArticleManager(models.Manager):
    def published(self):
        return self.filter(status='p')


class CategoryManager(models.Manager):
    def active(self):
        return self.filter(status=True)




class Category(models.Model):
    parent = models.ForeignKey('self', default=None, null=True, blank=True, on_delete=models.SET_NULL, related_name='children', verbose_name="زیردسته")
    title = models.CharField(max_length=200, verbose_name="عنوان دسته‌بندی")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="آدرس دسته‌بندی",blank=True,null=True)
    status = models.BooleanField(default=True, verbose_name="آیا نمایش داده شود؟")
    position = models.IntegerField(verbose_name="پوزیشن")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی ها"
        ordering = ['parent__id', 'position']

    def __str__(self):
        return self.title

    objects = CategoryManager()


def text_wrap(text, font, max_width) :
    lines = []
    # If the width of the text is smaller than image width
    # we don't need to split it, just add it to the lines array
    # and return
    if font.getsize(text)[0] <= max_width :
        lines.append(text)
    else :
        # split the line by spaces to get words
        words = text.split(' ')
        i = 0
        # append every word to a line while its width is shorter than image width
        while i < len(words) :
            line = ''
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width :
                line = line + words[i] + " "
                i += 1
            if not line :
                line = words[i]
                i += 1
            # when the line gets longer than the max width do not append the word,
            # add the line to the lines array
            lines.append(line)
    return lines


class Article(models.Model):
    STATUS_CHOICES = (
        ('d', 'پیش‌نویس'),
        ('p', 'منتشر شده'),
        ('i', 'در حال بررسی'),
        ('b', 'برگشت داده شده'),
    )

    author = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='articles', verbose_name="نویسنده", blank=True, null=True)
    title = models.CharField(max_length=200, verbose_name="عنوان مقاله")
    slug = AutoSlugField(populate_from='title', unique=True, always_update=True, max_length=100, verbose_name="آدرس مقاله", blank=True, null=True, editable=True)
    category = models.ManyToManyField(Category, verbose_name="دسته‌بندی", related_name="articles")
    description = CKEditor5Field(verbose_name="محتوا")
    thumbnail = models.ImageField(upload_to="article_images/",storage=DefaultStorage() ,verbose_name="تصویر مقاله", blank=True, null=True)
    publish = jmodels.jDateField(verbose_name= "تاریخ انتشار" ,auto_now_add = True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_special = models.BooleanField(default=False, verbose_name="مقاله ویژه")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, verbose_name="وضعیت")
    file = models.FileField(blank=True, null=True)
    video = models.FileField(blank=True, null=True, verbose_name="ویدیو")
    tags = TaggableManager(verbose_name = "برچسب‌ها", help_text = "برچسب‌ها را با کاما جدا کنید." ,blank = True)


    class Meta:
        verbose_name = "مقاله"
        verbose_name_plural = "مقالات"
        ordering = ['-publish']

    objects = ArticleManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("account:home")

    def jpublish(self):
        return jalali_converter(self.created)
    jpublish.short_description = "زمان انتشار"

    def thumbnail_tag(self):
        return format_html("<img width=100 height=75 style='border-radius: 5px;' src='{}'>".format(self.thumbnail.url))
    thumbnail_tag.short_description = "عکس"

    def category_to_str(self):
        return "، ".join([category.title for category in self.category.active()])
    category_to_str.short_description = "دسته‌بندی"

    def save(self, *args, **kwargs) :
        if not self.slug :
            self.slug = slugify(self.title, allow_unicode = True)
        super().save(*args, **kwargs)

    def create_image_with_title(self, title) :
        file = 'C:\\Users\\hmdbar\\PycharmProjects\\hamedanbar\\hamedanbar\\static\\font\\BTitr.ttf'
        base = Image.open('image/default_image.jpg')
        draw = ImageDraw.Draw(base)
        font = ImageFont.truetype(font = file, size = 36)
        def wrap_text(text, font, max_width) :
            lines = []
            words = text.split()
            current_line = ""

            for word in words :
                test_line = f"{current_line} {word}".strip()
                if draw.textlength(test_line, font = font) <= max_width :
                    current_line = test_line
                else :
                    lines.append(current_line)
                    current_line = word

            if current_line :
                lines.append(current_line)

            return lines
        max_width = 600
        wrapped_text_lines = wrap_text(title, font, max_width)

        y_position = 200
        for line in wrapped_text_lines :
            reshaped_text = arabic_reshaper.reshape(line)
            bidi_text = get_display(reshaped_text)
            draw.text((380, y_position), bidi_text, fill = "black", font = font, anchor = "mm", align = "center")
            y_position += font.getbbox(line)[1] + 45

        img_io = BytesIO()
        base.save(img_io, format = 'PNG')

        img_file = ContentFile(img_io.getvalue(), 'article_image.jpg')

        return img_file



    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.thumbnail:
            img = Image.open(self.thumbnail)

            desired_ratio = 16 / 9
            width, height = img.size
            current_ratio = width / height

            if current_ratio > desired_ratio:
                # عرض زیاد است → کراپ از عرض
                new_width = int(height * desired_ratio)
                left = (width - new_width) // 2
                img = img.crop((left, 0, left + new_width, height))
            elif current_ratio < desired_ratio:
                # ارتفاع زیاد است → کراپ از ارتفاع
                new_height = int(width / desired_ratio)
                top = (height - new_height) // 2
                img = img.crop((0, top, width, top + new_height))

            img = img.resize((1200, 680), Image.Resampling.LANCZOS)

            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG', quality=85)

            self.thumbnail.save(
                self.thumbnail.name,
                ContentFile(thumb_io.getvalue()),
                save=False
            )
            super().save(update_fields=['thumbnail'])  # فقط thumbnail رو دوباره ذخیره کن



class ArticleFile(models.Model) :
    article = models.ForeignKey(Article, on_delete = models.CASCADE, related_name = 'files')
    file = models.FileField(upload_to = 'article_files/',blank=True, null=True)
    name = models.CharField(max_length = 50,blank=True, null=True)


    def __str__(self) :
        return f"{self.article.title} - {self.file.name}"


class ArticleImage(models.Model) :
    article = models.ForeignKey(Article, on_delete = models.CASCADE, related_name = 'images')
    image = models.ImageField(upload_to = 'article_images/',blank = True,null = True)

    def __str__(self) :
        return f"Image for {self.article.title}"

class ArticleHit(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class Vakil(models.Model):
    GENDER_CHOICES = (
        ('M', 'مرد'),
        ('F', "زن"),
    )
    CITY_CHOICES = (
        ('همدان', 'همدان'),
        ('کبودراهنگ', 'کبودراهنگ'),
        ('ملایر', 'ملایر'),
        ('اسدآباد', 'اسدآباد'),  # اضافه کنید
        ('نهاوند', 'نهاوند'),  # اضافه کنید
        ('تویسرکان', 'تویسرکان'),  # اضافه کنید
        ('رزن', 'رزن'),  # اضافه کنید
        ('درگزین', 'درگزین'),  # اضافه کنید
        ('بهار', 'بهار'),  # اضافه کنید
        ('فامنین', 'فامنین'),  # اضافه کنید
    )
    CITY_MAPPING = {
        'همدان' : 'hamedan',
        'کبودراهنگ' : 'kabudrahang',
        'ملایر' : 'malayer',
        'اسدآباد' : 'asadabad',
        'نهاوند' : 'nahavand',
        'تویسرکان' : 'tuyserkan',
        'رزن' : 'razan',
        'درگزین' : 'dargazin',
        'بهار' : 'bahar',
        'فامنین' : 'famenin',
    }

    name = models.CharField(max_length=100, verbose_name="نام", blank=True, null=True)
    code = models.IntegerField(blank=True, null=True, verbose_name="شماره پروانه")
    gender = models.CharField(blank=True, null=True, max_length=1, choices=GENDER_CHOICES, verbose_name="جنسیت")
    year = models.DateTimeField(verbose_name=" سال",blank=True, null=True)
    month = models.DateTimeField(verbose_name=" ماه",blank=True, null=True)
    day = models.DateTimeField(verbose_name=" روز",blank=True, null=True)
    lastname = models.CharField(blank=True, null=True, max_length=150, verbose_name="نام خانوادگی")
    address = models.TextField(blank=True, null=True, verbose_name="آدرس")
    thumbnail = models.ImageField(upload_to="images", verbose_name="تصویر وکیل", blank=True, null=True)
    city = models.CharField(
        max_length = 150,
        choices = CITY_CHOICES,
        verbose_name = 'شهر',
        blank = True,
        null = True
    )
    city_slug = models.SlugField(max_length = 150, blank = True, verbose_name = "اسلاگ شهر")
    phone = models.CharField(max_length = 11, verbose_name = 'شماره تماس دفتر' ,  blank = True,null = True)
    mobile = models.CharField(max_length = 11, verbose_name = 'شماره موبایل',blank = True,null = True)

    def save(self, *args, **kwargs) :
        if self.city :
            self.city_slug = self.CITY_MAPPING.get(self.city, slugify(self.city))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} {self.lastname}"



    def jpublish(self):
        return jalali_converter(self.date)
    jpublish.short_description = "تاریخ انقضا"

    def thumbnail_tag(self):
        if self.thumbnail:
            return format_html("<img width=100 height=75 style='border-radius: 5px;' src='{}'>".format(self.thumbnail.url))
    thumbnail_tag.short_description = "عکس"

class Riyasat(models.Model):
    vakil = models.ForeignKey(Vakil,on_delete = models.CASCADE,related_name = 'vakils',verbose_name = 'وکیل' ,blank = True,null = True)
    role  = models.CharField(max_length = 50,verbose_name = 'نقش')

    def __str__(self):
        return str(self.vakil)






class Comision(models.Model):
    name = models.CharField(max_length=150, unique=True)
    vakils = models.ManyToManyField(Vakil, related_name='comisions')
    chairman = models.ForeignKey(Vakil, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_comisions')

    def __str__(self):
        return self.name

class Comment(models.Model):
    name= models.CharField(max_length = 150,blank = True,null = True)
    lastname = models.CharField(max_length = 150,blank = True,null = True)
    mobile =models.CharField(max_length = 11,blank = True,null = True)
    message = models.TextField(blank = True,null = True)


@receiver(pre_save, sender = Article)
def generate_article_slug(sender, instance, **kwargs) :
    if not instance.slug :  # فقط اگر Slug خالی است آن را تولید کن
        instance.slug = slugify(instance.title, allow_unicode = True)  # فارسی پشتیبانی می‌شود