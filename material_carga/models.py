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


class Perfil(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.DO_NOTHING, related_name='perfil')
    matricula = models.CharField(max_length=7)
    setor = models.ForeignKey(Setor, on_delete=models.DO_NOTHING)


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
    situacao = models.CharField(max_length=50, default=None)
    imagem = models.FileField(blank=True, default='')

    def __str__(self):

        return f'{self.n_bmp} - {self.nomenclatura}'


class Cautela(models.Model):
    Perfil = models.ForeignKey(Perfil, on_delete=models.DO_NOTHING)
    observacao = models.CharField(max_length=100, null=True, default=None)
    data_emissao = models.DateField(auto_now_add=True, blank=True)
    data_baixa = models.DateField(null=True)


class Emprestimo(models.Model):
    cautela = models.ForeignKey(Cautela, on_delete=models.DO_NOTHING)
    material = models.ForeignKey(
        Material, default=None, on_delete=models.DO_NOTHING)
    data_devolucao = models.DateField(null=True, blank=True)


# class Processo(models.Model):
#     titulo = models.CharField(max_length=50)
#     nup = models.CharField(max_length=50)


# class Processo_Conferencia(Processo):
#     # tipo = (ordinaria / extraordinaria)
#     # comissao = (somente para ORDINARIA)
#     # data_inicio
#     # data_fim
#     pass


# class Conferencia(models.Model):
#     processo = models.ForeignKey(
#         Processo_Conferencia, on_delete=models.DO_NOTHING)
#     material = models.ForeignKey(
#         Material, on_delete=models.DO_NOTHING)
#     Perfil = models.ForeignKey(
#         Perfil, on_delete=models.DO_NOTHING
#     )
#     parecer = models.CharField(max_length=100)
#     imagem = models.FileField(blank=True, default='')
