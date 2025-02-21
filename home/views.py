from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from psycopg2 import IntegrityError

from .forms import VakilSearchForm, AdminContactForm, ArticleSearchForm
from .models import Article, Category, Vakil, Riyasat, Comision, ArticleImage, ArticleFile
import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction, IntegrityError
from datetime import datetime

# Create your views here.
class ArticleSearchList(ListView):
    model = Article
    template_name = 'home/home.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Article.objects.published().filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
        return Article.objects.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class ArticleList(ArticleSearchList):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['heyatmodireh'] = Riyasat.objects.all()
        return context

class ArticleDetail(View):
    def get(self,request,slug):
        article = get_object_or_404(Article.objects.published(), slug=slug)
        images = ArticleImage.objects.filter(article = article)
        files = ArticleFile.objects.filter(article = article)
        return render(request, 'home/post_detail.html', {'article' : article, 'imagess' : images, 'files' : files})


def parse_date(date_str) :
    """
    تابع کمکی برای تبدیل رشته تاریخ به شیء تاریخ
    """
    try :
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError :
        try :
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
        except ValueError :
            try :
                return datetime.strptime(date_str, '%Y/%m/%d').date()
            except :
                return None


class UploadExcelView(LoginRequiredMixin, View) :
    login_url = '/accounts/login/'  # آدرس صفحه لاگین
    template_name = 'home/upload_excel.html'  # نام تمپلیت

    def get(self, request) :
        return render(request, self.template_name)

    def post(self, request) :
        try :
            # دریافت فایل اکسل
            excel_file = request.FILES['excel_file']

            # خواندن فایل اکسل با pandas
            df = pd.read_excel(excel_file)

            # تبدیل نام ستون‌ها به حروف کوچک و جایگزینی فاصله با زیرخط
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            # ستون‌های ضروری
            required_columns = ['نام', 'نام_خانوادگی', 'شماره_پروانه', 'جنسیت',
                                'تاریخ_انقضا', 'شهر', 'آدرس']

            # بررسی وجود ستون‌های ضروری
            if not all(col in df.columns for col in required_columns) :
                missing = set(required_columns) - set(df.columns)
                messages.error(request, f'ستون‌های ضروری وجود ندارند: {", ".join(missing)}')
                return redirect('home:upload_excel')

            # بررسی ردیف‌های تکراری در فایل اکسل
            duplicates = df[df.duplicated('شماره_پروانه', keep = False)]
            if not duplicates.empty :
                messages.warning(request, f'ردیف‌های تکراری در فایل اکسل: {len(duplicates)} مورد')
                return redirect('home:upload_excel')

            success_count = 0
            errors = []

            # شروع تراکنش دیتابیس
            with transaction.atomic() :
                for index, row in df.iterrows() :
                    try :
                        # تبدیل تاریخ
                        date_str = str(row['تاریخ_انقضا']).strip()
                        expiry_date = parse_date(date_str)

                        # اعتبارسنجی تاریخ
                        if not expiry_date :
                            errors.append(f'ردیف {index + 2}: فرمت تاریخ نامعتبر - {date_str}')
                            continue

                        # اعتبارسنجی جنسیت
                        gender = str(row['جنسیت']).strip()
                        if gender not in ['مرد', 'زن'] :
                            errors.append(f'ردیف {index + 2}: جنسیت نامعتبر - {gender}')
                            continue

                        # ایجاد یا به‌روزرسانی وکیل
                        vakil, created = Vakil.objects.update_or_create(
                            code = row['شماره_پروانه'],
                            defaults = {
                                'name' : row['نام'],
                                'lastname' : row['نام_خانوادگی'],
                                'gender' : 'M' if gender == 'مرد' else 'F',
                                'date' : expiry_date,
                                'city' : row['شهر'],
                                'address' : row['آدرس'],
                            }
                        )
                        success_count += 1

                        # فراخوانی متد save برای تنظیم city_slug
                        vakil.save()

                    except IntegrityError as e :
                        errors.append(f'ردیف {index + 2}: شماره پروانه تکراری - {row["شماره_پروانه"]}')
                    except Exception as e :
                        errors.append(f'ردیف {index + 2}: {str(e)}')

            # نمایش پیام‌ها به کاربر
            if errors :
                messages.error(request, f'{len(errors)} خطا رخ داد. اولین خطاها: {" | ".join(errors[:3])}')
            if success_count > 0 :
                messages.success(request, f'{success_count} وکیل با موفقیت پردازش شدند!')

        except Exception as e :
            messages.error(request, f'خطا در پردازش فایل: {str(e)}')

        return redirect('home:upload_excel')

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
    template_name = 'blog/search_list.html'

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


class VakilCity(View) :
    def get(self, request, city) :
        vakils = Vakil.objects.filter(city_slug = city)
        paginator = Paginator(vakils, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'home/vakil_detail.html', {'vakils' : vakils, 'page_obj' : page_obj})


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
        return render(request, 'home/../../account/templates/account/contact2.html', {'form':self.form_class})

    def post(self, request, *args, **kwargs) :
        form = self.form_class(request.POST)
        if form.is_valid() :
            form.save()
            messages.success(request, 'your comment submitted successfully', 'success')
            return redirect('/')