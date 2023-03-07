from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from material_carga import serializers
from material_carga import models
from material_carga.services import csv_service, user_service


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class PerfilViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = models.Perfil.objects.all()
    serializer_class = serializers.PerfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        user_service.create_profile()


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class MaterialViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Material
    """
    queryset = models.Material.objects.all()
    serializer_class = serializers.MaterialSerializer
    permission_classes = [permissions.IsAuthenticated]


class SetorViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Setor
    """
    queryset = models.Setor.objects.all()
    serializer_class = serializers.SetorSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Conta
    """
    queryset = models.Conta.objects.all()
    serializer_class = serializers.ContaSerializer
    permission_classes = [permissions.IsAuthenticated]


class CautelaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Cautela
    """

    queryset = models.Cautela.objects.all()
    serializer_class = serializers.CautelaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, pk=None):
        cautela = models.Cautela()
        cautela.usuario = request.usuario
        cautela.observacao = request.observacao
        cautela.data_emissao = request.data_emisao

        cautela.emprestimo_set = request.emprestimo_set

        cautela.save()

    def update(self, request, pk=None):
        cautela = get_object_or_404(self.queryset, pk=pk)
        cautela.data_devolucao = request.data_devolucao
        cautela.is_pending = False


class EmprestimoViewSet(viewsets.ModelViewSet):
    queryset = models.Emprestimo.objects.all()
    serializer_class = serializers.EmprestimoSerializer
    permission_classes = [permissions.IsAuthenticated]


class ArquivoEntradaViewSet(viewsets.ModelViewSet):
    queryset = models.ArquivoEntrada.objects.all()
    serializer_class = serializers.ArquivoEntradaSerializer

    def create(self, request, *args, **kwargs):
        file_name = request.data['file_data'].name  # type: ignore
        csv_service.update_database(file_name)
        return super().create(request, *args, **kwargs)
