# forms.py
from django import forms
from home.models import Vakil, ArticleFile, Comision, Article, Riyasat
from tinymce.widgets import TinyMCE
from django import forms
from .models import ContactMessage
from captcha.fields import CaptchaField

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
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


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'description': TinyMCE(),
        }

# class ComisionForm(forms.ModelForm):
#     class Meta:
#         model = Comision
#         fields = '__all__'
#         widgets = {
#             'vakils': forms.SelectMultiple(attrs={'class': 'raw-id-field'}),
#             'raees': forms.Select(attrs={'class': 'raw-id-field'}),
#         }
#
#     def clean(self):
#         cleaned_data = super().clean()
#         raees = cleaned_data.get('raees')
#         vakils = cleaned_data.get('vakils')
#
#         if raees and raees not in vakils:
#             raise forms.ValidationError("رئیس باید از بین اعضای کمیسیون انتخاب شود!")
#
#         return cleaned_data


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