import pandas as pd
from django.contrib import admin, messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import ListView, DetailView

from .forms import VakilSearchForm, AdminContactForm, ArticleSearchForm
from .models import Article, Category, Vakil, Riyasat, Comision, ArticleImage, ArticleFile
import zipfile
import os
from django.conf import settings
from django.core.files import File


# Create your views here.

import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Vakil


def upload_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES['excel_file']
        if excel_file.name.endswith('.xlsx') or excel_file.name.endswith('.xls'):
            try:
                df = pd.read_excel(excel_file)
                for index, row in df.iterrows():
                    # مسیر فایل عکس
                    image_name = row['عکس']
                    image_path = os.path.join(settings.MEDIA_ROOT, 'images', image_name)

                    # ایجاد نمونه مدل Vakil
                    vakil = Vakil(
                        name=row['نام'],
                        code=row['شماره پروانه'],
                        gender=row['جنسیت'],
                        date=row['تاریخ انقضا'],
                        lastname=row['نام خانوادگی'],
                        address=row['آدرس'],
                        city=row['شهر'],
                        thumbnail=row['عکس']
                    )

                    # اختصاص عکس به مدل
                    if os.path.exists(image_path):
                        with open(image_path, 'rb') as f:
                            vakil.thumbnail.save(image_name, File(f), save=True)
                    vakil.save()

                messages.success(request, 'داده‌ها با موفقیت اضافه شدند.')
            except Exception as e:
                messages.error(request, f'خطا در پردازش فایل اکسل: {str(e)}')
        else:
            messages.error(request, 'فایل باید در فرمت اکسل (xlsx یا xls) باشد.')
        return redirect('home:upload_excel')
    return render(request, 'home/upload_excel.html')

class ArticleList(View):

    form_class = ArticleSearchForm

    def get(self,request):
        article = Article.objects.published()
        if 'search' in request.GET:
            form = ArticleSearchForm(request.GET)
            if form.is_valid():
                cd = form.cleaned_data('search')
                article = article.filter(Q(title__icontains=cd) |Q(description__icontains=cd))
        heyatmodireh = Riyasat.objects.all()
        paginator = Paginator(article, 3)  # Show 25 contacts per page.
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        return render(request,'home/home.html',{'article':article,'heyatmodireh':heyatmodireh,"page_obj": page_obj,'form':self.form_class})


class ArticleDetail(View):
    def get(self, request, slug):
        article = get_object_or_404(Article.objects.published(), slug=slug)
        aks = ArticleImage.objects.filter(article=article).all()
        files = ArticleFile.objects.filter(article=article)
        return render(request, 'home/post_detail.html', {'article': article, 'aks': aks, 'files': files})

class VokalaView(View):
    form_class = VakilSearchForm
    def get(self,request):
        vakils = Vakil.objects.all()
        if request.GET.get('search') :
            vakils = vakils.filter(name__contains = request.GET['search'])
        return render(request,'home/vokala.html',{'vakils':vakils,'form':self.form_class})

class ArticlePreview(DetailView):
    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Article, pk=pk)


class CategoryList(ListView):
    paginate_by = 5
    template_name = 'home/category_list.html'
    def get_queryset(self):
        global category
        slug = self.kwargs.get('slug')
        category = get_object_or_404(Category.objects.active(), slug=slug)
        return category.articles.published()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = category
        return context


class SearchList(ListView):
    paginate_by = 1
    template_name = 'home/vokala.html'

    def get_queryset(self):
        search = self.request.GET.get('q')
        return Article.objects.published().filter(Q(description__icontains=search) | Q(title__icontains=search))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q')
        return context

class VakilPage(View):
    def get(self,request,id):
        vakil = Vakil.objects.get(id=id)
        return render(request,'home/vakilpage.html',{'vakil':vakil})

class VakilCity(View):
    # paginate_by = 2
    def get(self,request,city):
        vakils = Vakil.objects.filter(city=city)
        paginator = Paginator(vakils, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request,'home/vakil_detail.html',{'vakils':vakils,'page_obj': page_obj})



class ComisionView(View):
    def get(self,request):
        comi = Comision.objects.all()
        return render(request,'account/comision.html',{'comi':comi})


class ComisionDetailView(View):
    def get(self,request,id):
        comi = Comision.objects.get(id=id)

        return render(request,'account/comision-create-update.html',{'comi':comi})

class UpdateImageView(View):
    def post(self,request):
        selected_action = request.POST.getlist('_selected_action')
        if selected_action :
            model_admin = admin.site._registry[Vakil]
            print(Vakil.objects.filter(pk__in = selected_action))
            print('mm')
            return model_admin.update_image(request, Vakil.objects.filter(pk__in = selected_action))

        return redirect('/')


class Contact(View):

    form_class = AdminContactForm

    def get(self,request):
        return render(request,'home/contact2.html',{'form':self.form_class})

    def post(self, request, *args, **kwargs) :
        form = self.form_class(request.POST)
        if form.is_valid() :
            form.save()
            messages.success(request, 'your comment submitted successfully', 'success')
            return redirect('/')

