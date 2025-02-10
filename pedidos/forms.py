from django import forms

from core.custom_forms import FormModeloBase, ExtFileField

ESTADOS_VALIDACION_INSCRIPCION_CHOICES = (
    ('', 'Escoja un opción'),
    (1, 'Aprobar inscripcion'),
    (2, 'Rechazar inscripcion'),
)

class ValidateRequestInscriptionForm(FormModeloBase):
    estado = forms.ChoiceField(choices=ESTADOS_VALIDACION_INSCRIPCION_CHOICES, label='Estado de la inscripción', required=True, widget=forms.Select(attrs={'class': 'form-control jselect2'}))
    observacion = forms.CharField(label='Observación', required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))


class UploadInvoiceForm(FormModeloBase):
    archivo = ExtFileField(label=u'Cargar factura', required=False, help_text=u'Tamaño Maximo permitido 4Mb pdf', ext_whitelist=(".pdf",), max_upload_size=4194304,widget=forms.FileInput(attrs={'class': 'dropify', 'col': '12'}))