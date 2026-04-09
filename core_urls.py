from django.urls import path
from .core import views


urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Viagens
    path("viagens/",                        views.viagem_list,           name="viagem_list"),
    path("viagens/nova/",                   views.viagem_create,         name="viagem_create"),
    path("viagens/<int:pk>/",               views.viagem_detail,         name="viagem_detail"),
    path("viagens/<int:pk>/checklist/",     views.viagem_checklist_save, name="viagem_checklist_save"),
    path("viagens/<int:pk>/finalizar/",     views.viagem_finalizar,      name="viagem_finalizar"),

    # Mochilas
    path("mochilas/",                       views.mochila_list,          name="mochila_list"),
    path("mochilas/<int:pk>/",              views.mochila_detail,        name="mochila_detail"),

    # Itens
    path("itens/",                          views.item_list,             name="item_list"),

    # Lojas
    path("lojas/",                          views.loja_list,             name="loja_list"),
]
