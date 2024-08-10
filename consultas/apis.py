from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import HistoriaClinica, SignosVitales, ProblemaCronico, ProblemaTransitorio, NotaSOAP, PerfilUsuario
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
import json
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal, InvalidOperation

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
                historia_data = {
                    'nombre': historia.nombre,
                    'fecha_nacimiento': historia.fecha_nacimiento,
                    'sexo': historia.sexo,
                    'numero_identificacion': historia.numero_identificacion,
                    'direccion': historia.direccion,
                    'telefono': historia.telefono,
                    'fecha_registro': historia.fecha_registro,
                }
                return JsonResponse({'historia': historia_data}, status=200)
            except HistoriaClinica.DoesNotExist:
                logger.error(f"HistoriaClinica with id {id} not found")
                return JsonResponse({'error': 'Historia clínica no encontrada.'}, status=404)
        else:
            historias = HistoriaClinica.objects.all()
            historias_data = []
            for historia in historias:
                historias_data.append({
                    'id': historia.id,
                    'nombre': historia.nombre,
                    'fecha_nacimiento': historia.fecha_nacimiento,
                    'sexo': historia.sexo,
                    'numero_identificacion': historia.numero_identificacion,
                    'direccion': historia.direccion,
                    'telefono': historia.telefono,
                    'fecha_registro': historia.fecha_registro,
                })
            return JsonResponse({'historias': historias_data}, status=200)
    
    
    
    def post(self, request):
        # Extraer datos del formulario
        nombre = request.POST.get('nombre')
        fecha_nacimiento = request.POST.get('fecha_nacimiento')
        sexo = request.POST.get('sexo')
        numero_identificacion = request.POST.get('numero_identificacion')
        direccion = request.POST.get('direccion')
        telefono = request.POST.get('telefono')
        fecha_registro = request.POST.get('fecha_registro')

        # Validar que todos los campos necesarios estén presentes
        if all([nombre, fecha_nacimiento, sexo, numero_identificacion, direccion, telefono, fecha_registro]):
            try:
                # Crear una nueva entrada en HistoriaClinica
                historia = HistoriaClinica.objects.create(
                    nombre=nombre,
                    fecha_nacimiento=fecha_nacimiento,
                    sexo=sexo,
                    documento=numero_identificacion,
                    domicilio=direccion,
                    telefono=telefono,
                    fecha=fecha_registro
                )
                return JsonResponse({'message': 'Historia clínica creada exitosamente.', 'id': historia.id}, status=201)
            except Exception as e:
                logger.error(f"Error creating HistoriaClinica: {str(e)}")
                return JsonResponse({'error': 'Error inesperado al procesar la solicitud.'}, status=500)
        else:
            return JsonResponse({'error': 'Faltan datos obligatorios en la solicitud.'}, status=400)


    def put(self, request, id):
        try:
            historia = HistoriaClinica.objects.get(id=id)
            data = json.loads(request.body)
            
            nombre = data.get('nombre')
            fecha_nacimiento = data.get('fecha_nacimiento')
            sexo = data.get('sexo')
            numero_identificacion = data.get('numero_identificacion')
            direccion = data.get('direccion')
            telefono = data.get('telefono')
            fecha_registro = data.get('fecha_registro')

            if nombre:
                historia.nombre = nombre
            if fecha_nacimiento:
                historia.fecha_nacimiento = fecha_nacimiento
            if sexo:
                historia.sexo = sexo
            if numero_identificacion:
                historia.numero_identificacion = numero_identificacion
            if direccion:
                historia.direccion = direccion
            if telefono:
                historia.telefono = telefono
            if fecha_registro:
                historia.fecha_registro = fecha_registro

            historia.save()
            return JsonResponse({'message': 'Historia clínica actualizada exitosamente.'}, status=200)
        except HistoriaClinica.DoesNotExist:
            logger.error(f"HistoriaClinica with id {id} not found")
            return JsonResponse({'error': 'Historia clínica no encontrada.'}, status=404)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in request body")
            return JsonResponse({'error': 'JSON inválido en el cuerpo de la solicitud.'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': 'Error inesperado al procesar la solicitud.'}, status=500)

    def delete(self, request, id):
        try:
            historia = HistoriaClinica.objects.get(id=id)
            historia.delete()
            return JsonResponse({'message': 'Historia clínica eliminada exitosamente.'}, status=200)
        except HistoriaClinica.DoesNotExist:
            logger.error(f"HistoriaClinica with id {id} not found")
            return JsonResponse({'error': 'Historia clínica no encontrada.'}, status=404)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': 'Error inesperado al procesar la solicitud.'}, status=500)

        
@method_decorator(csrf_exempt, name='dispatch')
class SignosVitalesApi(View):
    def get(self, request, id=None):
        if id:
            try:
                historia = HistoriaClinica.objects.get(id=id)
                signos = SignosVitales.objects.filter(historia_clinica=historia)

                if signos.exists():
                    data = [{
                        'id': signo.id,
                        'historia_clinica': signo.historia_clinica.id,
                        'fecha': str(signo.fecha),
                        'pulso': signo.pulso,
                        'presion_arterial': signo.presion_arterial,
                        'temperatura': str(signo.temperatura),
                        'frecuencia_respiratoria': signo.frecuencia_respiratoria,
                        'saturacion_oxigeno': signo.saturacion_oxigeno,
                        'peso': str(signo.peso),
                        'talla': str(signo.talla),
                        'imc': str(signo.imc),
                        'perimetro_cefalico': str(signo.perimetro_cefalico),
                    } for signo in signos]
                else:    
                    return JsonResponse({'error': 'Signos Vitales no encontrados'}, status=404)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Signos Vitales no encontrados'}, status=404)
        else:
            signos_list = SignosVitales.objects.all()
            data = [{
                'id': signos.id,
                'historia_clinica': signos.historia_clinica.id,
                'fecha': str(signos.fecha),
                'pulso': signos.pulso,
                'presion_arterial': signos.presion_arterial,
            } for signos in signos_list]
        return JsonResponse(data, safe=False)

    def post(self, request):
        # Extraer datos del formulario
        id_historia_clinica = request.POST.get('historia_clinica')
        pulso = request.POST.get('pulso')
        presion_arterial = request.POST.get('presion_arterial')
        temperatura = request.POST.get('temperatura')
        frecuencia_respiratoria = request.POST.get('frecuencia_respiratoria')
        saturacion_oxigeno = request.POST.get('saturacion_oxigeno')
        peso = request.POST.get('peso')
        talla = request.POST.get('talla')
        imc = request.POST.get('imc')
        perimetro_cefalico = request.POST.get('perimetro_cefalico')
        
        
        # Validar que todos los campos necesarios estén presentes
        if all([id_historia_clinica, pulso, presion_arterial, temperatura, frecuencia_respiratoria, saturacion_oxigeno, peso, talla, imc, perimetro_cefalico]):
            try:
                # Obtener la historia clínica correspondiente
                print(f"temperatura: {request.POST.get('temperatura')}")
                print(f"peso: {request.POST.get('peso')}")
                print(f"talla: {request.POST.get('talla')}")
    
                historia_clinica = HistoriaClinica.objects.get(id=id_historia_clinica)
                temperatura = Decimal(request.POST.get('temperatura'))
                peso = Decimal(request.POST.get('peso'))
                talla = Decimal(request.POST.get('talla'))
                print(peso)
                # Crear una nueva entrada en SignosVitales
                signos = SignosVitales.objects.create(
                    historia_clinica=historia_clinica,
                    pulso=pulso,
                    presion_arterial=presion_arterial,
                    temperatura=temperatura,
                    frecuencia_respiratoria=frecuencia_respiratoria,
                    saturacion_oxigeno=saturacion_oxigeno,
                    peso=peso,
                    talla=talla,
                    imc = imc,
                    perimetro_cefalico = perimetro_cefalico,   
                )
                return JsonResponse({
                    'id': signos.id,
                    'mensaje': 'Signos vitales registrados exitosamente'
                }, status=201)
            except InvalidOperation as e:
                logger.error(f"Invalid decimal operation: {str(e)}")
                return JsonResponse({'error': 'Error con los valores decimales.'}, status=400)
            except HistoriaClinica.DoesNotExist:
                return JsonResponse({'error': 'Historia clínica no encontrada.'}, status=404)
            
            except ValueError as e:
                logger.error(f"Value error: {str(e)}")
                return JsonResponse({'error': 'Error con los valores numéricos.'}, status=400)
            except Exception as e:
                logger.error(f"Error creating SignosVitales: {str(e)}")
                return JsonResponse({'error': 'Error inesperado al procesar la solicitud.'}, status=500)
        else:
            return JsonResponse({'error': 'Faltan datos obligatorios en la solicitud.'}, status=400)



    def put(self, request, id):
        try:
            signos = SignosVitales.objects.get(id=id)
            data = json.loads(request.body)
            
            signos.pulso = data.get('pulso', signos.pulso )
            signos.presion_arterial = data.get('presion_arterial', signos.presion_arterial)
            signos.temperatura = data.get('temperatura', signos.temperatura)
            signos.frecuencia_respiratoria = data.get('frecuencia_respiratoria', signos.frecuencia_respiratoria)
            signos.saturacion_oxigeno = data.get('saturacion_oxigeno', signos.saturacion_oxigeno)
            signos.peso = data.get('peso', signos.peso)
            signos.talla = data.get('talla',signos.talla)
            signos.imc = data.get('imc', signos.imc)
            signos.perimetro_cefalico = data.get('perimetro_cefalico', signos.perimetro_cefalico)
            
            
            signos.save()
            return JsonResponse({'mensaje': 'Signos Vitales actualizados exitosamente'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Signos Vitales no encontrados'}, status=404)

    def delete(self, request, historiaId,id):
        try:
            signos = SignosVitales.objects.get(id=id)
            signos.delete()
            return JsonResponse({'mensaje': 'Signos Vitales eliminados exitosamente'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Signos Vitales no encontrados'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class ProblemaCronicoApi(View):
    def get(self, request, id=None):
        if id:
            try:
                historia = HistoriaClinica.objects.get(id=id)
                problemas = ProblemaCronico.objects.filter(historia_clinica=historia)
                if problemas.exists():
                    data = [{
                        'id': problema.id,
                        'historia_clinica': problema.historia_clinica.id,
                        'descripcion': problema.descripcion,
                        'fecha_inicio': str(problema.fecha_inicio),
                        'fecha_resolucion': str(problema.fecha_resolucion) if problema.fecha_resolucion else None,
                    } for problema in problemas]
                else:
                    return JsonResponse({'error': 'No se encontraron problemas crónicos para esta historia clínica'}, status=404)
            except HistoriaClinica.DoesNotExist:
                return JsonResponse({'error': 'Historia Clínica no encontrada'}, status=404)
        else:
            problemas = ProblemaCronico.objects.all()
            data = [{
                'id': problema.id,
                'historia_clinica': problema.historia_clinica.id,
                'descripcion': problema.descripcion,
                'fecha_inicio': str(problema.fecha_inicio),
            } for problema in problemas]
        return JsonResponse(data, safe=False)

    def post(self, request):
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_resolucion = request.POST.get('fecha_resolucion')
        historiaId = request.POST.get('historia_clinica')
        historia = HistoriaClinica.objects.get(id =  historiaId)
        descripcion = request.POST.get('descripcion')
        problema = ProblemaCronico.objects.create(historia_clinica = historia, descripcion = descripcion ,fecha_inicio  = fecha_inicio, fecha_resolucion=fecha_resolucion )
        return JsonResponse({
            'id': problema.id,
            'mensaje': 'Problema Crónico registrado exitosamente'
        }, status=201)

    def put(self, request, id):
        try:
            problema = ProblemaCronico.objects.get(id=id)
            data = json.loads(request.body)
            problema.descripcion = data.get('descripcion', problema.descripcion)
            problema.fecha_inicio = data.get('fecha_inicio', problema.fecha_inicio)
            problema.fecha_resolucion = data.get('fecha_resolucion', problema.fecha_resolucion)

            problema.save()
            
            return JsonResponse({'mensaje': 'Problema Crónico actualizado exitosamente'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Problema Crónico no encontrado'}, status=404)

    def delete(self, request,  historiaId,id):
        try:
            problema = ProblemaCronico.objects.get(id=id)
            problema.delete()
            return JsonResponse({'mensaje': 'Problema Crónico eliminado exitosamente'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Problema Crónico no encontrado'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class ProblemaTransitorioApi(View):
    def get(self, request, id=None):
        if id:
            try:
                historia = HistoriaClinica.objects.get(id=id)
                problemas = ProblemaTransitorio.objects.filter(historia_clinica=historia)
                if problemas.exists():
                    data = [{
                        'id': problema.id,
                        'historia_clinica': problema.historia_clinica.id,
                        'descripcion': problema.descripcion,
                        'fecha': str(problema.fecha),
                    } for problema in problemas]
                else:
                    return JsonResponse({'error': 'No se encontraron problemas transitorios para esta historia clínica'}, status=404)
            except HistoriaClinica.DoesNotExist:
                return JsonResponse({'error': 'Historia Clínica no encontrada'}, status=404)
        else:
            problemas = ProblemaTransitorio.objects.all()
            data = [{
                'id': problema.id,
                'historia_clinica': problema.historia_clinica.id,
                'descripcion': problema.descripcion,
                'fecha': str(problema.fecha),
            } for problema in problemas]
        return JsonResponse(data, safe=False)

    def post(self, request):
        fecha = request.POST.get('fecha')
        historiaId = request.POST.get('historia_clinica')
        historia = HistoriaClinica.objects.get(id =  historiaId)
        descripcion = request.POST.get('descripcion')
        problema = ProblemaTransitorio.objects.create(historia_clinica = historia, descripcion = descripcion ,fecha = fecha)
        
        return JsonResponse({
            'id': problema.id,
            'mensaje': 'Problema Transitorio registrado exitosamente'
        }, status=201)

    def put(self, request, id):
        try:
            problema = ProblemaTransitorio.objects.get(id=id)
            data = json.loads(request.body)
            problema.descripcion = data.get('descripcion', problema.descripcion)
            problema.fecha = data.get('fecha', problema.fecha)
            problema.save()
            return JsonResponse({'mensaje': 'Problema Transitorio actualizado exitosamente'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Problema Transitorio no encontrado'}, status=404)

    def delete(self, request,historiaId, id):
        try:
            problema = ProblemaTransitorio.objects.get(id=id)
            problema.delete()
            return JsonResponse({'mensaje': 'Problema Transitorio eliminado exitosamente'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Problema Transitorio no encontrado'}, status=404)

@method_decorator(csrf_exempt, name='dispatch')
class NotaSOAPApi(View):
    def get(self, request, id=None):
        if id:
            try:
                historia = HistoriaClinica.objects.get(id=id)
                notas = NotaSOAP.objects.filter(historia_clinica=historia)
                if notas.exists():
                    data = [{
                        'id': nota.id,
                        'historia_clinica': nota.historia_clinica.id,
                        'fecha': str(nota.fecha),
                        'contenido': nota.contenido,
                    } for nota in notas]
                else:
                    return JsonResponse({'error': 'No se encontraron notas SOAP para esta historia clínica'}, status=404)
            except HistoriaClinica.DoesNotExist:
                return JsonResponse({'error': 'Historia Clínica no encontrada'}, status=404)
        else:
            notas = NotaSOAP.objects.all()
            data = [{
                'id': nota.id,
                'historia_clinica': nota.historia_clinica.id,
                'fecha': str(nota.fecha),
            } for nota in notas]
        return JsonResponse(data, safe=False)

    def post(self, request):
        contenido = request.POST.get('contenido')
        historiaId = request.POST.get('historia_clinica')
        historia = HistoriaClinica.objects.get(id =  historiaId)
        
        nota = NotaSOAP.objects.create(historia_clinica = historia, contenido = contenido)
        return JsonResponse({
            'id': nota.id,
            'mensaje': 'Nota SOAP registrada exitosamente'
        }, status=201)

    def put(self, request, id):
        try:
            nota = NotaSOAP.objects.get(id=id)
            data = json.loads(request.body)
            nota.contenido = data.get('contenido', nota.contenido)
            nota.fecha = data.get('fecha', nota.fecha)
            nota.save()
            return JsonResponse({'mensaje': 'Nota SOAP actualizada exitosamente'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Nota SOAP no encontrada'}, status=404)

    def delete(self, request,id=None, historiaId=None):
        try:
            nota = NotaSOAP.objects.get(id=id)
            nota.delete()
            return JsonResponse({'mensaje': 'Nota SOAP eliminada exitosamente'})
        except ObjectDoesNotExist:
            return JsonResponse({'error': 'Nota SOAP no encontrada'}, status=404)
