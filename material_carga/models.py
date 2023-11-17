from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver
from django.utils import timezone

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

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


class User(AbstractUser):
    matricula = models.CharField(max_length=7)
    setor = models.ForeignKey(Setor, on_delete=models.DO_NOTHING, null=True)

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_auth_token(sender, instance=None, created=False, **kwargs):
        if created:
            Token.objects.create(user=instance)

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

    def is_from_usuario_setor(self, usuario):
        return self.setor == usuario.setor


class Cautela(models.Model):
    class Meta:
        permissions = [
            ("gerenciar", "Can create, update, delete cautela")
        ]
    observacao = models.CharField(max_length=100, null=True, default=None)
    data_emissao = models.DateField(auto_now_add=True, blank=True)
    data_baixa = models.DateField(null=True)
    # Um usuário deve registrar o recebimento da cautela
    cautelado = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    data_recebimento = models.DateField(null=True)

    def set_data_recebimento(self, date=timezone.now().date()):
        self.data_recebimento = date


class Emprestimo(models.Model):
    cautela = models.ForeignKey(
        Cautela, on_delete=models.DO_NOTHING, related_name='emprestimos')
    material = models.ForeignKey(
        Material, default=None, on_delete=models.DO_NOTHING)
    data_devolucao = models.DateField(null=True, blank=True)


class Conferencia(models.Model):
    
    class Estado(models.IntegerChoices):
        EM_USO = 1
        INUTILIZADO_DANIFICADO = 2
        OCIOSO = 3

    material = models.ForeignKey(
        Material, on_delete=models.DO_NOTHING)
    conferente = models.ForeignKey(
        User, on_delete=models.DO_NOTHING)
    is_owner = models.BooleanField(default=False)
    localizacao = models.ForeignKey(
        Setor, on_delete=models.DO_NOTHING)
    observacao = models.CharField(max_length=100, default='')
    estado = models.IntegerField(choices=Estado.choices)

    created = models.DateField(auto_now=True)


class Processo(models.Model):

    class Tipo(models.IntegerChoices):
        
        CONFERENCIA_INTERNA = 1
        CONFERENCIA_ANUAL = 2
        INVENTARIO = 3

    titulo = models.CharField(max_length=50)
    nup = models.CharField(max_length=50)
    tipo = models.IntegerField(choices=Tipo.choices)
    data_inicio = models.DateField()
    data_fim = models.DateField()
    is_open = models.BooleanField(default=True)
    conferencias = models.ManyToManyField(Conferencia)
