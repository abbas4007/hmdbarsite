from django.contrib import admin, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from psycopg2 import IntegrityError

from .forms import VakilSearchForm, AdminContactForm, ArticleSearchForm
from .models import Article, Category, Vakil, Riyasat, Comision, ArticleImage, ArticleFile
import pandas as pd
from django.db import transaction, IntegrityError
from datetime import datetime
from django.http import HttpResponseForbidden

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
    def get(self, request, slug):
        article = get_object_or_404(Article.objects.published(), slug=slug)
        images = ArticleImage.objects.filter(article=article)
        files = ArticleFile.objects.filter(article=article)

        # خبرهای مرتبط بر اساس تگ‌ها
        related_articles = Article.objects.published().filter(
            tags__in=article.tags.all()
        ).exclude(id=article.id).distinct()[:6]

        return render(request, 'home/post_detail.html', {
            'article': article,
            'imagess': images,
            'files': files,
            'related_articles': related_articles,
        })

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y/%m/%d').date()
            except:
                return None

class UploadExcelView(LoginRequiredMixin, UserPassesTestMixin, View):
    login_url = '/accounts/login/'
    template_name = 'home/upload_excel.html'

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        try:
            excel_file = request.FILES.get('excel_file')

            if not excel_file:
                messages.error(request, 'فایلی ارسال نشده است')
                return redirect('home:upload_excel')

            if not excel_file.name.endswith(('.xls', '.xlsx')):
                messages.error(request, 'فقط فایل‌های Excel مجاز هستند')
                return redirect('home:upload_excel')

            if excel_file.size > 2 * 1024 * 1024:
                messages.error(request, 'حجم فایل بیش از ۲ مگابایت است')
                return redirect('home:upload_excel')

            df = pd.read_excel(excel_file)
            df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

            required_columns = ['نام', 'نام_خانوادگی', 'شماره_پروانه', 'جنسیت', 'تاریخ_انقضا', 'شهر', 'آدرس']
            if not all(col in df.columns for col in required_columns):
                missing = set(required_columns) - set(df.columns)
                messages.error(request, f'ستون‌های ضروری وجود ندارند: {", ".join(missing)}')
                return redirect('home:upload_excel')

            if len(df) > 500:
                messages.error(request, 'تعداد ردیف‌های فایل بیش از حد مجاز است (حداکثر ۵۰۰)')
                return redirect('home:upload_excel')

            duplicates = df[df.duplicated('شماره_پروانه', keep=False)]
            if not duplicates.empty:
                messages.warning(request, f'ردیف‌های تکراری در فایل اکسل: {len(duplicates)} مورد')
                return redirect('home:upload_excel')

            success_count = 0
            errors = []

            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        date_str = str(row['تاریخ_انقضا']).strip()
                        expiry_date = parse_date(date_str)
                        if not expiry_date:
                            errors.append(f'ردیف {index + 2}: فرمت تاریخ نامعتبر - {date_str}')
                            continue

                        gender = str(row['جنسیت']).strip()
                        if gender not in ['مرد', 'زن']:
                            errors.append(f'ردیف {index + 2}: جنسیت نامعتبر - {gender}')
                            continue

                        vakil, created = Vakil.objects.update_or_create(
                            code=row['شماره_پروانه'],
                            defaults={
                                'name': row['نام'],
                                'lastname': row['نام_خانوادگی'],
                                'gender': 'M' if gender == 'مرد' else 'F',
                                'date': expiry_date,
                                'city': row['شهر'],
                                'address': row['آدرس'],
                            }
                        )
                        vakil.save()
                        success_count += 1

                    except IntegrityError:
                        errors.append(f'ردیف {index + 2}: شماره پروانه تکراری - {row["شماره_پروانه"]}')
                    except Exception as e:
                        errors.append(f'ردیف {index + 2}: {str(e)}')

            if errors:
                messages.error(request, f'{len(errors)} خطا رخ داد. اولین خطاها: {" | ".join(errors[:3])}')
            if success_count > 0:
                messages.success(request, f'{success_count} وکیل با موفقیت پردازش شدند!')

        except Exception as e:
            messages.error(request, f'خطا در پردازش فایل: {str(e)}')

        return redirect('home:upload_excel')

class VokalaView(View):
    form_class = VakilSearchForm

    def get(self, request):
        form = self.form_class(request.GET or None)
        vakils = Vakil.objects.all()
        if form.is_valid():
            search_query = form.cleaned_data.get('search')
            if search_query:
                vakils = vakils.filter(
                    Q(name__icontains=search_query) |
                    Q(lastname__icontains=search_query)
                )
        return render(request, 'home/vokala.html', {'vakils': vakils, 'form': form})

class ArticlePreview(LoginRequiredMixin, DetailView):
    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Article, pk=pk)

class CategoryList(ListView):
    paginate_by = 5
    template_name = 'home/category_list.html'

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        self.category = get_object_or_404(Category.objects.active(), slug=slug)
        return self.category.articles.published()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context

class SearchList(ListView):
    paginate_by = 10
    template_name = 'blog/search_list.html'

    def get_queryset(self):
        search = self.request.GET.get('q')
        return Article.objects.published().filter(Q(description__icontains=search) | Q(title__icontains=search))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q')
        return context

class VakilPage(View):
    def get(self, request, id):
        vakil = get_object_or_404(Vakil, id=id)
        return render(request, 'home/vakilpage.html', {'vakil': vakil})

class VakilCity(View):
    def get(self, request, city):
        vakils = Vakil.objects.filter(city_slug=city)
        paginator = Paginator(vakils, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'home/vakil_detail.html', {'vakils': vakils, 'page_obj': page_obj})

class ComisionView(LoginRequiredMixin, View):
    def get(self, request):
        comi = Comision.objects.all()
        return render(request, 'account/comision.html', {'comi': comi})

class ComisionDetailView(LoginRequiredMixin, View):
    def get(self, request, id):
        comi = get_object_or_404(Comision, id=id)
        return render(request, 'account/comision-create-update.html', {'comi': comi})

class UpdateImageView(LoginRequiredMixin, View):
    def post(self, request):
        if not request.user.is_staff:
            return HttpResponseForbidden('دسترسی غیرمجاز')
        selected_action = request.POST.getlist('_selected_action')
        if selected_action:
            model_admin = admin.site._registry[Vakil]
            return model_admin.update_image(request, Vakil.objects.filter(pk__in=selected_action))
        return redirect('/')

class Contact(View):
    form_class = AdminContactForm

    def get(self, request):
        return render(request, 'home/contact2.html', {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'پیام شما با موفقیت ارسال شد', 'success')
            return redirect('/')
        messages.error(request, 'ارسال پیام با خطا مواجه شد')
        return render(request, 'home/contact2.html', {'form': form})
