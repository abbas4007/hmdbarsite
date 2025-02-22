from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from home.models import Article, Vakil, Riyasat, ArticleImage, ArticleFile,Comision
from .forms import ImageForm, ComisionForm, RaeesForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from .forms import ContactForm
from django.conf import settings
import requests
from django.http import JsonResponse
from captcha.models import CaptchaStore
from .models import ContactMessage
from utils import send_sms

# Create your views here.


@csrf_exempt
def contact_view(request) :
    if request.method == 'POST' :
        print("داده‌های فرم:", request.POST)
        form = ContactForm(request.POST)
        if form.is_valid() :
            message = form.save()
            print("پیام ذخیره شد با آیدی:", message.id)

            try :
                print("شروع ارسال پیامک...")
                response = requests.post(
                    "https://api.ghasedak.me/v2/sms/send/simple",
                    data = {
                        "message" : f"پیام شما با شماره پیگیری {message.id} دریافت شد",
                        "receptor" : message.phone,
                        "linenumber" : settings.SMS_LINE_NUMBER
                    },
                    headers = {
                        "apikey" : settings.GHASEDAK_API_KEY,
                        "Content-Type" : "application/x-www-form-urlencoded"
                    },
                    timeout = 10
                )
                print("وضعیت پاسخ:", response.status_code)
                print("محتوی پاسخ:", response.text)

                if response.status_code == 200 :
                    print("پیامک با موفقیت ارسال شد")
                else :
                    print("خطا در ارسال پیامک:", response.json())

            except requests.exceptions.RequestException as e :
                print("خطا در ارتباط با سرویس پیامکی:", str(e))

            return redirect('account:success_page')
        else :
            print("خطاهای فرم:", form.errors)
    else :
        form = ContactForm()

    return render(request, 'account/contact.html', {'form' : form})

def success_page(request) :
    return render(request, 'account/success.html')


# بخش مدیریتی
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin


class MessageListView(LoginRequiredMixin, ListView) :
    model = ContactMessage
    template_name = 'account/message_list.html'
    context_object_name = 'messages'
    ordering = ['-created_at']
    paginate_by = 10


class MessageUpdateView(LoginRequiredMixin, UpdateView) :
    model = ContactMessage
    fields = ['status', 'response']
    template_name = 'account/message_form.html'
    success_url = '/admin/messages/'

    def form_valid(self, form) :
        response = super().form_valid(form)
        if form.cleaned_data.get('response') :
            try :
                api_key = settings.GHASEDAK_API_KEY
                url = "https://api.ghasedak.me/v2/sms/send/simple"
                payload = {
                    "message" : f"پاسخ به پیام شما:\n{form.cleaned_data['response']}",
                    "receptor" : self.object.phone,
                    "linenumber" : settings.SMS_LINE_NUMBER
                }
                headers = {"apikey" : api_key}
                requests.post(url, data = payload, headers = headers)
            except Exception as e :
                print(f"خطا در ارسال پاسخ: {str(e)}")
        return response
def success_page(request) :
    return render(request, 'account/success.html')


# بخش مدیریتی
from django.views.generic import ListView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin


class MessageListView(LoginRequiredMixin, ListView) :
    model = ContactMessage
    template_name = 'account/message_list.html'
    context_object_name = 'messages'
    ordering = ['-created_at']
    paginate_by = 10


class MessageUpdateView(LoginRequiredMixin, UpdateView) :
    model = ContactMessage
    fields = ['status', 'response']
    template_name = 'account/message_form.html'
    success_url = reverse_lazy('account:home')

    def form_valid(self, form) :
        response = super().form_valid(form)
        if form.cleaned_data.get('response') :
            try :
                api_key = settings.GHASEDAK_API_KEY
                url = "https://api.ghasedak.me/v2/sms/send/simple"

                payload = {
                    "message" : f"پاسخ به پیام شما:\n{form.cleaned_data['response']}",
                    "receptor" : self.object.phone,
                    "linenumber" : settings.SMS_LINE_NUMBER
                }

                headers = {
                    "apikey" : 'vuyDb4/n8/XM44gZHDzGzHMyF8CKqnSGgftvGqUWZUo',
                    "Content-Type" : "application/x-www-form-urlencoded"
                }

                # ارسال درخواست و دریافت پاسخ
                api_response = requests.post(url, data = payload, headers = headers)

                # تبدیل پاسخ به دیکشنری
                response_data = api_response.json()

                # بررسی وضعیت پاسخ
                if api_response.status_code != 200 :
                    print(f"خطا در ارسال: {response_data}")
                else :
                    print("پیامک با موفقیت ارسال شد!")

            except Exception as e :
                print(f"خطا در ارسال پاسخ: {str(e)}")

        return response

class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('account:home')

class ArticleList(LoginRequiredMixin, ListView) :  # اضافه کردن LoginRequiredMixin
    model = Article
    paginate_by = 6
    template_name = "account/home.html"


class ComisionList(LoginRequiredMixin, View) :  # اضافه کردن LoginRequiredMixin
    def get(self, request) :
        comisions = Comision.objects.all().order_by('-chairman')
        return render(request, 'inc/navbar.html', {'comisions' : comisions})


class ComisionDetail(LoginRequiredMixin, View) :  # اضافه کردن LoginRequiredMixin
    def get(self, request, id) :
        comisions = get_object_or_404(Comision.objects.prefetch_related('vakils'), id = id)
        return render(request, 'account/comisiondetail.html', {'comisions' : comisions})


@login_required  # اضافه کردن دکوراتور
def add_comision(request) :
    if request.method == 'POST' :
        form = ComisionForm(request.POST)
        if form.is_valid() :
            comision = form.save()
            return redirect('home:home')
    else :
        form = ComisionForm()
    return render(request, 'account/comision-create-update.html', {'form' : form})


class ArticleCreate(CreateView) :
    model = Article
    fields = ['author', 'title', 'slug', 'category', 'description', 'thumbnail', 'publish', 'is_special', 'status','file','video']

    template_name = "account/article-create-update.html"

    success_url = reverse_lazy('account:home')


class ArticleUpdate(LoginRequiredMixin, UpdateView) :  # اضافه کردن LoginRequiredMixin
    model = Article
    template_name = "account/article-create-update.html"
    fields = '__all__'


class ArticleDelete(LoginRequiredMixin, DeleteView) :  # اضافه کردن LoginRequiredMixin
    model = Article
    success_url = reverse_lazy('account:home')
    template_name = "account/article_confirm_delete.html"


class AddVakil(LoginRequiredMixin, CreateView):
    model = Vakil
    fields = ['name', 'lastname', 'gender', 'code', 'thumbnail', 'address', 'date', 'city']
    template_name = "account/vakil-create-update.html"
    success_url = reverse_lazy('account:home')

class vakileList(LoginRequiredMixin, ListView) :
    template_name = "account/vakil_list.html"
    model = Vakil
    context_object_name = "vakils"
    paginate_by = 10

    def get_queryset(self) :
        # دریافت عبارت جستجو از پارامتر GET
        search_query = self.request.GET.get('search', '')

        # اگر عبارت جستجو وجود داشت، فیلتر اعمال می‌شود
        if search_query :
            # جستجو در فیلدهای name، lastname، city و address
            return Vakil.objects.filter(
                Q(name__icontains = search_query) |
                Q(lastname__icontains = search_query) |
                Q(city__icontains = search_query) |
                Q(address__icontains = search_query)
            )

        # اگر جستجو وجود نداشت، همه وکلا برگردانده می‌شوند
        return Vakil.objects.all()
class Riyasatlist(LoginRequiredMixin, ListView) :  # اضافه کردن LoginRequiredMixin
    template_name = "account/riyasat_list.html"

    def get_queryset(self) :
        return Riyasat.objects.all()


def add_riyasat(request) :
    if request.method == 'POST' :
        form = RaeesForm(request.POST)
        if form.is_valid() :
            form.save()
            messages.success(request, 'عضو هیئت مدیره با موفقیت اضافه شد!')

            return redirect('account:home')
    else :
        form = RaeesForm()  # فرم خالی ایجاد می‌شود

    # انتقال تمام وکیل‌ها به تمپلیت برای نمایش در جستجو (اختیاری)
    vakils = Vakil.objects.all()
    return render(request, 'account/add_riyasat.html', {'form' : form, 'vakils' : vakils})

class RiyasatDeleteView(LoginRequiredMixin, DeleteView):
    model = Riyasat
    success_url = reverse_lazy('account:riyasat_list')
    template_name = 'account/riyasat_confirm_delete.html'

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

class AddComision(LoginRequiredMixin, CreateView) :  # اضافه کردن LoginRequiredMixin
    model = Comision
    form_class = ComisionForm
    template_name = "account/comision-create-update.html"
    success_url = reverse_lazy('account:home')

    def get_form(self, form_class=None) :
        form = super().get_form(form_class)
        form.fields['vakils'].widget.attrs.update({'class' : 'vakil-raw-id'})
        form.fields['raees'].widget.attrs.update({'class' : 'raees-raw-id'})
        return form


class ComisionView(View):
    def get(self,request):
        comi = Comision.objects.all()
        return render(request,'account/comision.html',{'comi':comi})

class VakilUpdateView(UpdateView):
    model = Vakil
    template_name = 'account/vakil-create-update.html'
    fields = '__all__'
    success_url = reverse_lazy('account:vakil_list')

class VakilDeleteView(DeleteView):
    model = Vakil
    template_name = 'account/vakil_confirm_delete.html'
    success_url = reverse_lazy('account:vakil_list')

def comision_edit(request, pk):
    commission = get_object_or_404(Comision, id=pk)
    if request.method == "POST":
        form = ComisionForm(request.POST, instance=commission)
        if form.is_valid():
            form.save()
            return redirect('account:comision')  # بعد از ویرایش به لیست کمیسیون‌ها برگردید
    else:
        form = ComisionForm(instance=commission)
    return render(request, 'account/comision-create-update.html', {'form': form})

def comision_delete(request, pk):
    commission = get_object_or_404(Comision, id=pk)
    if request.method == "POST":
        commission.delete()
        return redirect('account:comision')  # بعد از حذف به لیست کمیسیون‌ها برگردید
    return render(request, 'account/comision_confirm_delete.html', {'commission': commission})