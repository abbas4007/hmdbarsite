from django.contrib import admin
from django.urls import reverse

from . import models
from .models import  ArticleFile,Comment, Article, Category, Vakil, Riyasat, ArticleImage,Comision
from import_export.admin import ImportExportModelAdmin
import pandas as pd
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django import forms
import csv

from .forms import ImageForm

# Admin header change
admin.site.site_header = "وبلاگ جنگویی من"
from import_export.admin import ImportExportModelAdmin


class CsvImportForm(forms.Form) :
    csv_file = forms.FileField()


class VakilAdmin(ImportExportModelAdmin, admin.ModelAdmin) :
    list_display = ('name', 'lastname', 'address', 'thumbnail_tag', 'jpublish', 'gender', 'code',)
    list_filter = ('code', 'name', 'lastname')
    search_fields = ('name', 'code')
    ordering = ['code', '-date']
    # change_form_template ="change_list.html"
    actions = ['update_image']

    def import_csv(request) :
        if request.method == 'POST' :

            form = CsvImportForm(request.POST, request.FILES)

            if form.is_valid() :
                csv_file = request.FILES['csv_file'].read().decode('utf-8').splitlines()
                csv_reader = csv.DictReader(csv_file)

                for row in csv_reader :
                    Vakil.objects.create(
                        code = row['code'],
                        name = row['name'],
                        lastname = row['lastname'],
                        date = row['date'],
                        gender = row['gender'],
                        address = row['address'],
                        city = row['city'],
                        id = row['id'],
                        # thumbnail = row['thumbnail']

                    )

                return redirect('success_page')  # Redirect to a success page
        else :
            form = CsvImportForm()

        return render(request, 'admin/import.html', {'form' : form})

    def admin_action_url(self) :
        return reverse('admin:%s_%s_update_image' % (self.model._meta.app_label, self.model._meta.model_name))

    # def update_image(self, request, s):
    #     for obj in s:
    #         obj.thumbnail = request.FILES['thumbnail']
    #         obj.save()
    #
    #     return redirect('/')
    # update_image.short_description = "Update Image with Custom File"

    def update_image(self, request, s) :
        for obj in s :
            # obj.thumbnail = request.FILES['thumbnail']
            # obj.save()
            print(request.FILES['thumbnail'])

        return redirect('/')

    update_image.short_description = "Update Image with Custom File"


# Register your models here.
def make_published(modeladmin, request, queryset) :
    rows_updated = queryset.update(status = 'p')
    if rows_updated == 1 :
        message_bit = "منتشر شد."
    else :
        message_bit = "منتشر شدند."
    modeladmin.message_user(request, "{} مقاله {}".format(rows_updated, message_bit))


make_published.short_description = "انتشار مقالات انتخاب شده"


def make_draft(modeladmin, request, queryset) :
    rows_updated = queryset.update(status = 'd')
    if rows_updated == 1 :
        message_bit = "پیش‌نویس شد."
    else :
        message_bit = "پیش‌نویس شدند."
    modeladmin.message_user(request, "{} مقاله {}".format(rows_updated, message_bit))


make_draft.short_description = "پیش‌نویس شدن مقالات انتخاب شده"


class CategoryAdmin(admin.ModelAdmin) :
    list_display = ('position', 'title', 'slug', 'parent', 'status')
    list_filter = (['status'])
    search_fields = ('title', 'slug')
    prepopulated_fields = {'slug' : ('title',)}


admin.site.register(Category, CategoryAdmin)


class ArticleImageAdmin(admin.StackedInline) :
    model = ArticleImage

class ArticleFileAdmin(admin.StackedInline) :
    model = ArticleFile


class ArticleAdmin(admin.ModelAdmin) :
    inlines = [ArticleImageAdmin,ArticleFileAdmin]

    class Meta :
        model = Article

    list_display = ('title', 'thumbnail_tag', 'slug', 'author', 'jpublish', 'is_special', 'status', 'category_to_str')
    list_filter = ('publish', 'status', 'author')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug' : ('title',)}
    ordering = ['-status', '-publish']
    actions = [make_published, make_draft]


@admin.register(ArticleImage)
class ArticleImageAdmin(admin.ModelAdmin) :
    pass

@admin.register(ArticleFile)
class ArticleFileAdmin(admin.ModelAdmin) :
    pass


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'slug')
    readonly_fields = ('slug',)

admin.site.register(Vakil, VakilAdmin)
admin.site.register(Riyasat)
admin.site.register(Comment)
admin.site.register(Comision)
