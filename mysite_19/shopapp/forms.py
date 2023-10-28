from django import forms
from django.contrib.auth.models import Group
from django.forms import Textarea

from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = 'name', 'description', 'price', 'quantity', 'has_additional_guarantee', \
            'archived', 'created_by', 'preview'
        widgets = {
            'description': Textarea(attrs={'cols': 40, 'rows': 5}),
        }

    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': False}), required=False
    )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = 'delivery_address', 'promocode', 'user', 'products'
        widgets = {
            'delivery_address': Textarea(attrs={'cols': 40, 'rows': 2}),
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = 'name',


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()

