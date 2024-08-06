from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario,HistoriaClinica
# Create your views here.
def menu_view(request):
    return redirect('./consultas')
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('menu')  # Cambia 'dashboard' por la URL a la que deseas redirigir después del inicio de sesión exitoso
        else:
            # Manejo de error: usuario o contraseña incorrectos
            return render(request, 'login.html', {'error_message': 'Usuario o contraseña incorrectos'})
    else:
        return render(request, 'login.html')
    
@login_required
def users(request):

    user_profiles = PerfilUsuario.objects.all()
    user_data = []
    for profile in user_profiles:
        user_data.append({
            'id' : profile.id,
            'name': profile.usuario.get_full_name(),
            'username': profile.usuario.username,
            'user_type': profile.tipo_usuario,
            'password' : profile.contrasenha,
        })


    return render(request, 'usuarios.html', {'user_data': user_data})
 
@login_required
def consultas(request, id=None):
    if id is None:
        historias = HistoriaClinica.objects.all()
        return render(request, 'consultas.html', {'historias': historias})
    else:
        historia = get_object_or_404(HistoriaClinica, id=id)
        return render(request, 'pacientes.html', {'historia': historia})
    
    