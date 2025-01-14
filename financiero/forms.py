from core.custom_models import ModelFormBase
from financiero.models import EntidadFinanciera, CuentaFinancieraEmpresa


class EntidadFinancieraForm(ModelFormBase):
    class Meta:
        model = EntidadFinanciera
        exclude = ('usuario_creacion', 'fecha_registro', 'hora_registro', 'status','usuario_modificacion')

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver') if 'ver' in kwargs else False
        self.editando = True if 'instance' in kwargs else False
        instancia = kwargs.get('instance', None)
        super(EntidadFinancieraForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            self.fields[k].widget.attrs['class'] = "form-control"
            if ver:
                self.fields[k].widget.attrs['readonly'] = 'readonly'
        if self.editando:
            self.fields["logo"].widget.attrs['data_default_file'] = instancia.logo.url if instancia.logo else ""


class CuentaFinancieraForm(ModelFormBase):
    class Meta:
        model = CuentaFinancieraEmpresa
        exclude = ('usuario_creacion', 'fecha_registro', 'hora_registro', 'status','usuario_modificacion')

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver') if 'ver' in kwargs else False
        self.editando = True if 'instance' in kwargs else False
        super(CuentaFinancieraForm, self).__init__(*args, **kwargs)
        self.fields['ent_fin'].queryset = EntidadFinanciera.objects.filter(status=True)
        for k, v in self.fields.items():
            self.fields[k].widget.attrs['class'] = "form-control"
            if k in ('ent_fin','tipo',):
                self.fields[k].widget.attrs['class'] = "form-control select2-simple"
            if ver:
                self.fields[k].widget.attrs['readonly'] = 'readonly'

    def clean_num_cuenta(self):
        num_cuenta = self.cleaned_data["num_cuenta"]
        return num_cuenta.replace(' ', '').upper()

    def clean_nombres(self):
        nombres = self.cleaned_data["nombres"]
        return nombres.upper()

    def clean_documento(self):
        documento = self.cleaned_data["documento"]
        return documento.replace(' ', '').upper()