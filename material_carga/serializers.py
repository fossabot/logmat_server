from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import JsonResponse
from rest_framework import serializers

from material_carga import models
from material_carga.services import cautela_service


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "password", "email", "matricula", "setor"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class UsuarioResumidoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username"]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class SetorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Setor
        fields = ["id", "sigla", "nome"]


class SetorResumidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Setor
        fields = ["id", "sigla"]


class ContaSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Conta
        fields = ["numero", "nome"]


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        fields = [
            "id",
            "setor",
            "conta",
            "n_bmp",
            "nomenclatura",
            "n_serie",
            "vl_atualizado",
            "vl_liquido",
        ]

    setor = SetorSerializer()


class MaterialResumidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        fields = [
            "id",
            "n_bmp",
            "nomenclatura",
            "n_serie",
        ]


class EmprestimoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Emprestimo
        fields = ["id", "material", "data_devolucao"]
        extra_kwargs = {"cautela": {"read_only": True}}


class CautelaSerializer(serializers.HyperlinkedModelSerializer):
    # deprecated
    # cautelado = serializers.CurrentUserDefault()

    class Meta:
        model = models.Cautela
        fields = [
            "id",
            "observacao",
            "data_emissao",
            "data_baixa",
            "data_recebimento",
            "emprestimos",
        ]

    emprestimos = EmprestimoSerializer(many=True)

    def create(self, validated_data):
        emprestimos = validated_data.pop("emprestimos")
        cautela = super().create(validated_data)

        usuario_autenticado = serializers.CurrentUserDefault()
        for emprestimo_dict in emprestimos:
            emprestimo = models.Emprestimo(**emprestimo_dict)
            if emprestimo.material.is_from_usuario_setor(usuario_autenticado):
                emprestimo.cautela = cautela
                emprestimo.save()
                cautela.emprestimos.add(emprestimo)
        cautela.save()
        return cautela

    def update(self, instance, validated_data):
        instance.data_baixa = validated_data.get("data_baixa", instance.data_baixa)

        if instance.data_baixa:
            cautela_service.close_all_emprestimos(instance)
        else:
            cautela_service.close_requested_emprestimos(instance, validated_data)
        instance.save()

        return instance


class CautelaRecebimentoSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Cautela
        fields = ["id", "cautelado", "data_recebimento", "emprestimos"]

    emprestimos = EmprestimoSerializer(many=True)

    def update(self, instance, validated_data):
        instance.set_data_recebimento()
        instance.save()
        return instance


class ArquivoEntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ArquivoEntrada
        fields = ("file_data",)


class ConferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Conferencia
        fields = ["id", "localizacao", "material", "conferente", "observacao", "estado", "is_owner"]

    material = MaterialResumidoSerializer()
    localizacao = SetorResumidoSerializer()
    conferente = UsuarioResumidoSerializer()


class ConferenciaDeMaterial(serializers.ModelSerializer):
    conferente = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_owner = serializers.HiddenField(default=False)

    class Meta:
        model = models.Conferencia
        fields = [
            "material",
            "observacao",
            "estado",
            "conferente",
            "localizacao",
            "is_owner",
        ]

    def create(self, validated_data):
        conferente = self.context["request"].user
        is_owner = validated_data["material"].setor == conferente.setor
        validated_data["conferente"] = conferente
        validated_data["is_owner"] = is_owner
        conferencia = models.Conferencia(**validated_data)
        conferencia.save()
        return conferencia


class RelatorioConferencia(serializers.ModelSerializer):
    class Meta:
        model = models.Conferencia
        fields = ["localizacao", "material", "conferente", "observacao", "estado"]


class PanelSerializer(serializers.Serializer):
    material_qty = serializers.IntegerField()
    percentage_checked = serializers.IntegerField()


class ProcessoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Processo
        fields = [
            "nup",
            "tipo",
            "data_inicio",
            "data_fim",
        ]
