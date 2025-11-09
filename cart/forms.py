from django import forms
from .models import CartItem


class AddToCartForm(forms.Form):
    size_id = forms.IntegerField(required=False)
    quantity = forms.IntegerField(min_value=1, initial=1)


    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product


class UpdateCartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']