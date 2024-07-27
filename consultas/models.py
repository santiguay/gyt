from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=20)
    contrasenha = models.CharField(max_length=125, blank=True)

class HistoriaClinica(models.Model):
    prontuario = models.CharField(max_length=50, unique=True)
    jefe_familia = models.CharField(max_length=100)
    nombre_apellidos = models.CharField(max_length=200)
    fecha_nacido = models.DateField()
    sexo = models.CharField(max_length=10)
    documento = models.CharField(max_length=50)
    domicilio = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    estado_civil = models.CharField(max_length=20)

class SignosVitales(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    pulso = models.IntegerField()
    presion_arterial = models.CharField(max_length=20)
    temperatura = models.FloatField()
    frecuencia_respiratoria = models.IntegerField()
    saturacion_oxigeno = models.FloatField()

class DatosCorporales(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    peso = models.FloatField()
    talla = models.FloatField()
    imc = models.FloatField()
    porcentaje_grasa_corporal = models.FloatField()

class ProblemaCronico(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_control = models.DateField()

class ProblemaTransitorio(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    fechas = models.JSONField()  # Almacena múltiples fechas como un array JSON

class NotaSOAP(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    contenido = models.TextField()