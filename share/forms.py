from django import forms
from django.core.validators import MinValueValidator,MaxValueValidator

from .models import Document,Review

class DocumentForm(forms.ModelForm):

    class Meta:
        model   = Document
        #mimeを追加する。userも追加する。
        fields = ["name", "content", "mime", "user"]

class ReviewForm(forms.ModelForm):

    class Meta:
        model   = Review
        fields = ["document", "user", "comment","star"]

#モデルを継承しないフォームクラス
class YearMonthForm(forms.Form):
    year    = forms.IntegerField()
    month   = forms.IntegerField(validators=[MinValueValidator(1),MaxValueValidator(12)])

