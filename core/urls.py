from django.urls import path
from .views import *

urlpatterns = [
    # AUTH
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),

    # DASHBOARD
    path("", DashboardView.as_view(), name="dashboard"),

    # VIAGENS
    path("viagens/", ViagemListView.as_view(), name="viagem_list"),
    path("viagens/nova/", ViagemCreateView.as_view(), name="viagem_create"),
    path("viagens/<int:pk>/", ViagemDetailView.as_view(), name="viagem_detail"),
    path("viagens/<int:pk>/finalizar/", FinalizarViagemView.as_view(), name="viagem_finalizar"),
    path("viagens/<int:pk>/checklist/", ChecklistSaveView.as_view(), name="viagem_checklist_save"),

    # MOCHILAS
    path("mochilas/", MochilaListView.as_view(), name="mochila_list"),
    path("mochilas/<int:pk>/", MochilaDetailView.as_view(), name="mochila_detail"),
    path("mochilas/nova/", MochilaCreateView.as_view(), name="mochila_create"),

    # ITENS
    path("itens/", ItemListView.as_view(), name="item_list"),

    # LOJAS
    path("lojas/", LojaListView.as_view(), name="loja_list"),
]