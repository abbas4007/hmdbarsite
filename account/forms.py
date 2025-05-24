# forms.py
from botocore.exceptions import ValidationError
from django import forms
from django.forms import modelformset_factory
from jalali_date.widgets import AdminJalaliDateWidget
from home.models import Vakil, ArticleFile, Comision, Article, Riyasat, ArticleImage
from tinymce.widgets import TinyMCE
from django import forms
from .models import ContactMessage
from captcha.fields import CaptchaField




class ContactForm(forms.ModelForm):
    captcha = CaptchaField(label = "کد امنیتی")

    class Meta :
        model = ContactMessage
        fields = ['full_name', 'phone', 'subject', 'message', 'captcha']
        widgets = {
            'message' : forms.Textarea(attrs = {'rows' : 5}),
        }

class ImageForm(forms.ModelForm):
    class Meta:
        model = Vakil
        fields = ['thumbnail']
        widgets = {
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'})
        }


    def save(self, commit=True) :
        vakil = super().save(commit = False)
        if commit :
            vakil.save()
        return vakil


class ArticleFileForm(forms.ModelForm):
    class Meta:
        model = ArticleFile
        fields = ['file']


class ArticleImageForm(forms.ModelForm) :

    class Meta :
        model = ArticleImage
        fields = ['image']


# class MultipleFileInput(forms.ClearableFileInput) :
#     allow_multiple_selected = True  # این خط مهم است


# class MultipleFileField(forms.FileField) :
#     def __init__(self, *args, **kwargs) :
#         kwargs.setdefault("widget", MultipleFileInput())
#         super().__init__(*args, **kwargs)
#
#     def clean(self, data, initial=None) :
#         if data is not None :
#             if not isinstance(data, (list, tuple)) :
#                 data = [data]
#         else :
#             data = []
#         return super().clean(data, initial)


class ArticleForm(forms.ModelForm) :
    class Meta :
        model = Article
        fields = '__all__'
        widgets = {
            'date' : AdminJalaliDateWidget(attrs = {'class' : 'form-control'}),
        }

ArticleImageFormSet = modelformset_factory(
    ArticleImage,
    form=ArticleImageForm,
    extra=3
)
class ComisionForm(forms.ModelForm):
    class Meta:
        model = Comision
        fields = ['name', 'vakils', 'chairman']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['chairman'].queryset = Vakil.objects.none()

        if 'vakils' in self.data:
            try:
                vakil_ids = self.data.getlist('vakils')
                self.fields['chairman'].queryset = Vakil.objects.filter(id__in=vakil_ids)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['chairman'].queryset = self.instance.vakils.all()


class RaeesForm(forms.ModelForm):
    class Meta:
        model = Riyasat
        fields = ['vakil', 'role']

    def __init__(self, *args, **kwargs) :
        super().__init__(*args, **kwargs)
        self.fields['vakil'].queryset = Vakil.objects.all()

class VakilForm(forms.ModelForm):
    class Meta:
        model = Vakil
        fields = '__all__'
        exclude = ['city_slug']