import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .core.models import Loja, Item, Mochila, Viagem, ChecklistItem, MochilaItem


# ─── DASHBOARD ──────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    from django.utils import timezone
    from datetime import timedelta
    now = timezone.now()
    inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    context = {
        "total_andamento":   Viagem.objects.filter(status="andamento").count(),
        "total_finalizadas": Viagem.objects.filter(status="finalizada", data_retorno__gte=inicio_mes).count(),
        "total_mochilas":    Mochila.objects.count(),
        "total_lojas":       Loja.objects.count(),
        "viagens_andamento": Viagem.objects.filter(status="andamento").select_related("responsavel", "loja", "mochila").order_by("-data_saida")[:10],
        "ultimas_viagens":   Viagem.objects.select_related("responsavel", "loja", "mochila").order_by("-id")[:8],
        "mochilas":          Mochila.objects.prefetch_related("mochilaitem_set__item").all(),
    }
    return render(request, "core/dashboard.html", context)


# ─── VIAGENS ─────────────────────────────────────────────────────────────────
@login_required
def viagem_list(request):
    qs = Viagem.objects.select_related("responsavel", "loja", "mochila").order_by("-id")

    q      = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    loja   = request.GET.get("loja", "")

    if q:
        qs = qs.filter(responsavel__username__icontains=q) | \
             qs.filter(loja__nome__icontains=q)
        qs = qs.distinct()
    if status:
        qs = qs.filter(status=status)
    if loja:
        qs = qs.filter(loja_id=loja)

    context = {
        "viagens": qs,
        "lojas":   Loja.objects.all(),
    }
    return render(request, "core/viagem_list.html", context)


@login_required
def viagem_detail(request, pk):
    viagem = get_object_or_404(Viagem, pk=pk)
    checklist_items = viagem.checklist.select_related("item").all()
    return render(request, "core/viagem_detail.html", {
        "viagem": viagem,
        "checklist_items": checklist_items,
    })


@login_required
def viagem_create(request):
    from django import forms as dj_forms
    from django.contrib.auth.models import User

    class ViagemForm(dj_forms.Form):
        responsavel = dj_forms.ModelChoiceField(
            queryset=User.objects.filter(is_active=True).order_by("username"),
            empty_label="Selecione o responsável",
        )
        loja = dj_forms.ModelChoiceField(
            queryset=Loja.objects.order_by("nome"),
            empty_label="Selecione a loja",
        )
        mochila = dj_forms.ModelChoiceField(
            queryset=Mochila.objects.order_by("nome"),
            empty_label="Selecione a mochila",
        )

    # JSON das mochilas para preview JS
    mochilas_dict = {}
    for m in Mochila.objects.prefetch_related("mochilaitem_set__item").all():
        mochilas_dict[str(m.pk)] = [
            {"item": mi.item.nome, "quantidade": mi.quantidade}
            for mi in m.mochilaitem_set.all()
        ]

    if request.method == "POST":
        form = ViagemForm(request.POST)
        if form.is_valid():
            viagem = Viagem.objects.create(
                responsavel=form.cleaned_data["responsavel"],
                loja=form.cleaned_data["loja"],
                mochila=form.cleaned_data["mochila"],
            )
            messages.success(request, f"Viagem #{viagem.id} registrada com sucesso!")
            return redirect("core:viagem_detail", pk=viagem.pk)
    else:
        form = ViagemForm()

    return render(request, "core/viagem_form.html", {
        "form": form,
        "mochilas_json": json.dumps(mochilas_dict),
    })


@login_required
def viagem_checklist_save(request, pk):
    viagem = get_object_or_404(Viagem, pk=pk, status="andamento")
    if request.method == "POST":
        for ci in viagem.checklist.all():
            ci.saida_ok    = f"saida_ok_{ci.id}" in request.POST
            ci.retorno_ok  = f"retorno_ok_{ci.id}" in request.POST
            ci.observacao_retorno = request.POST.get(f"obs_{ci.id}", "")
            ci.save()
        messages.success(request, "Checklist salvo com sucesso!")
    return redirect("core:viagem_detail", pk=pk)


@login_required
def viagem_finalizar(request, pk):
    viagem = get_object_or_404(Viagem, pk=pk, status="andamento")
    viagem.status = "finalizada"
    viagem.data_retorno = timezone.now()
    viagem.save()
    messages.success(request, f"Viagem #{viagem.id} finalizada!")
    return redirect("core:viagem_detail", pk=pk)


# ─── MOCHILAS ────────────────────────────────────────────────────────────────
@login_required
def mochila_list(request):
    mochilas = Mochila.objects.prefetch_related("mochilaitem_set__item").all()
    return render(request, "core/mochila_list.html", {"mochilas": mochilas})


@login_required
def mochila_detail(request, pk):
    mochila = get_object_or_404(Mochila, pk=pk)
    viagens = Viagem.objects.filter(mochila=mochila).select_related("loja", "responsavel").order_by("-id")
    return render(request, "core/mochila_detail.html", {
        "mochila": mochila,
        "viagens": viagens,
    })


# ─── ITENS ───────────────────────────────────────────────────────────────────
@login_required
def item_list(request):
    itens = Item.objects.prefetch_related("mochilas").order_by("nome")
    return render(request, "core/item_list.html", {"itens": itens})


# ─── LOJAS ───────────────────────────────────────────────────────────────────
@login_required
def loja_list(request):
    lojas = Loja.objects.prefetch_related("viagem_set").order_by("nome")
    return render(request, "core/loja_list.html", {"lojas": lojas})
