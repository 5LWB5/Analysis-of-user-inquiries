from django import forms

from .models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('subject', 'description', 'category')
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Например, не проходит оплата'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Опишите проблему подробнее'}),
        }


class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('category', 'status')
