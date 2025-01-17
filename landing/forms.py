from django import forms
from django.forms import ModelForm
from django.utils.safestring import mark_safe

from .models import Sponsor, TopicCategory, Topic, GuidelineType, Guideline, ImportantDate, Summary, CommitteeCategory, \
    CommitteeMember, SponsorCategory, SummaryImage, PrincipalCarrousel, CallForPapers, TYPE_DOCUMENT, Conference, \
    ConferenceFee, DetailConferenceFee
from core.custom_models import ModelFormBase


class SponsorCategoryForm(ModelFormBase):
    class Meta:
        model = SponsorCategory
        fields = ('order', 'name', 'public', 'carrousel', )

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(SponsorCategoryForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if k in ['public', 'carrousel']: self.fields[k].widget.attrs['col'] = '6'
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class SponsorForm(ModelFormBase):
    class Meta:
        model = Sponsor
        fields = ('name', 'image', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(SponsorForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if k == 'category':  # Aplica jselect2 solo al campo ForeignKey
                self.fields[k].widget.attrs['class'] = "jselect2"
            if k in('image'):
                self.fields[k].widget.attrs['class'] = 'dropify'
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class TopicCategoryForm(ModelFormBase):
    class Meta:
        model = TopicCategory
        fields = ('name', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(TopicCategoryForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class TopicForm(ModelFormBase):
    class Meta:
        model = Topic
        fields = ('name', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(TopicForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if k == 'category':  # Aplica jselect2 solo al campo ForeignKey
                self.fields[k].widget.attrs['class'] = "jselect2"
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class GuidelineTypeForm(ModelFormBase):
    class Meta:
        model = GuidelineType
        fields = ('name', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(GuidelineTypeForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class GuidelineForm(ModelFormBase):
    class Meta:
        model = Guideline
        fields = ('content', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(GuidelineForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if k == 'guideline_type':  # Aplica jselect2 solo al campo ForeignKey
                self.fields[k].widget.attrs['class'] = "jselect2"
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class ImportantDateForm(ModelFormBase):
    class Meta:
        model = ImportantDate
        fields = ('title', 'start_date', 'end_date', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(ImportantDateForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class SummaryForm(ModelFormBase):
    class Meta:
        model = Summary
        fields = (
            'title_principal', 'title',
            'description', 'start_date',
            'end_date', 'activo', 'public',
            'view_committe', 'text_committe',
            'view_topics', 'text_topics',
            'view_sponsors', 'text_sponsors',
            'view_call_for_papers', 'text_call_for_papers',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(SummaryForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'

        check_fields = ['view_committe', 'view_topics', 'view_sponsors', 'view_call_for_papers', 'activo', 'public', 'start_date', 'end_date']
        text_fields = ['text_committe', 'text_topics', 'text_sponsors', 'text_call_for_papers']

        for field in check_fields:
            self.fields[field].widget.attrs['col'] = '6'

        for field in text_fields:
            self.fields[field].widget.attrs['col'] = '6'

        if self.instance.view_committe:
            self.fields['text_committe'].widget.attrs['disabled'] = 'disabled'
        if self.instance.view_topics:
            self.fields['text_topics'].widget.attrs['disabled'] = 'disabled'
        if self.instance.view_sponsors:
            self.fields['text_sponsors'].widget.attrs['disabled'] = 'disabled'
        if self.instance.view_call_for_papers:
            self.fields['text_call_for_papers'].widget.attrs['disabled'] = 'disabled'


class SummaryImageForm(ModelFormBase):
    class Meta:
        model = SummaryImage
        fields = ('summary', 'name', 'public', 'position', 'image', )

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(SummaryImageForm, self).__init__(*args, **kwargs)
        self.fields['summary'].widget.attrs['readonly'] = "readonly"
        for k, v in self.fields.items():
            if k in ['position', 'public']:
                self.fields[k].widget.attrs['col'] = '6'
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class CommitteeCategoryForm(ModelFormBase):
    class Meta:
        model = CommitteeCategory
        fields = ('name', 'order', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(CommitteeCategoryForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class CommitteeMemberForm(ModelFormBase):
    class Meta:
        model = CommitteeMember
        fields = (
            'category', 'sexo', 'name', 'degree', 'rol', 'description_rol', 'photo', 'linkedin', 'x', 'instagram', 'facebook',
            'youtube', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(CommitteeMemberForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = self.fields['category'].queryset.filter(status=True).order_by('-id')
        for k, v in self.fields.items():
            if k in ['category', 'sexo']:  # Aplica jselect2 solo al campo ForeignKey
                self.fields[k].widget.attrs['class'] = "jselect2"
            if k in ['category', 'sexo', 'degree', 'rol', 'linkedin', 'x', 'instagram', 'facebook', 'youtube', 'public']:
                self.fields[k].widget.attrs['col'] = "6"
            if k in('photo'):
                self.fields[k].widget.attrs['class'] = 'dropify'
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class PrincipalCarrouselForm(ModelFormBase):
    class Meta:
        model = PrincipalCarrousel
        fields = ('name', 'order', 'public', 'image')

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(PrincipalCarrouselForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if k in ['order', 'public']:
                self.fields[k].widget.attrs['col'] = '6'
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class CallForPapersForm(ModelFormBase):
    class Meta:
        model = CallForPapers
        fields = ('name', 'type_document', 'order', 'name_button', 'public', 'url', 'icon','file_example')

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(CallForPapersForm, self).__init__(*args, **kwargs)
        self.fields['type_document'].queryset = TYPE_DOCUMENT
        for k, v in self.fields.items():
            if k in ['order', 'name_button', 'public', 'type_document', 'url',]:
                self.fields[k].widget.attrs['col'] = '6'
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class ConferenceForm(ModelFormBase):
    class Meta:
        model = Conference
        exclude = ('usuario_creacion', 'fecha_registro', 'hora_registro', 'status', 'usuario_modificacion',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver') if 'ver' in kwargs else False
        instancia = kwargs["instance"] if 'instance' in kwargs else None
        super(ConferenceForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            self.fields[k].widget.attrs['class'] = "form-control"

            if k in ('start_date','end_date','max_papers', 'value_adittional_paper','max_sheets', 'value_adittional_sheet',):
                self.fields[k].widget.attrs['col'] = "6"

            if k in ('active',):
                self.fields[k].widget.attrs['class'] = "js-switch"
                self.fields[k].widget.attrs['data-render'] = "switchery"
                self.fields[k].widget.attrs['data-theme'] = "default"


class ConferenceFeeForm(ModelFormBase):
    class Meta:
        model = ConferenceFee
        exclude = ('usuario_creacion', 'fecha_registro', 'hora_registro', 'status', 'usuario_modificacion','conference',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver') if 'ver' in kwargs else False
        instancia = kwargs["instance"] if 'instance' in kwargs else None
        super(ConferenceFeeForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            self.fields[k].widget.attrs['class'] = "form-control"
            self.fields[k].widget.attrs['col'] = "6"

            if k in ('role',):
                self.fields[k].widget.attrs['class'] = "jselect2"

            if k in ('published',):
                self.fields[k].widget.attrs['class'] = "js-switch"
                self.fields[k].widget.attrs['data-render'] = "switchery"
                self.fields[k].widget.attrs['data-theme'] = "default"


class DetailConferenceFeeForm(ModelFormBase):
    class Meta:
        model = DetailConferenceFee
        exclude = ('usuario_creacion', 'fecha_registro', 'hora_registro', 'status', 'usuario_modificacion','cab',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver') if 'ver' in kwargs else False
        instancia = kwargs["instance"] if 'instance' in kwargs else None
        super(DetailConferenceFeeForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            self.fields[k].widget.attrs['class'] = "form-control"
            self.fields[k].widget.attrs['col'] = "6"

            if k in ('published',):
                self.fields[k].widget.attrs['class'] = "js-switch"
                self.fields[k].widget.attrs['data-render'] = "switchery"
                self.fields[k].widget.attrs['data-theme'] = "default"





