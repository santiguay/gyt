from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=20)
    contrasenha = models.CharField(max_length=125, blank=True)

class HistoriaClinica(models.Model):
    nombre = models.CharField(max_length=250, blank=True)
    fecha_nacimiento = models.DateField(default=timezone.now)
    sexo = models.CharField(max_length=10)
    documento = models.CharField(max_length=20)
    domicilio = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    estado_civil = models.CharField(max_length=20)
    jefe_familia = models.CharField(max_length=100)
    prontuario = models.CharField(max_length=50, blank=True)
    fecha = models.DateField(default=timezone.now)

class SignosVitales(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)  # Remove auto_now_add=True
    pulso = models.IntegerField()
    presion_arterial = models.CharField(max_length=20)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1)
    frecuencia_respiratoria = models.IntegerField()
    saturacion_oxigeno = models.IntegerField()
    peso = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    talla = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    imc = models.DecimalField(max_digits=4, decimal_places=2, default=0.0) 
    perimetro_cefalico = models.DecimalField(max_digits=4, decimal_places=2, default=0.0)

class ProblemaCronico(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_resolucion = models.DateField(null=True, blank=True)

class ProblemaTransitorio(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    fecha = models.DateField(default=timezone.now)
    
class NotaSOAP(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)  # Set default value
    contenido = models.TextField()
