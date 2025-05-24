from django import forms
from jalali_date.widgets import AdminJalaliDateWidget

from .models import Vakil, Article, Comment
from ckeditor.widgets import CKEditorWidget
from django_jalali.forms import jDateField


class ImageForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Vakil
        fields = ('thumbnail',)


class VakilSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'نام یا نام خانوادگی وکیل...',
            'class': 'form-control'
        })
    )

class ArticleSearchForm(forms.Form):
    title = forms.CharField(label="",widget = forms.TextInput( attrs = {'class' : 'form-control mt-2 p-1'}))

    # class Meta:
    #     model = Article
    #     fields  = ('title', )

class AdminContactForm(forms.Form):
    name = forms.CharField(label = "",widget=forms.TextInput(attrs={ 'class' : "form-control",'style' : 'max-width: 300px;','placeholder' : 'نام'}))
    lastname = forms.CharField(label = "",widget=forms.TextInput(attrs={ 'class' : "form-control",'style' : 'max-width: 300px;','placeholder' : 'نام خانوادگی'}))
    mobile = forms.CharField(label = "",widget=forms.TextInput(attrs={ 'class' : "form-control",'style' : 'max-width: 300px;','placeholder' : 'تلفن همراه'}))
    message = forms.CharField(label = "",widget=forms.Textarea(attrs={ 'class' : "form-control",'style' : 'max-width: 300px;','placeholder' : 'متن پیام'}))

    def save(self) :
        data = self.cleaned_data
        comment = Comment(name = data['name'], lastname = data['lastname'],
                 mobile = data['mobile'],
                    message = data['message'])
        comment.save()


class VakilForm(forms.ModelForm) :
    date = jDateField(
        label = "تاریخ انقضا",
        widget = AdminJalaliDateWidget(attrs = {'class' : 'form-control'}),
    )

    class Meta :
        model = Vakil
        fields = '__all__'