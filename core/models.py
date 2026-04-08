from django.db import models
from django.contrib.auth.models import User

class Loja(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Item(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Mochila(models.Model):
    nome = models.CharField(max_length=100,default='Mochila')
    itens = models.ManyToManyField(Item, through="MochilaItem", related_name="mochilas")

    def __str__(self):
        return self.nome


class MochilaItem(models.Model):
    mochila = models.ForeignKey("Mochila", on_delete=models.CASCADE)
    item = models.ForeignKey("Item", on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.item} x{self.quantidade}"
        

class Viagem(models.Model):

    STATUS_CHOICES = [
        ("andamento", "Em andamento"),
        ("finalizada", "Finalizada"),
    ]

    responsavel = models.ForeignKey(User, on_delete=models.CASCADE)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE)
    mochila = models.ForeignKey(Mochila, on_delete=models.CASCADE)

    data_saida = models.DateTimeField(auto_now_add=True)
    data_retorno = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="andamento"
    )

    def __str__(self):
        return f"Viagem {self.id} - {self.loja}"


class ChecklistItem(models.Model):
    viagem = models.ForeignKey(Viagem, on_delete=models.CASCADE, related_name="checklist")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    saida_ok = models.BooleanField(default=True)
    retorno_ok = models.BooleanField(default=True)

    observacao_retorno = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.item} - Viagem {self.viagem.id}"