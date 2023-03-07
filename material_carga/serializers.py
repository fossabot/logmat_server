from django.contrib.auth.models import Group, User
from rest_framework import serializers

from material_carga import models


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class PerfilSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Perfil
        fields = ['user', 'matricula', 'setor']
    user = UserSerializer(many=False)


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
        ]


class EmprestimoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Emprestimo
        fields = [
            "cautela", "material", "data_devolucao"
        ]


class CautelaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Cautela
        fields = [
            "perfil", "observacao",
            "data_emissao", "data_baixa", "emprestimos"
        ]
    emprestimos = EmprestimoSerializer(many=True)


class ArquivoEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ArquivoEntrada
        fields = ('file_data', )
