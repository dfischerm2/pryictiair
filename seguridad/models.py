from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.safestring import mark_safe

from autenticacion.models import Usuario
from core.custom_models import ModeloBase, NormalModel
from core.models_utils import FileNameUploadToPath
from core.validadores import validate_file_size_20mb
from pryictiair.settings import AUTH_USER_MODEL


class ErrorLog(models.Model):
    usuario = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Usuario', blank=True, null=True)
    archivo = models.TextField(verbose_name='Archivo', blank=True, null=True)
    metodo = models.CharField(max_length=100, verbose_name='Metodo', blank=True, null=True)
    accion = models.CharField(max_length=100, verbose_name='Acción', blank=True, null=True)
    tipo = models.CharField(max_length=100, verbose_name='Tipo Error', blank=True, null=True)
    linea = models.CharField(max_length=100, verbose_name='Linea', blank=True, null=True)
    descripcion = models.TextField(verbose_name='Descripción', blank=True, null=True)
    corregido = models.BooleanField(default=False, verbose_name="¿Error Corregido?")
    fecha = models.DateTimeField(verbose_name='Fecha', auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.accion = self.accion.upper()
        super(ErrorLog, self).save(force_insert, force_update, using)

    def __str__(self):
        return "{} - {} - {} [{}]".format(self.tipo, self.linea, self.descripcion, self.accion)

    class Meta:
        verbose_name = 'ErrorLog'
        verbose_name_plural = 'ErrorLogs'
        ordering = ('-fecha', 'pk')


class UsuarioConectado(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    sesion = models.ForeignKey("sessions.Session", on_delete=models.CASCADE, blank=True, null=True)
    dispositivo = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Dispositivo')
    ip = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Ip')
    fecha_conexion = models.DateTimeField(blank=True, null=True)

    def ultima_vez(self):
        fechaactual = timezone.now()
        tiempo = fechaactual - self.fecha_conexion
        return 'Hace {}'.format(str(tiempo).replace('day', 'dia').split('.')[0])

    def is_not_expired(self):
        from datetime import datetime
        return self.sesion.expire_date > datetime.now()


class AudiUsuarioTabla(models.Model):
    usuario = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Usuario', editable=False)
    usuario_admin = models.ForeignKey(AUTH_USER_MODEL, editable=False, on_delete=models.PROTECT,
                                      verbose_name='Usuario Administrador', blank=True, null=True,
                                      related_name="fk_usuario_admin")
    # GenericForeignKey
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    modelo = GenericForeignKey('content_type', 'object_id')
    # ----------------------------------------------------------------
    registroname = models.CharField(max_length=1000, editable=False, verbose_name='Registro Name')
    accion = models.CharField(max_length=100, verbose_name='Acción', editable=False)
    fecha = models.DateTimeField(verbose_name='Fecha', auto_now_add=True)
    datos_json = models.TextField(verbose_name="Datos en formato json", null=True, blank=True, editable=False)
    ip = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Ip')

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.registroname = str(self.registroname).upper()
        self.accion = self.accion.upper()
        super(AudiUsuarioTabla, self).save(force_insert, force_update, using)

    def get_model_name(self):
        return self.modelo.__class__.__name__ if self.modelo else ''

    def __str__(self):
        return "{} - {} - {} [{}]".format(self.usuario.username, self.modelo.__class__.__name__ if self.modelo else '', self.registroname, self.accion)

    class Meta:
        verbose_name = 'Auditoría Usuario'
        verbose_name_plural = 'Auditorías Usuarios'
        ordering = ('-fecha', 'pk')


TIPO_ENTORNO = ((True, "Producción"), (False, "Test"),)




class Configuracion(ModeloBase):
    ico = models.FileField(upload_to='configuracion/', max_length=600, blank=True, null=True, verbose_name='Favicon', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'svg', "jfif"])])
    logo_sistema = models.FileField(upload_to='configuracion/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'svg', "jfif"])], max_length=600, blank=True, null=True, verbose_name='Logo')
    logo_sistema_white = models.FileField(upload_to='configuracion/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'svg', "jfif"])], max_length=600, blank=True, null=True, verbose_name='Logo Blanco')
    fondo_perfil = models.FileField(upload_to='configuracion/fondo_perfil/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'svg', "jfif"])], blank=True, null=True, verbose_name='Fondo de perfil de usuario', help_text='Se recomienda que la imagen tenga un tamaño de 500x281')
    banner_login = models.FileField(upload_to='configuracion/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'svg', "jfif"])], blank=True, null=True, verbose_name='Fondo Login')
    fondoprincipal = models.FileField(upload_to='configuracion/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'svg', "jfif"])], blank=True, null=True, verbose_name='Fondo Principal')
    imagenprincipal = models.FileField(upload_to='configuracion/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'svg', "jfif"])], blank=True, null=True, verbose_name='Imagen Sobre Nosotros')
    nombre_empresa = models.CharField(max_length=1000, verbose_name='Nombre de la Empresa')
    alias = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Alias')
    descripcion = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Descripción')
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono Empresa')
    email = models.CharField(max_length=100, blank=True, null=True, verbose_name='Email Empresa')
    web = models.CharField(max_length=100, blank=True, null=True, verbose_name='Web')
    email_notificacion = models.CharField(max_length=100, blank=True, null=True, verbose_name='Email Notificaciones')
    direccion = models.CharField(max_length=5000, blank=True, null=True, verbose_name='Dirección Empresa')
    # metodos de pago
    paypal_modo = models.BooleanField("Running PayPal", choices=TIPO_ENTORNO, default=1)
    porcentaje_pagoonline = models.DecimalField(max_digits=19, decimal_places=2, default=0,
                                                verbose_name='% Convenience Fee',
                                                validators=[MinValueValidator(Decimal('0')),
                                                            MaxValueValidator(Decimal('100'))])

    @staticmethod
    def get_instancia():
        from core.funciones import db_table_exists
        try:
            # confi = Configuracion.objects.first()
            confi = Configuracion.objects.first() if db_table_exists(
                Configuracion._meta.db_table) and Configuracion.objects.count() > 0 else Configuracion()
        except Exception as ex:
            confi = Configuracion()
        return confi

    class Meta:
        verbose_name = 'Configuración'
        verbose_name_plural = 'Configuración'
        permissions = (
            ("can_view_auditoria", "Puede ver auditorías"),
        )


class Modulo(ModeloBase):
    url = models.CharField(max_length=100)
    nombre = models.CharField(max_length=100)
    orden = models.IntegerField(default=0)

    def __str__(self):
        return '{} ({})'.format(self.nombre, self.url)

    class Meta:
        verbose_name = 'URL del Sidebar'
        verbose_name_plural = 'URLs del Sidebar'
        ordering = ['nombre']


class GroupModulo(ModeloBase):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    modulos = models.ManyToManyField(Modulo)

    def __str__(self):
        return '{}'.format(self.group.name)

    class Meta:
        verbose_name = 'Asignar Urls a cada rol de usuario'
        verbose_name_plural = 'Asignar Urls a cada rol de usuario'
        ordering = ('pk',)


class ModuloGrupo(ModeloBase):
    nombre = models.CharField(max_length=100)
    icono = models.CharField(max_length=100)
    modulos = models.ManyToManyField(Modulo)
    prioridad = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return '{} {}'.format(self.nombre, self.prioridad)

    class Meta:
        verbose_name = 'Grupo de URLs del Sidebar'
        verbose_name_plural = 'Grupos de URLs del Sidebar'
        ordering = ('prioridad', 'nombre')
        # permissions = (
        #     ('')
        # )

    def modulos_ordenados(self):
        return self.modulos.all().order_by('orden')

    def modulos_activos(self):
        return self.modulos.filter(status=True).order_by('orden')

def slug_name(self):
    from django.utils.text import slugify
    return slugify(self.name)


Group.add_to_class("slug_name", slug_name)


class SessionUser(NormalModel):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.OneToOneField("sessions.Session", on_delete=models.CASCADE)
    dispositivo = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Dispositivo')
    ip = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Ip')
    codigounico = models.TextField("Código Único de navegador")
    fecha_conexion = models.DateTimeField(auto_now_add=True)
    areageografica = models.CharField("Área Geográfica", max_length=500, null=True, blank=True)

    @staticmethod
    def nuevo(request):
        from core.funciones import get_client_ip
        from django.contrib.sessions.models import Session
        ucc = SessionUser.objects.get_or_create(session_id=Session.objects.get(session_key=request.session.session_key).pk,
                                                   user_id=request.user.pk, codigounico=request.COOKIES.get('SISTEMA_DEVICE_ID') or 'SINCODIGO')[0]
        ucc.fecha_conexion = datetime.now()
        ucc.ip = get_client_ip(request)
        ucc.save()
        return ucc

    def ultima_vez(self):
        fechaactual = datetime.now()
        tiempo = fechaactual - self.fecha_conexion.astimezone(timezone.get_current_timezone()).replace(tzinfo=None)
        return 'Hace {}'.format(str(tiempo).replace('day', 'dia').split('.')[0])

    def is_not_expired(self):
        from datetime import datetime
        return self.session.expire_date > datetime.now()



TIPO_CERTIFICADO = (
    (1, 'HORIZONTAL'),
    (2, 'VERTICAL'),
)

FORMATO_CERTIFICADO = (
    (1, 'CON LOGO'),
    (2, 'CON MENCIÓN'),
)


class CertificadosFormato(ModeloBase):
    nombre = models.CharField(default='', blank=True, null=True, max_length=200, verbose_name=u"Nombre")
    tipocertificado = models.IntegerField(choices=TIPO_CERTIFICADO, default=1, verbose_name=u'Tipo Certificado')
    formato = models.IntegerField(choices=FORMATO_CERTIFICADO, default=1, verbose_name=u'Tipo Certificado')
    color = models.CharField(default='', blank=True, null=True, max_length=200, verbose_name=u"Color")
    fondocertificado = models.FileField(upload_to='cursos/fondocertificados/', max_length=6000, blank=True, null=True,
                                        verbose_name="Fondo Alfrente",
                                        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', "jfif", "svg"]),validate_file_size_20mb])
    fondocertificadoatras = models.FileField(upload_to='cursos/fondocertificados/', max_length=6000, blank=True,
                                             null=True, verbose_name="Fondo Atras",
                                             validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', "jfif", "svg"]), validate_file_size_20mb])

    def __str__(self):
        return u'%s' % self.nombre

    class Meta:
        verbose_name = u"Formato de certificación"
        verbose_name_plural = u"Formato de certificaciones"
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        self.nombre = self.nombre.upper().strip()
        super(CertificadosFormato, self).save(*args, **kwargs)