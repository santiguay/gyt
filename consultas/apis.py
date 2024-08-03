from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import HistoriaClinica, SignosVitales, DatosCorporales, ProblemaCronico, ProblemaTransitorio, NotaSOAP, PerfilUsuario
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import json
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Consulta, PerfilUsuario


logger = logging.getLogger(__name__)

class UsuarioApi(View):
    
    def get(self, request, id=None):
        user_profiles = PerfilUsuario.objects.all()
        user_data = []
        for profile in user_profiles:
            user_data.append({
                'name': profile.usuario.get_full_name(),
                'username': profile.usuario.username,
                'user_type': profile.tipo_usuario,
            })


        return {'user_data': user_data}
    
    def post(self, request, id=None):
        nombre = request.POST.get('nombre')
        username = request.POST.get('username')
        password = request.POST.get('password')
        tipo_usuario = request.POST.get('tipo')

        if nombre and username and password and tipo_usuario:
            user = User.objects.create_user(username=username, password=password, first_name=nombre)
            PerfilUsuario.objects.create(usuario=user, tipo_usuario=tipo_usuario, contrasenha = password)
            return JsonResponse({'message': 'Usuario creado exitosamente.'})
        else:
            return JsonResponse({'error': 'Faltan datos obligatorios en la solicitud.'}, status=400)
    
    def put(self, request, id):
        try:
            profile = PerfilUsuario.objects.get(id=id)
            print(f"Request body: {request.body}")
            
            data = json.loads(request.body)
            print(f"Parsed data: {data}")
            
            nombre = data.get('nombre')
            username = data.get('username')
            password = data.get('password')
            tipo_usuario = data.get('tipo')
            
            print(f"Extracted data - nombre: {nombre}, username: {username}, tipo_usuario: {tipo_usuario}")
            
            if nombre:
                profile.usuario.first_name = nombre
            if username:
                profile.usuario.username = username
            if tipo_usuario:
                profile.tipo_usuario = tipo_usuario
            if password:
                profile.contrasenha = password
                profile.usuario.password = make_password(password)
            
            print(f"Before save - username: {profile.usuario.username}, tipo_usuario: {profile.tipo_usuario}")
            
            try:
                profile.usuario.save(update_fields=['first_name', 'username', 'password'])
                profile.save(update_fields=['tipo_usuario', 'contrasenha'])
                print("User and profile saved successfully")
            except Exception as e:
                logger.error(f"Error saving user or profile: {str(e)}")
                return JsonResponse({'error': 'Error al guardar los cambios.'}, status=500)
            
            print(f"After save - username: {profile.usuario.username}, tipo_usuario: {profile.tipo_usuario}")
            
            return JsonResponse({'message': 'Perfil de usuario actualizado exitosamente.'}, status=200)
        except PerfilUsuario.DoesNotExist:
            logger.error(f"PerfilUsuario with id {id} not found")
            return JsonResponse({'error': 'Perfil de usuario no encontrado.'}, status=404)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': 'Error inesperado al procesar la solicitud.'}, status=500)
        
    def delete(self, request, id):
        try:
            profile = PerfilUsuario.objects.get(id=id)
            id_user = profile.usuario.id
            user = User.objects.get(id=id_user)
            user.delete()
            return JsonResponse({'message': 'Perfil de usuario actualizado exitosamente.'}, status=200)
        except PerfilUsuario.DoesNotExist:
            return JsonResponse({'error': 'Perfil de usuario no encontrado.'}, status=404)  

class ConsultaApi(View):
    def get(self, request):
        consultas = Consulta.objects.all()
        consulta_data = []
        for consulta in consultas:
            consulta_data.append({
                'id': consulta.id,
                'paciente': consulta.paciente.usuario.get_full_name(),
                'medico': consulta.medico.usuario.get_full_name(),
                'fecha': consulta.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                'motivo': consulta.motivo,
                'diagnostico': consulta.diagnostico,
                'tratamiento': consulta.tratamiento,
            })
        return JsonResponse({'consultas': consulta_data})

    def post(self, request):
        data = json.loads(request.body)
        paciente_id = data.get('paciente_id')
        medico_id = data.get('medico_id')
        motivo = data.get('motivo')
        diagnostico = data.get('diagnostico')
        tratamiento = data.get('tratamiento')

        if paciente_id and medico_id and motivo and diagnostico and tratamiento:
            paciente = PerfilUsuario.objects.get(id=paciente_id)
            medico = PerfilUsuario.objects.get(id=medico_id)
            consulta = Consulta.objects.create(
                paciente=paciente,
                medico=medico,
                motivo=motivo,
                diagnostico=diagnostico,
                tratamiento=tratamiento
            )
            return JsonResponse({'message': 'Consulta creada exitosamente.', 'id': consulta.id})
        else:
            return JsonResponse({'error': 'Faltan datos obligatorios en la solicitud.'}, status=400)

    def put(self, request, id):
        try:
            consulta = Consulta.objects.get(id=id)
            data = json.loads(request.body)
            
            if 'motivo' in data:
                consulta.motivo = data['motivo']
            if 'diagnostico' in data:
                consulta.diagnostico = data['diagnostico']
            if 'tratamiento' in data:
                consulta.tratamiento = data['tratamiento']
            
            consulta.save()
            return JsonResponse({'message': 'Consulta actualizada exitosamente.'})
        except Consulta.DoesNotExist:
            return JsonResponse({'error': 'Consulta no encontrada.'}, status=404)