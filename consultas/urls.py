from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import apis

urlpatterns = [
    # ========================== VISTAS ================
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.menu_view, name='menu'),
    path('users/', views.users, name='users'),
    path('consultas/', views.consultas, name='consultas'),
    path('consultas/<int:id>/', views.consultas, name='consultasPaciente'),
    

    # ========================== APIS ================
    path('alumno/api/v0/<int:id>/',apis.UsuarioApi.as_view(), name='UserApi'),
    path('api/historias_clinicas/', apis.HistoriaClinicaApi.as_view(), name='historia-clinica-list'),
    path('api/historias_clinicas/<int:id>/', apis.HistoriaClinicaApi.as_view(), name='historia-clinica-detail'),
    path('signos_vitales/', apis.SignosVitalesApi.as_view(), name='signos_vitales_list'),
    path('signos_vitales/<int:id>/', apis.SignosVitalesApi.as_view(), name='signos_vitales_detail'),
    path('problemas_cronicos/', apis.ProblemaCronicoApi.as_view(), name='problema_cronico_list'),
    path('problemas_cronicos/<int:id>/', apis.ProblemaCronicoApi.as_view(), name='problema_cronico_detail'),
    path('problemas_transitorios/', apis.ProblemaTransitorioApi.as_view(), name='problema_transitorio_list'),
    path('problemas_transitorios/<int:id>/', apis.ProblemaTransitorioApi.as_view(), name='problema_transitorio_detail'),
    path('notas_soap/', apis.NotaSOAPApi.as_view(), name='nota_soap_list'),
    path('notas_soap/<int:id>/', apis.NotaSOAPApi.as_view(), name='nota_soap_detail'),
]