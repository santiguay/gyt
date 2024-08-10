from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import PerfilUsuario,HistoriaClinica, ProblemaTransitorio, ProblemaCronico, SignosVitales, NotaSOAP
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from datetime import date
from django.templatetags.static import static
import os
from django.conf import settings
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
    
def generar_pdf_historia_clinica(request, historia_id):
    historia = HistoriaClinica.objects.get(id=historia_id)
    signos_vitales = SignosVitales.objects.filter(historia_clinica=historia).order_by('-fecha').first()
    problemas_cronicos = ProblemaCronico.objects.filter(historia_clinica=historia)
    problemas_transitorios = ProblemaTransitorio.objects.filter(historia_clinica=historia)
    notas_soap = NotaSOAP.objects.filter(historia_clinica=historia).order_by('-fecha')[:5]  # Últimas 5 notas
    
    
    context = {
        'historia': historia,
        'signos_vitales': signos_vitales,
        'problemas_cronicos': problemas_cronicos,
        'problemas_transitorios': problemas_transitorios,
        'notas_soap': notas_soap,
        
        
    }
    
    template = get_template('pdf_historia_clinica.html')
    html = template.render(context)
    
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return HttpResponse('Error al generar el PDF', status=400)    
    