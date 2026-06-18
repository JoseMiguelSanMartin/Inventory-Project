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

        labels = {
            "item_name": "Item Name",
            "quantity_required": "Quantity Needed",
            "quantity_have": "Quantity Available",
        }

        widgets = {
            "item_name": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none",
                "placeholder": "Example: Paint Roller"
            }),
            "quantity_required": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none",
                "placeholder": "Example: 3"
            }),
            "quantity_have": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none",
                "placeholder": "Example: 1"
            }),
        }

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in ["quantity_required", "quantity_have"]:
            self.fields[field].error_messages["min_value"] = (
                "Quantity cannot be negative"
            )
