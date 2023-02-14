from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets

from logistica.bmp import serializers
from logistica.bmp.models import (ArquivoEntrada, Cautela, Conta, Material,
                                  Setor)
from logistica.bmp.serializers import GroupSerializer, UserSerializer


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

    def perform_create(self, serializer):
        return super().perform_create(serializer)


class CautelaViewSet(viewsets.ModelViewSet):
    """
    API endpoint para Cautela
    """

    queryset = Cautela.objects.all()
    serializer_class = serializers.CautelaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()
        return super().perform_create(serializer)


class ArquivoEntradaViewSet(viewsets.ModelViewSet):
    queryset = ArquivoEntrada.objects.all()
    serializer_class = serializers.ArquivoEntradaSerializer

    def pre_save(self, obj):
        obj.file_data = self.request.FILES.get('file')

    def perform_create(self, serializer):
        serializer.save()
        file_name = serializer.validated_data['file_data'].name  # type: ignore
        ArquivoEntrada.update_database(file_name)
