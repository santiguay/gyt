from django.db import models
from django.contrib.auth.models import User

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=20)
    contrasenha = models.CharField(max_length=125, blank=True)



class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=20)
    contrasenha = models.CharField(max_length=125, blank=True)

class HistoriaClinica(models.Model):
    perfil_usuario = models.OneToOneField(PerfilUsuario, on_delete=models.CASCADE)
    fecha_nacimiento = models.DateField()
    sexo = models.CharField(max_length=10)
    documento = models.CharField(max_length=20)
    domicilio = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    estado_civil = models.CharField(max_length=20)
    jefe_familia = models.CharField(max_length=100)
    prontuario = models.CharField(max_length=50, blank=True)

class SignosVitales(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    pulso = models.IntegerField()
    presion_arterial = models.CharField(max_length=20)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1)
    frecuencia_respiratoria = models.IntegerField()
    saturacion_oxigeno = models.IntegerField()
    peso = models.DecimalField(max_digits=5, decimal_places=2)
    talla = models.DecimalField(max_digits=3, decimal_places=2)
    imc = models.DecimalField(max_digits=4, decimal_places=2)
    perimetro_cefalico = models.DecimalField(max_digits=4, decimal_places=2)

class ProblemaCronico(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_resolucion = models.DateField(null=True, blank=True)

class ProblemaTransitorio(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    fecha = models.DateField()

class NotaSOAP(models.Model):
    historia_clinica = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    contenido = models.TextField()
class Consulta(models.Model):
    paciente = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='consultas_paciente')
    medico = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name='consultas_medico')
    fecha = models.DateTimeField(auto_now_add=True)
    motivo = models.CharField(max_length=200)
    diagnostico = models.TextField()
    tratamiento = models.TextField()

    def __str__(self):
        return f"Consulta de {self.paciente.usuario.get_full_name()} con {self.medico.usuario.get_full_name()}"