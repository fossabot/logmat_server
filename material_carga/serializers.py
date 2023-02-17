from django.contrib.auth.models import Group, User
from rest_framework import serializers

from material_carga import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class SetorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Setor
        fields = [
            "sigla", "nome"
        ]


class ContaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Conta
        fields = [
            "numero", "nome"
        ]


class MaterialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Material
        fields = [
            "setor",
            "conta",
            "n_bmp",
            "nomenclatura",
            "n_serie",
            "vl_atualizado",
            "vl_liquido",
            "situacao",
            "has_cautela_pendente"
        ]


class CautelaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Cautela
        fields = [
            "usuario", "materials", "observacao",
            "data_emissao", "data_devolucao"
        ]


class ArquivoEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ArquivoEntrada
        fields = ('file_data', )
