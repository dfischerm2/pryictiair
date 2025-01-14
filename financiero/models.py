from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.safestring import mark_safe

from core.custom_models import ModeloBase


TIPO_EF = (
    ("BANCO", "Banco"),
    ("COOP_AHORRO_CREDITO", "Cooperativa de Ahorro y Crédito"),
    ("CAJA_DE_AHORROS", "Caja de Ahorros"),
    ("ASEGURADORA", "Aseguradora"),
)


class EntidadFinanciera(ModeloBase):
    tipo = models.CharField(choices=TIPO_EF, max_length=100, verbose_name="Tipo de entidad financiera")
    logo = models.FileField("Logo del banco", upload_to="financiero/bancos/",
                            help_text="Se recomienda que el archivo sea svg",
                            validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'tiff', 'svg', "jfif"])])
    nombre = models.CharField("Nombre", max_length=200)
    abreviatura = models.CharField("Abreviatura", max_length=200, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.nombre)

    def get_logo(self):
        if self.logo:
            return self.logo.url
        return "/static/images/cards/transferencia-bancaria.png"

    class Meta:
        verbose_name = "Entidad Financiera"
        verbose_name_plural = "Entidades Financieras"
        ordering = ('nombre',)
        # constraints = [
        #     models.CheckConstraint(check=Q(tipo__in=("BANCO", "COOP_AHORRO_CREDITO", "CAJA_DE_AHORROS", "ASEGURADORA")),
        #                            name='tipo__in__TIPO_EF'),
        # ]


TIPO_CUENTA = (
    ("AHORRO", "AHORROS"),
    ("CORRIENTE", "CORRIENTE")
)

TIPO_DOCUMENTO = (
    ("CEDULA", "Cédula"),
    ("RUC", "Ruc"),
)


class CuentaFinancieraEmpresa(ModeloBase):
    ent_fin = models.ForeignKey(EntidadFinanciera, verbose_name="Entidad Financiera", on_delete=models.PROTECT)
    tipo = models.CharField(choices=TIPO_CUENTA, max_length=100, verbose_name="Tipo de cuenta")
    num_cuenta = models.CharField("Nº de Cuenta", max_length=200)
    nombres = models.CharField("Nombres o razón social", max_length=500)
    tipo_documento = models.CharField("Tipo de documento", max_length=200, choices=TIPO_DOCUMENTO)
    documento = models.CharField("Cédula/RUC", max_length=13)
    email = models.CharField("Correo", max_length=500, blank=True, null=True)

    def __str__(self):
        return "{} {} #{}  a nombre de {} {} {}".format(self.ent_fin.__str__(),  self.get_tipo_display(), self.num_cuenta, self.nombres, self.get_tipo_documento_display(), self.documento)

    def get_datos_html(self):
        ef = self.ent_fin
        return mark_safe("{} {} ({}) {}<br>{}: {}<br>{}".format(ef.get_tipo_display(), ef.nombre, self.get_tipo_display(), self.num_cuenta, self.get_tipo_documento_display(), self.documento, self.nombres))

    class Meta:
        verbose_name = "Cuenta Financiera Empresa"
        verbose_name_plural = "Cuentas Financieras Empresa"
        ordering = ('ent_fin__nombre',)
        # constraints = [
        #     models.CheckConstraint(check=Q(tipo__in=("AHORRO", "CORRIENTE")),
        #                            name='tipo__in__TIPO_CUENTA'),
        #     models.CheckConstraint(check=Q(tipo_documento__in=("CEDULA", "RUC")),
        #                            name='tipo__in__TIPO_DOCUMENTO'),
        # ]
