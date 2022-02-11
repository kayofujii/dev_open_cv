from django import forms

from .models import UploadedImage


class ImageForm(forms.Form):
    name = forms.CharField(max_length=255, label="タイトル", required=True)
    image = forms.ImageField(label="元画像", required=False)
    product_im = forms.ImageField(label="商品画像", required=False)
