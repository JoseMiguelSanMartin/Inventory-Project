from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import InventoryItem

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ["item_name", "quantity_required", "quantity_have"]
