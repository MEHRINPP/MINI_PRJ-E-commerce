from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from core.models import *
from django_countries.widgets import CountrySelectWidget

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name'] 
        
class ProductCountForm(forms.Form):
    product_count = forms.IntegerField(min_value=0)
    
class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'subtitle', 'image'] 

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_status']

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'category':forms.Select(attrs={'class':'form-control'}),
            'desc':forms.Textarea(attrs={'class':'form-control'}),
            'price':forms.NumberInput(attrs={'class':'form-control'}),
            'product_available_count':forms.NumberInput(attrs={'class':'form-control'}),
            'img':forms.FileInput(attrs={'class':'form-control'}),
        }

class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'1234 Main st'
    }))
    apartment_address = forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'Apartment or suit'
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100'
    }))
        
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']

    rating = forms.IntegerField(min_value=1, max_value=5, widget=forms.NumberInput(attrs={'type': 'range', 'min': '1', 'max': '5'}))


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'desc', 'price', 'discount_price', 'product_available_count', 'img']

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('custom_admin_dashboard')  # Redirect to dashboard after saving
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'core/edit_product.html', {'form': form})