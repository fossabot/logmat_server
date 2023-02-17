from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
import pandas as pd
from material_carga import serializers
from material_carga.models import (ArquivoEntrada, Cautela, Conta, Material,
                                   Setor)
from material_carga.serializers import ArquivoEntradaSerializer, GroupSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class MaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Material
    """
    queryset = Material.objects.all()
    serializer_class = serializers.MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]


class SetorViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Setor
    """
    queryset = Setor.objects.all()
    serializer_class = serializers.SetorSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Conta
    """
    queryset = Conta.objects.all()
    serializer_class = serializers.ContaSerializer
    permission_classes = [permissions.IsAuthenticated]


class CautelaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Cautela
    """

    queryset = Cautela.objects.all()
    serializer_class = serializers.CautelaSerializer
    permission_classes = [permissions.IsAuthenticated]


class ArquivoEntradaViewSet(viewsets.ModelViewSet):
    queryset = ArquivoEntrada.objects.all()
    serializer_class = serializers.ArquivoEntradaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        file_name = request.data['file_data'].name  # type: ignore
        self.update_database(file_name)
        return super().create(request, *args, **kwargs)
  
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
