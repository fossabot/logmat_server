from django import urls
from django.urls import include, path
from django.conf import settings
from rest_framework import routers
from material_carga import views
from rest_framework.authtoken.views import obtain_auth_token


router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
router.register(r"arquivo", views.ArquivoEntradaViewSet)
router.register(r"material", views.MaterialViewSet, "material")
router.register(r"setor", views.SetorViewSet)
router.register(r"conta", views.ContaViewSet)
router.register(r"cautela", views.CautelaViewSet, "cautela")
router.register(r"recebe-cautela", views.CautelaRecebimentoViewSet, "recebe-cautela")
router.register(r"emprestimo", views.EmprestimoViewSet)
router.register(r"processo", views.ProcessoViewSet)
router.register(r"conferencia", views.ConferenciaViewSet, basename="conferencia")
router.register(r"conferidos", views.ConferidosViewSet, "conferidos")
router.register(r"nao-encontrados", views.MateriaisNaoEncontrados, "nao-encontrados")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("login/", views.CustomAuthToken.as_view()),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
