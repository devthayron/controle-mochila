import json

from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.urls import reverse_lazy

from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView

from django.db.models import Q
from django.db import transaction
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

from .models import Loja, Item, Mochila, Viagem, MochilaItem
from .forms import ViagemForm, MochilaForm


# ───────────────── DASHBOARD ─────────────────
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        context.update({
            "total_andamento": Viagem.objects.filter(status="andamento").count(),
            "total_finalizadas": Viagem.objects.filter(
                status="finalizada",
                data_retorno__gte=inicio_mes
            ).count(),
            "total_mochilas": Mochila.objects.count(),
            "total_lojas": Loja.objects.count(),
            "viagens_andamento": Viagem.objects.filter(status="andamento")
                .select_related("responsavel", "loja", "mochila")
                .order_by("-data_saida")[:10],
            "ultimas_viagens": Viagem.objects.select_related(
                "responsavel", "loja", "mochila"
            ).order_by("-id")[:8],
            "mochilas": Mochila.objects.prefetch_related("mochilaitem_set__item").all(),
        })

        return context


# ───────────────── LOGIN / LOGOUT ─────────────────
class CustomLoginView(LoginView):
    template_name = "core/login.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields['username'].widget.attrs.update({
            'placeholder': 'Usuário',
            'class': 'login-input'
        })

        form.fields['password'].widget.attrs.update({
            'placeholder': 'Senha',
            'class': 'login-input'
        })

        return form


class CustomLogoutView(LogoutView):
    next_page = "login"


# ───────────────── VIAGENS ─────────────────
class ViagemListView(LoginRequiredMixin, ListView):
    model = Viagem
    template_name = "core/viagem_list.html"
    context_object_name = "viagens"

    def get_queryset(self):
        qs = Viagem.objects.select_related(
            "responsavel", "loja", "mochila"
        ).order_by("-id")

        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status")
        loja = self.request.GET.get("loja")

        if q:
            qs = qs.filter(
                Q(responsavel__username__icontains=q) |
                Q(loja__nome__icontains=q)
            )

        if status:
            qs = qs.filter(status=status)

        if loja:
            qs = qs.filter(loja_id=loja)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lojas"] = Loja.objects.all()
        return context


class ViagemDetailView(LoginRequiredMixin, DetailView):
    model = Viagem
    template_name = "core/viagem_detail.html"
    context_object_name = "viagem"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["checklist_items"] = self.object.checklist.select_related("item")
        return context


class ViagemCreateView(LoginRequiredMixin, CreateView):
    model = Viagem
    form_class = ViagemForm
    template_name = "core/viagem_form.html"

    def get_success_url(self):
        return reverse_lazy("viagem_detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Viagem criada com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        mochilas_dict = {}
        for m in Mochila.objects.prefetch_related("mochilaitem_set__item").all():
            mochilas_dict[str(m.pk)] = [
                {"item": mi.item.nome, "quantidade": mi.quantidade}
                for mi in m.mochilaitem_set.all()
            ]

        context["mochilas_json"] = json.dumps(mochilas_dict)
        return context


# ─────────────── AÇÕES CUSTOM ───────────────
@method_decorator(require_POST, name='dispatch')
class FinalizarViagemView(LoginRequiredMixin, View):
    def post(self, request, pk):
        viagem = get_object_or_404(Viagem, pk=pk, status="andamento")
        viagem.status = "finalizada"
        viagem.data_retorno = timezone.now()
        viagem.save()

        messages.success(request, "Viagem finalizada!")
        return redirect("viagem_detail", pk=pk)


class ChecklistSaveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        viagem = get_object_or_404(Viagem, pk=pk, status="andamento")

        for ci in viagem.checklist.all():
            ci.saida_ok = f"saida_ok_{ci.id}" in request.POST
            ci.retorno_ok = f"retorno_ok_{ci.id}" in request.POST
            ci.observacao_retorno = request.POST.get(f"obs_{ci.id}", "")
            ci.save()

        messages.success(request, "Checklist salvo!")
        return redirect("viagem_detail", pk=pk)


# ───────────────── MOCHILAS ─────────────────
class MochilaListView(LoginRequiredMixin, ListView):
    model = Mochila
    template_name = "core/mochila_list.html"
    context_object_name = "mochilas"

    def get_queryset(self):
        return Mochila.objects.prefetch_related("mochilaitem_set__item")


class MochilaCreateView(LoginRequiredMixin, CreateView):
    model = Mochila
    form_class = MochilaForm
    template_name = "core/mochila_form.html"
    success_url = reverse_lazy("mochila_list")

    def form_valid(self, form):
        with transaction.atomic():
            response = super().form_valid(form)

            itens = form.cleaned_data["itens"]

            MochilaItem.objects.bulk_create([
                MochilaItem(
                    mochila=self.object,
                    item=item,
                    quantidade=1
                ) for item in itens
            ])

        return response


class MochilaDetailView(LoginRequiredMixin, DetailView):
    model = Mochila
    template_name = "core/mochila_detail.html"
    context_object_name = "mochila"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["viagens"] = Viagem.objects.filter(
            mochila=self.object
        ).select_related("loja", "responsavel").order_by("-id")
        return context


# ───────────────── ITENS ─────────────────
class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = "core/item_list.html"
    context_object_name = "itens"


# ───────────────── LOJAS ─────────────────
class LojaListView(LoginRequiredMixin, ListView):
    model = Loja
    template_name = "core/loja_list.html"
    context_object_name = "lojas"