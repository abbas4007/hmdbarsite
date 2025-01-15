# forms.py
from django import forms
from home.models import Vakil, ArticleFile


class ImageForm(forms.ModelForm):

    class Meta:
        model = Vakil
        fields = ['thumbnail']

    def save(self, commit=True) :
        vakil = super().save(commit = False)
        if commit :
            vakil.save()
        return vakil


class ArticleFileForm(forms.ModelForm):
    class Meta:
        model = ArticleFile
        fields = ['file']