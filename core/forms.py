from django import forms
from .models import Mochila, Item, Viagem

class MochilaForm(forms.ModelForm):
    itens = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all().order_by("nome"),
        widget=forms.SelectMultiple(attrs={
            "class": "multi-select"
        })
    )

    class Meta:
        model = Mochila
        fields = ["nome", "itens"]



class ViagemForm(forms.ModelForm):
    class Meta:
        model = Viagem
        fields = ["responsavel", "loja", "mochila"]