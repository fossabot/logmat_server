from django.urls import include, path
from rest_framework import routers

from material_carga import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'arquivo', views.ArquivoEntradaViewSet)
router.register(r'cautela', views.CautelaViewSet)
router.register(r'material', views.MaterialViewSet)
router.register(r'setor', views.SetorViewSet)
router.register(r'conta', views.ContaViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/',
         include('rest_framework.urls', namespace='rest_framework'))
]
