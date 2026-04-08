from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import Mochila, Item

class MochilaForm(forms.ModelForm):
    itens = forms.ModelMultipleChoiceField(
        queryset=Item.objects.all(),
        widget=FilteredSelectMultiple("Itens", is_stacked=False)
    )

    class Meta:
        model = Mochila
        fields = ['nome', 'itens']