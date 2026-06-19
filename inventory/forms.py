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
        fields = ["item_name", "category", "quantity_required", "quantity_have", "notes"]

        widgets = {
            "item_name": forms.Select(attrs={
            "class": "w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white focus:border-blue-500 focus:outline-none",
            }),
            "category": forms.TextInput(attrs={
                "class": "w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none",
                "placeholder": "Example: Tools",
            }),
            "quantity_required": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white focus:border-blue-500 focus:outline-none",
            }),
            "quantity_have": forms.NumberInput(attrs={
                "class": "w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white focus:border-blue-500 focus:outline-none",
            }),
            "notes": forms.Textarea(attrs={
                "class": "w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white placeholder-slate-500 focus:border-blue-500 focus:outline-none",
                "rows": 4,
                "placeholder": "Optional notes...",
            }),
        }

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["item_name"].error_messages["required"] = (
            "Item name is required."
        )

        for field in ["quantity_required", "quantity_have"]:
            self.fields[field].error_messages["min_value"] = (
                "Quantity cannot be negative."
            )
