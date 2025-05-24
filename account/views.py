from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests

from home.models import Article, Vakil, Riyasat, ArticleImage, ArticleFile, Comision
from .forms import ImageForm, ComisionForm, RaeesForm, ContactForm, ArticleForm, ArticleImageForm, ArticleImageFormSet
from .models import ContactMessage

# --- تماس با ما ---
@csrf_exempt
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save()
            try:
                response = requests.post(
                    "https://api.ghasedak.me/v2/sms/send/simple",
                    data={
                        "message": f"پیام شما با شماره پیگیری {message.id} دریافت شد",
                        "receptor": message.phone,
                        "linenumber": settings.SMS_LINE_NUMBER
                    },
                    headers={
                        "apikey": settings.GHASEDAK_API_KEY,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    timeout=10
                )
            except requests.exceptions.RequestException as e:
                print("SMS Error:", str(e))
            return redirect('account:success_page')
    else:
        form = ContactForm()
    return render(request, 'account/contact.html', {'form': form})


def success_page(request):
    return render(request, 'account/success.html')


# --- مدیریت پیام‌ها ---
class MessageListView(LoginRequiredMixin, ListView):
    model = ContactMessage
    template_name = 'account/message_list.html'
    context_object_name = 'messages'
    ordering = ['-created_at']
    paginate_by = 10


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = ContactMessage
    fields = ['status', 'response']
    template_name = 'account/message_form.html'
    success_url = reverse_lazy('account:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get('response'):
            try:
                payload = {
                    "message": f"پاسخ به پیام شما:\n{form.cleaned_data['response']}",
                    "receptor": self.object.phone,
                    "linenumber": settings.SMS_LINE_NUMBER
                }
                headers = {
                    "apikey": settings.GHASEDAK_API_KEY,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                requests.post("https://api.ghasedak.me/v2/sms/send/simple", data=payload, headers=headers)
            except Exception as e:
                print("SMS Response Error:", str(e))
        return response


# --- ورود ---
class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('account:home')


# --- مقاله ---
class ArticleList(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 6
    template_name = "account/home.html"
    context_object_name = "object_list"

    def get_queryset(self):
        query = self.request.GET.get("q")
        queryset = super().get_queryset()
        if query:
            queryset = queryset.filter(Q(title__icontains=query))
        return queryset

@login_required
def article_create_view(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        images = request.FILES.getlist('images')

        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user  # یا هر شرطی برای نویسنده
            article.save()
            form.save_m2m()

            # ذخیره تصاویر گالری
            for image in images:
                ArticleImage.objects.create(article=article, image=image)

            messages.success(request, "مقاله با موفقیت ذخیره شد.")
            return redirect('home:detail', slug=article.slug)  # تغییر به آدرس درست شما

        else:
            messages.error(request, "لطفاً خطاهای فرم را بررسی کنید.")
    else:
        form = ArticleForm()

    return render(request, 'account/article-create-update.html', {
        'form': form
    })

# class ArticleCreateView(CreateView):
#     model = Article
#     form_class = ArticleForm
#     template_name = "account/article-create-update.html"
#     success_url = reverse_lazy('account:home')
#
#     # def form_valid(self, form) :
#     #     try :
#     #         # چاپ برای دیباگ
#     #         print("FILES:", self.request.FILES)
#     #         print("POST:", self.request.POST)
#     #
#     #         article = form.save(commit = False)
#     #         if not article.author :
#     #             article.author = self.request.user
#     #         article.save()
#     #         form.save_m2m()
#     #
#     #         # ذخیره تصاویر
#     #         images = self.request.FILES.getlist('images')
#     #         print(f"تعداد تصاویر دریافتی: {len(images)}")  # برای دیباگ
#     #
#     #         for image in images :
#     #             print(f"ذخیره تصویر: {image.name}")  # برای دیباگ
#     #             ArticleImage.objects.create(
#     #                 article = article,
#     #                 image = image
#     #             )
#     #
#     #         messages.success(self.request, "مقاله با موفقیت ذخیره شد.")
#     #         return super().form_valid(form)
#     #     except Exception as e :
#     #         print(f"خطا: {str(e)}")  # برای دیباگ
#     #         messages.error(self.request, f"خطا در ذخیره مقاله: {str(e)}")
#     #         return self.form_invalid(form)
#     # def form_invalid(self, form):
#     #     messages.error(self.request, "لطفاً خطاهای فرم را برطرف کنید.")
#     #     for field, errors in form.errors.items():
#     #         for error in errors:
#     #             messages.error(self.request, f"{field}: {error}")
#     #     return super().form_invalid(form)
@login_required
@require_POST
def delete_article_image(request, image_id):
    try:
        image = ArticleImage.objects.get(id=image_id)
        # اطمینان از دسترسی کاربر
        if request.user.is_superuser or image.article.author == request.user:
            image.delete()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    except ArticleImage.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Image not found'}, status=404)
class ArticleUpdate(LoginRequiredMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "account/article-create-update.html"
    success_url = reverse_lazy('account:home')

    def form_valid(self, form):
        response = super().form_valid(form)
        files = self.request.FILES.getlist('file')
        for f in files:
            ArticleFile.objects.create(article=self.object, file=f)
        return response


class ArticleDelete(LoginRequiredMixin, DeleteView):
    model = Article
    template_name = "account/article_confirm_delete.html"
    success_url = reverse_lazy('account:home')


# --- وکیل ---
class AddVakil(LoginRequiredMixin, CreateView):
    model = Vakil
    fields = '__all__'
    template_name = "account/vakil-create-update.html"
    success_url = reverse_lazy('account:home')


class VakilUpdateView(LoginRequiredMixin, UpdateView):
    model = Vakil
    template_name = 'account/vakil-create-update.html'
    fields = '__all__'
    success_url = reverse_lazy('account:vakil_list')


class VakilDeleteView(LoginRequiredMixin, DeleteView):
    model = Vakil
    template_name = 'account/vakil_confirm_delete.html'
    success_url = reverse_lazy('account:vakil_list')


class vakileList(LoginRequiredMixin, ListView):
    model = Vakil
    template_name = "account/vakil_list.html"
    context_object_name = "vakils"
    paginate_by = 10

    def get_queryset(self):
        search_query = self.request.GET.get('search', '')
        if search_query:
            return Vakil.objects.filter(
                Q(name__icontains=search_query) |
                Q(lastname__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(address__icontains=search_query)
            )
        return Vakil.objects.all()


class vakil_image_view(LoginRequiredMixin, View):
    form_class = ImageForm
    template_name = 'account/vakil_image_update.html'

    def get_object(self):
        return get_object_or_404(Vakil, pk=self.kwargs['id'])

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.get_object())
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        vakil = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=vakil)
        if form.is_valid():
            form.save()
            return redirect('account:vakil_list')
        return render(request, self.template_name, {'form': form})


# --- کمیسیون ---
class ComisionList(LoginRequiredMixin, View):
    def get(self, request):
        comisions = Comision.objects.all().order_by('-chairman')
        return render(request, 'inc/navbar.html', {'comisions': comisions})


class ComisionDetail(LoginRequiredMixin, View):
    def get(self, request, id):
        comision = get_object_or_404(Comision.objects.prefetch_related('vakils'), id=id)
        return render(request, 'account/comisiondetail.html', {'comisions': comision})


@login_required
def add_comision(request):
    if request.method == 'POST':
        form = ComisionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home:home')
    else:
        form = ComisionForm()
    return render(request, 'account/comision-create-update.html', {'form': form})


class AddComision(LoginRequiredMixin, CreateView):
    model = Comision
    form_class = ComisionForm
    template_name = "account/comision-create-update.html"
    success_url = reverse_lazy('account:home')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['vakils'].widget.attrs.update({'class': 'vakil-raw-id'})
        form.fields['raees'].widget.attrs.update({'class': 'raees-raw-id'})
        return form


class ComisionView(LoginRequiredMixin, View):
    def get(self, request):
        comi = Comision.objects.all()
        return render(request, 'account/comision.html', {'comi': comi})


@login_required
def comision_edit(request, pk):
    commission = get_object_or_404(Comision, id=pk)
    if request.method == "POST":
        form = ComisionForm(request.POST, instance=commission)
        if form.is_valid():
            form.save()
            return redirect('account:comision')
    else:
        form = ComisionForm(instance=commission)
    return render(request, 'account/comision-create-update.html', {'form': form})


@login_required
def comision_delete(request, pk):
    commission = get_object_or_404(Comision, id=pk)
    if request.method == "POST":
        commission.delete()
        return redirect('account:comision')
    return render(request, 'account/comision_confirm_delete.html', {'commission': commission})


# --- ریاست ---
class Riyasatlist(LoginRequiredMixin, ListView):
    template_name = "account/riyasat_list.html"
    model = Riyasat


@login_required
def add_riyasat(request):
    if request.method == 'POST':
        form = RaeesForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'عضو هیئت مدیره با موفقیت اضافه شد!')
            return redirect('account:home')
    else:
        form = RaeesForm()
    vakils = Vakil.objects.all()
    return render(request, 'account/add_riyasat.html', {'form': form, 'vakils': vakils})


class RiyasatDeleteView(LoginRequiredMixin, DeleteView):
    model = Riyasat
    success_url = reverse_lazy('account:riyasat_list')
    template_name = 'account/riyasat_confirm_delete.html'
