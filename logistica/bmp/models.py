from django.contrib.auth.models import User
from django.db import models

import pandas as pd


class ArquivoEntrada(models.Model):
    file_data = models.FileField(blank=True, default='')

    @classmethod
    def update_database(cls, csv_file):
        file = pd.read_csv(
            filepath_or_buffer=csv_file,
            sep=';',
            encoding='iso-8859-1')

        for i in range(0, len(file)):
            dependencia = file['DEPENDENCIA'][i]
            if not isinstance(dependencia, str):
                continue

            conta_raw = file['CONTA'][i]
            if not isinstance(conta_raw, str):
                continue

            try:
                sigla, nome = Setor.format_dependencia(dependencia)
                setor = Setor.objects.get_or_create(sigla=sigla, nome=nome)[0]

                conta_numero, conta_nome = Conta.format_conta(conta_raw)
                conta = Conta.objects.get_or_create(
                    numero=conta_numero, nome=conta_nome)[0]
                material = Material(
                    setor=setor,
                    conta=conta,
                    n_bmp=int(file['Nº BMP'][i]),
                    nomenclatura=file['NOMECLATURA/COMPONENTE'][i],
                    n_serie=file['Nº SERIE'][i],
                    vl_atualizado=float(
                        0 if not isinstance(file['VL. ATUALIZ.'][i], str)
                        else file['VL. ATUALIZ.'][i].replace(',', '.')
                    ),
                    vl_liquido=float(
                        0 if not isinstance(file['VL. LIQUIDO'][i], str)
                        else file['VL. LIQUIDO'][i].replace(',', '.')
                    ),
                    situacao=file['SITUACAO'][i]
                )
                material.save()
            except IndexError:
                print(f'Row {i} with invalid data.')
            except Exception as exc:
                print(f'line: {i}')
                print(exc)


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
