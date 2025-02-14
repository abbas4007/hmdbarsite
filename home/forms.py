from django import forms
from .models import Vakil, Article, Comment
from ckeditor.widgets import CKEditorWidget


class ImageForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Vakil
        fields = ('thumbnail',)


class VakilSearchForm(forms.ModelForm):
    class Meta:
        model = Vakil
        fields  = ('name',)

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


