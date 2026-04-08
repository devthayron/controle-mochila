from django.urls import path
from .views import (
    ViagemListView,
    ViagemCreateView,
    ViagemDetailView,
    FinalizarViagemView,
    ItensFaltantesView,
)

urlpatterns = [
    path("", ViagemListView.as_view(), name="viagem_list"),
    path("nova/", ViagemCreateView.as_view(), name="viagem_create"),
    path("<int:pk>/", ViagemDetailView.as_view(), name="viagem_detail"),

    path("<int:pk>/finalizar/", FinalizarViagemView.as_view(), name="finalizar_viagem"),

    path("faltantes/", ItensFaltantesView.as_view(), name="faltantes"),
]