from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import apis

urlpatterns = [
    # ========================== VISTAS ================
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', views.consultas, name='menu'),
    path('users/', views.users, name='users'),
    path('consultas/', views.consultas, name='consultas'),
    

    # ========================== APIS ================
    path('alumno/api/v0/<int:id>/',apis.UsuarioApi.as_view(), name='UserApi'),
    path('historia-clinica/', apis.HistoriaClinicaView.as_view()),
    path('historia-clinica/<str:prontuario>/', apis.HistoriaClinicaView.as_view()),
    path('historia-clinica/<int:historia_id>/signos-vitales/', apis.SignosVitalesView.as_view()),
    path('historia-clinica/<int:historia_id>/datos-corporales/', apis.DatosCorporalesView.as_view()),
    path('historia-clinica/<int:historia_id>/problemas-cronicos/', apis.ProblemaCronicoView.as_view()),
    path('historia-clinica/<int:historia_id>/problemas-transitorios/', apis.ProblemaTransitorioView.as_view()),
    path('historia-clinica/<int:historia_id>/notas-soap/', apis.NotaSOAPView.as_view()),
]