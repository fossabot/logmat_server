from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets, views, exceptions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from material_carga.serializers import *
from material_carga.models import (
    ArquivoEntrada,
    Cautela,
    Conferencia,
    Conta,
    Emprestimo,
    Material,
    Processo,
    Setor,
    User,
)
from material_carga.services import csv_service


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user": {"username": user.username, "id": user.pk},
                "setor": {"nome": user.setor.nome, "sigla": user.setor.sigla},
            }
        )


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # permission_classes = [permissions.IsAuthenticated]


class MaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Material
    """

    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["n_bmp", "setor__sigla"]

    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]


class SetorViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Setor
    """

    queryset = Setor.objects.all()
    serializer_class = SetorSerializer
    # permission_classes = [permissions.IsAuthenticated]


class ContaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Conta
    """

    queryset = Conta.objects.all()
    serializer_class = ContaSerializer
    # permission_classes = [permissions.IsAuthenticated]


class CautelaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Cautela
    """

    queryset = Cautela.objects.all()
    serializer_class = CautelaSerializer
    # permission_classes = [
    #     permissions.IsAuthenticated & custom_permissions.IsCautelado]

    def perform_create(self, serializer):
        authenticated_user = serializer.context["request"].user
        if authenticated_user.has_perm("gerenciar"):
            serializer.save()
        else:
            raise exceptions.PermissionDenied


class CautelaRecebimentoViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Recebimento de Cautela
    """

    queryset = Cautela.objects.all()
    serializer_class = CautelaRecebimentoSerializer
    # permission_classes = [
    #     permissions.IsAuthenticated & custom_permissions.IsCautelado
    # ]


class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = Emprestimo.objects.all()
    serializer_class = EmprestimoSerializer
    # permission_classes = [permissions.IsAuthenticated]


class ArquivoEntradaViewSet(viewsets.ModelViewSet):
    queryset = ArquivoEntrada.objects.all()
    serializer_class = ArquivoEntradaSerializer

    def create(self, request, *args, **kwargs):
        file_data = request.data["file_data"].file  # type: ignore
        csv_service.update_database(file_data)
        return super().create(request, *args, **kwargs)


class ProcessoViewSet(viewsets.ModelViewSet):
    queryset = Processo.objects.all()
    serializer_class = ProcessoSerializer
    # permission_classes = [permissions.IsAuthenticated]


class ConferenciaViewSet(viewsets.ModelViewSet):
    queryset = Conferencia.objects.all()
    serializer_class = ConferenciaDeMaterial

    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]


class PanelViewSet(viewsets.ViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, pk=None):
        sector = pk
        material_qty = Material.objects.filter(setor__sigla=sector).count()

        checks_qty = (
            Conferencia.objects.prefetch_related("material")
            .filter(material__setor__sigla=sector)
            .order_by("material__n_bmp", "-is_owner")
            .distinct("material__n_bmp")
        ).count()
        percentage_checked = int((checks_qty/material_qty)*100)
        report = {
            "material_qty": material_qty,
            "percentage_checked": percentage_checked
        }
        serializer = PanelSerializer(report)
        return Response(serializer.data)


class ConferidosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConferenciaSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conferencia.objects.prefetch_related("material")

    def list(self, request, *args, **kwargs):
        setor = request.query_params["setor"]
        conferencias = (
            self.get_queryset()
            .filter(material__setor__sigla=setor)
            .order_by("material__n_bmp", "-is_owner")
            .distinct("material__n_bmp")
        )
        conferencias = sorted(conferencias, key=lambda conf: conf.is_owner)

        page = self.paginate_queryset(conferencias)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(conferencias, many=True)
        return Response(serializer.data)


class MateriaisNaoEncontrados(viewsets.ReadOnlyModelViewSet):
    serializer_class = MaterialResumidoSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conferencia.objects.prefetch_related("material")

    def list(self, request, *args, **kwargs):
        setor = request.query_params["setor_sigla"]
        conferencias = self.get_queryset().filter(material__setor__sigla=setor)

        nao_conferidos = (
            Material.objects
                .filter(setor__sigla=setor)
                .exclude(id__in=conferencias.values("material__id"))
                .order_by("n_bmp")
            )

        page = self.paginate_queryset(nao_conferidos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(nao_conferidos, many=True)
        return Response(serializer.data)
