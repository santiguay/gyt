from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import HistoriaClinica, SignosVitales, DatosCorporales, ProblemaCronico, ProblemaTransitorio, NotaSOAP, PerfilUsuario
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import json
import logging

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


class HistoriaClinicaApi(View):
    def get(self, request, id=None):
        if id:
            try:
                historia = HistoriaClinica.objects.get(id=id)
                data = self.serialize_historia(historia)
                return JsonResponse(data)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Historia clínica no encontrada.'}, status=404)
        else:
            historias = HistoriaClinica.objects.all()
            data = [self.serialize_historia(historia) for historia in historias]
            return JsonResponse({'historias': data})

    def post(self, request):
        try:
            data = json.loads(request.body)
            historia = HistoriaClinica.objects.create(
                prontuario=data['prontuario'],
                jefe_familia=data['jefe_familia'],
                nombre_apellidos=data['nombre_apellidos'],
                fecha_nacido=data['fecha_nacido'],
                sexo=data['sexo'],
                documento=data['documento'],
                domicilio=data['domicilio'],
                telefono=data['telefono'],
                estado_civil=data['estado_civil']
            )
            return JsonResponse({'message': 'Historia clínica creada exitosamente.', 'id': historia.id})
        except KeyError as e:
            return JsonResponse({'error': f'Falta el campo obligatorio: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)

    def put(self, request, id):
        try:
            historia = HistoriaClinica.objects.get(id=id)
            data = json.loads(request.body)
            
            for field, value in data.items():
                setattr(historia, field, value)
            
            historia.save()
            return JsonResponse({'message': 'Historia clínica actualizada exitosamente.'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Historia clínica no encontrada.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)

    def delete(self, request, id):
        try:
            historia = HistoriaClinica.objects.get(id=id)
            historia.delete()
            return JsonResponse({'message': 'Historia clínica eliminada exitosamente.'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Historia clínica no encontrada.'}, status=404)

    def serialize_historia(self, historia):
        return {
            'id': historia.id,
            'prontuario': historia.prontuario,
            'jefe_familia': historia.jefe_familia,
            'nombre_apellidos': historia.nombre_apellidos,
            'fecha_nacido': historia.fecha_nacido.isoformat(),
            'sexo': historia.sexo,
            'documento': historia.documento,
            'domicilio': historia.domicilio,
            'telefono': historia.telefono,
            'estado_civil': historia.estado_civil
        }

class SignosVitalesApi(View):
    def get(self, request, historia_id):
        signos = SignosVitales.objects.filter(historia_clinica_id=historia_id).order_by('-fecha')
        data = [{
            'id': signo.id,
            'fecha': signo.fecha.isoformat(),
            'pulso': signo.pulso,
            'presion_arterial': signo.presion_arterial,
            'temperatura': signo.temperatura,
            'frecuencia_respiratoria': signo.frecuencia_respiratoria,
            'saturacion_oxigeno': signo.saturacion_oxigeno
        } for signo in signos]
        return JsonResponse({'signos_vitales': data})

    def post(self, request, historia_id):
        try:
            data = json.loads(request.body)
            signo = SignosVitales.objects.create(
                historia_clinica_id=historia_id,
                pulso=data['pulso'],
                presion_arterial=data['presion_arterial'],
                temperatura=data['temperatura'],
                frecuencia_respiratoria=data['frecuencia_respiratoria'],
                saturacion_oxigeno=data['saturacion_oxigeno']
            )
            return JsonResponse({'message': 'Signos vitales registrados exitosamente.', 'id': signo.id})
        except KeyError as e:
            return JsonResponse({'error': f'Falta el campo obligatorio: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)
class DatosCorporalesApi(View):
    def get(self, request, historia_id):
        datos = DatosCorporales.objects.filter(historia_clinica_id=historia_id).order_by('-fecha')
        data = [{
            'id': dato.id,
            'fecha': dato.fecha.isoformat(),
            'peso': dato.peso,
            'talla': dato.talla,
            'imc': dato.imc,
            'porcentaje_grasa_corporal': dato.porcentaje_grasa_corporal
        } for dato in datos]
        return JsonResponse({'datos_corporales': data})

    def post(self, request, historia_id):
        try:
            data = json.loads(request.body)
            dato = DatosCorporales.objects.create(
                historia_clinica_id=historia_id,
                peso=data['peso'],
                talla=data['talla'],
                imc=data['imc'],
                porcentaje_grasa_corporal=data['porcentaje_grasa_corporal']
            )
            return JsonResponse({'message': 'Datos corporales registrados exitosamente.', 'id': dato.id})
        except KeyError as e:
            return JsonResponse({'error': f'Falta el campo obligatorio: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)

class ProblemaCronicoApi(View):
    def get(self, request, historia_id):
        problemas = ProblemaCronico.objects.filter(historia_clinica_id=historia_id)
        data = [{
            'id': problema.id,
            'descripcion': problema.descripcion,
            'fecha_inicio': problema.fecha_inicio.isoformat(),
            'fecha_control': problema.fecha_control.isoformat()
        } for problema in problemas]
        return JsonResponse({'problemas_cronicos': data})

    def post(self, request, historia_id):
        try:
            data = json.loads(request.body)
            problema = ProblemaCronico.objects.create(
                historia_clinica_id=historia_id,
                descripcion=data['descripcion'],
                fecha_inicio=data['fecha_inicio'],
                fecha_control=data['fecha_control']
            )
            return JsonResponse({'message': 'Problema crónico registrado exitosamente.', 'id': problema.id})
        except KeyError as e:
            return JsonResponse({'error': f'Falta el campo obligatorio: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)

    def put(self, request, id):
        try:
            problema = ProblemaCronico.objects.get(id=id)
            data = json.loads(request.body)
            
            for field, value in data.items():
                setattr(problema, field, value)
            
            problema.save()
            return JsonResponse({'message': 'Problema crónico actualizado exitosamente.'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Problema crónico no encontrado.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)

    def delete(self, request, id):
        try:
            problema = ProblemaCronico.objects.get(id=id)
            problema.delete()
            return JsonResponse({'message': 'Problema crónico eliminado exitosamente.'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Problema crónico no encontrado.'}, status=404)

class ProblemaTransitorioApi(View):
    def get(self, request, historia_id):
        problemas = ProblemaTransitorio.objects.filter(historia_clinica_id=historia_id)
        data = [{
            'id': problema.id,
            'descripcion': problema.descripcion,
            'fechas': problema.fechas
        } for problema in problemas]
        return JsonResponse({'problemas_transitorios': data})

    def post(self, request, historia_id):
        try:
            data = json.loads(request.body)
            problema = ProblemaTransitorio.objects.create(
                historia_clinica_id=historia_id,
                descripcion=data['descripcion'],
                fechas=data['fechas']
            )
            return JsonResponse({'message': 'Problema transitorio registrado exitosamente.', 'id': problema.id})
        except KeyError as e:
            return JsonResponse({'error': f'Falta el campo obligatorio: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)

    def put(self, request, id):
        try:
            problema = ProblemaTransitorio.objects.get(id=id)
            data = json.loads(request.body)
            
            for field, value in data.items():
                setattr(problema, field, value)
            
            problema.save()
            return JsonResponse({'message': 'Problema transitorio actualizado exitosamente.'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Problema transitorio no encontrado.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)

    def delete(self, request, id):
        try:
            problema = ProblemaTransitorio.objects.get(id=id)
            problema.delete()
            return JsonResponse({'message': 'Problema transitorio eliminado exitosamente.'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Problema transitorio no encontrado.'}, status=404)

class NotaSOAPApi(View):
    def get(self, request, historia_id):
        notas = NotaSOAP.objects.filter(historia_clinica_id=historia_id).order_by('-fecha')
        data = [{
            'id': nota.id,
            'fecha': nota.fecha.isoformat(),
            'contenido': nota.contenido
        } for nota in notas]
        return JsonResponse({'notas_soap': data})

    def post(self, request, historia_id):
        try:
            data = json.loads(request.body)
            nota = NotaSOAP.objects.create(
                historia_clinica_id=historia_id,
                contenido=data['contenido']
            )
            return JsonResponse({'message': 'Nota SOAP registrada exitosamente.', 'id': nota.id})
        except KeyError as e:
            return JsonResponse({'error': f'Falta el campo obligatorio: {str(e)}'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)

    def put(self, request, id):
        try:
            nota = NotaSOAP.objects.get(id=id)
            data = json.loads(request.body)
            
            nota.contenido = data['contenido']
            nota.save()
            
            return JsonResponse({'message': 'Nota SOAP actualizada exitosamente.'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Nota SOAP no encontrada.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)

    def delete(self, request, id):
        try:
            nota = NotaSOAP.objects.get(id=id)
            nota.delete()
            return JsonResponse({'message': 'Nota SOAP eliminada exitosamente.'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Nota SOAP no encontrada.'}, status=404)