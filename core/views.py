from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, View
from django.shortcuts import get_object_or_404, redirect
from .models import Viagem, ChecklistItem



class ViagemListView(ListView):
    model = Viagem
    template_name = "mochila/viagem_list.html"


class ViagemCreateView(CreateView):
    model = Viagem
    fields = ["responsavel", "loja", "mochila"]
    template_name = "mochila/viagem_form.html"
    success_url = reverse_lazy("viagem_list")

class ViagemDetailView(DetailView):
    model = Viagem
    template_name = "mochila/viagem_detail.html"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.checklist.exists():
            itens = self.object.mochila.mochilaitem_set.all()

            checklist = [
                ChecklistItem(
                    viagem=self.object,
                    item=mi.item,
                    quantidade=mi.quantidade
                )
                for mi in itens
            ]

            ChecklistItem.objects.bulk_create(checklist)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if not self.object.checklist.exists():
            return redirect("viagem_detail", pk=self.object.pk)

        if self.object.status == "finalizada":
            return redirect("viagem_detail", pk=self.object.pk)

        checklist = list(self.object.checklist.all())

        for item in checklist:
            saida = request.POST.get(f"saida_{item.id}")
            retorno = request.POST.get(f"retorno_{item.id}")
            qtd = request.POST.get(f"qtd_{item.id}")

            if saida:
                item.status_saida = saida

            if retorno:

                if item.status_saida != "pendente":
                    item.status_retorno = retorno

            if qtd:
                try:
                    item.quantidade = int(qtd)
                except ValueError:
                    pass  

        ChecklistItem.objects.bulk_update(
            checklist,
            ["status_saida", "status_retorno", "quantidade"]
        )

        return redirect("viagem_detail", pk=self.object.pk)

class FinalizarViagemView(View):

    def post(self, request, pk):
        viagem = get_object_or_404(Viagem, pk=pk)

        checklist = viagem.checklist.all()

        for item in checklist:
            if item.status_saida == "pendente" or not item.status_retorno:
                return redirect("viagem_detail", pk=pk)

        viagem.status = "finalizada"
        viagem.save()

        return redirect("viagem_detail", pk=pk)


class ItensFaltantesView(ListView):
    model = ChecklistItem
    template_name = "mochila/faltantes.html"

    def get_queryset(self):
        return ChecklistItem.objects.filter(status_retorno="faltando")
    
    