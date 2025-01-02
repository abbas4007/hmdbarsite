from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View

from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView
)
from home.models import Article,Vakil,Riyasat,Comision,ComisionVarzeshi

from .forms import ImageForm


# Create your views here.
class ArticleList(ListView):
    model = Article
    paginate_by = 6
    template_name = "account/home.html"

  
class ComisionList(View):


    def get(self,request):
        comisions = Comision.objects.all().order_by('-raees')
        return render(request,'account/comision.html',{'comisions':comisions})
        
class ComisionDetail(View):
    def get(self,request,id):
        comisions = Comision.objects.get(id=id)
        return render(request, 'account/comisiondetail.html', {'comisions': comisions})
class AddComision(CreateView):
    model = Comision
    fields = '__all__'
    template_name = "account/comision-create-update.html"
    success_url = reverse_lazy('account:home')

class AazaComision(CreateView):
    model = Comision
    fields = '__all__'
    template_name = "account/aaza_comision.html"
    success_url = reverse_lazy('account:home') 

class ArticleCreate(CreateView):
    model = Article
    fields =  '__all__'
    template_name = "account/article-create-update.html"
    success_url = reverse_lazy('account:home')



class ArticleUpdate(UpdateView):
    model = Article
    template_name = "account/article-create-update.html"
    fields =  '__all__'

class ArticleDelete(DeleteView):
    model = Article
    success_url = reverse_lazy('account:home')
    template_name = "account/article_confirm_delete.html"

class AddVakil(CreateView):
    model = Vakil
    fields =  '__all__'
    template_name = "account/vakil-create-update.html"
    success_url = reverse_lazy('account:home')


class vakileList(ListView):
    template_name = "account/vakil_list.html"

    def get_queryset(self):
        return Vakil.objects.all()

class Riyasatlist(ListView):
    template_name = "account/riyasat_list.html"

    def get_queryset(self):
        return Riyasat.objects.all()

class VakilUpdate(UpdateView):
    model = Vakil
    fields = '__all__'
    template_name = "account/vakil-create-update.html"
    success_url = reverse_lazy('account:home')

class vakil_image_view(View):
    form_class = ImageForm

    def setup(self, request, *args, **kwargs) :
        self.post_instance = get_object_or_404(Vakil, pk = kwargs['id'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs) :
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        vakil = self.post_instance
        form = self.form_class(instance = vakil )
        return render(request, 'account/vakil_image_update.html', {'form' : form})

    def post(self, request, *args, **kwargs):
        vakil = self.post_instance
        form = ImageForm(request.POST, request.FILES,instance = vakil)
        if form.is_valid() :
            form.save()
            return redirect('account:vakil_list')

