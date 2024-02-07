from django.contrib.auth.models import Group
from rest_framework import permissions, viewsets, views, exceptions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from material_carga.serializers import *
from material_carga.models import (
    ArquivoEntrada, Cautela, Conferencia, Conta, Emprestimo, Material,
    Processo, Setor, User)
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
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {'username': user.username, 'id': user.pk},
            'setor': {'nome': user.setor.nome, 'sigla': user.setor.sigla}
        })
    
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
    filterset_fields = ['n_bmp', 'setor__sigla']
    
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
        authenticated_user = serializer.context['request'].user
        if authenticated_user.has_perm('gerenciar'):
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
        file_data = request.data['file_data'].file  # type: ignore
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


class ConferenciasPorMaterialViewSet(viewsets.ModelViewSet):
    queryset = Conferencia.objects.all()
    serializer_class = ConferenciaSerializer

    def list(self, request, *args, **kwargs):
        material_id = request.data.material
        # processo_id = request.data.processo

        conferencias = self.get_queryset()\
            .filter(material__n_bmp=material_id)
        # .filter(processo__id=processo_id)

        serializer = self.get_serializer(conferencias, many=True)
        return Response(serializer.data)


class ConferidosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConferenciaSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conferencia.objects.prefetch_related('material')

    def list(self, request, *args, **kwargs):
        setor = request.query_params['setor']
        conferencias = self.get_queryset()\
            .filter(material__setor__sigla=setor)\
            .filter(is_owner=True)\
            .order_by('material__n_bmp')\
            .distinct('material__n_bmp')

        page = self.paginate_queryset(conferencias)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(conferencias, many=True)
        return Response(serializer.data)


class EncontradosViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ConferenciaSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conferencia.objects.prefetch_related('material')

    def list(self, request, *args, **kwargs):
        setor = request.query_params['setor']
        conf_completas = self.get_queryset()\
            .filter(material__setor__sigla=setor)\
            .filter(is_owner=True)

        materiais_conferidos = [conf.material for conf in conf_completas]

        encontrados_por_outros = self.get_queryset()\
            .filter(material__setor__sigla=setor)\
            .filter(is_owner=False)\
            .order_by('material__n_bmp')\
            .distinct('material__n_bmp')\
            .exclude(material__in=materiais_conferidos)
    
        page = self.paginate_queryset(encontrados_por_outros)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(encontrados_por_outros, many=True)
        return Response(serializer.data)


class MateriaisNaoEncontrados(viewsets.ReadOnlyModelViewSet):
    serializer_class = MaterialResumidoSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conferencia.objects.prefetch_related('material')

    def list(self, request, *args, **kwargs):
        setor = request.query_params['setor']
        conferencias = self.get_queryset()\
            .filter(material__setor__sigla=setor)

        nao_conferidos = Material.objects\
            .exclude(id__in=conferencias.values('material__id'))\
            .order_by('n_bmp')

        page = self.paginate_queryset(nao_conferidos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(nao_conferidos, many=True)
        return Response(serializer.data)
