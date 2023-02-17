from django.contrib.auth.models import User
from django.db import models


class ArquivoEntrada(models.Model):
    file_data = models.FileField(blank=True, default='')


class Setor(models.Model):
    sigla = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.sigla

    @staticmethod
    def format_dependencia(dependencia):
        sigla = dependencia.split(' ')[0]
        nome = dependencia.split(' - ')[1]
        return (sigla, nome)


class Conta(models.Model):
    numero = models.CharField(max_length=10, unique=True)
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome

    @staticmethod
    def format_conta(conta):
        numero = conta.split(' ')[0]
        nome = conta.split(' - ')[1]
        return (numero, nome)


class Material(models.Model):

    setor = models.ForeignKey(Setor, on_delete=models.DO_NOTHING)
    conta = models.ForeignKey(Conta, on_delete=models.DO_NOTHING)
    n_bmp = models.IntegerField(unique=True)
    nomenclatura = models.CharField(max_length=1000)
    n_serie = models.CharField(max_length=100)
    vl_atualizado = models.FloatField()
    vl_liquido = models.FloatField()
    situacao = models.CharField(max_length=5)
    is_pending = models.BooleanField(default=False)

    def __str__(self):

        return f'{self.n_bmp} - {self.nomenclatura}'


class Usuario(models.Model):
    nome = models.CharField(max_length=100)
    saram = models.CharField(max_length=7)
    setor = models.ForeignKey(Setor, on_delete=models.DO_NOTHING)


class Cautela(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    materials = models.ManyToManyField(
        Material, related_name="cautelas", related_query_name="cautela")
    observacao = models.CharField(max_length=100, null=True, default=None)
    data_emissao = models.DateField()
    data_devolucao = models.DateField(null=True, blank=True)

    def is_pending(self):
        return self.data_devolucao is None
