from rest_framework import permissions


class IsCautelado(permissions.BasePermission):
    """ 
    Verifica se o usuário que dará o recebimento da cautela é o usuário 
    que deve recebê-la e deter a posse dos materiais
    """

    def has_object_permission(self, request, view, obj):

        return obj.cautelado == request.user
