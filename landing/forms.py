from django import forms
from django.forms import ModelForm

from .models import Sponsor, TopicCategory, Topic, GuidelineType, Guideline, ImportantDate, Summary, CommitteeCategory, \
    CommitteeMember, SponsorCategory, SummaryImage, PrincipalCarrousel, CallForPapers, TYPE_DOCUMENT
from core.custom_models import ModelFormBase


class SponsorCategoryForm(ModelFormBase):
    class Meta:
        model = SponsorCategory
        fields = ('order', 'public', 'name',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(SponsorCategoryForm, self).__init__(*args, **kwargs)
        for k, v in self.fields.items():
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class SponsorForm(ModelFormBase):
    class Meta:
        model = Sponsor
        fields = ('category', 'name', 'image', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(SponsorForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = self.fields['category'].queryset.filter(status=True).order_by('-id')
        for k, v in self.fields.items():
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
        fields = ('category', 'name', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(TopicForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = self.fields['category'].queryset.all().order_by('-id')
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
        fields = ('guideline_type', 'content', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(GuidelineForm, self).__init__(*args, **kwargs)
        self.fields['guideline_type'].queryset = self.fields['guideline_type'].queryset.all().order_by('-id')
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

        check_fields = ['view_committe', 'view_topics', 'view_sponsors', 'view_call_for_papers']
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
        fields = ('summary', 'name', 'image', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(SummaryImageForm, self).__init__(*args, **kwargs)
        self.fields['summary'].widget.attrs['readonly'] = "readonly"
        for k, v in self.fields.items():
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
            'category', 'name', 'degree', 'rol', 'description_rol', 'photo', 'linkedin', 'x', 'instagram', 'facebook',
            'youtube', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(CommitteeMemberForm, self).__init__(*args, **kwargs)
        self.fields['category'].queryset = self.fields['category'].queryset.filter(status=True).order_by('-id')
        for k, v in self.fields.items():
            if k == 'category':  # Aplica jselect2 solo al campo ForeignKey
                self.fields[k].widget.attrs['class'] = "jselect2"
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
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'


class CallForPapersForm(ModelFormBase):
    class Meta:
        model = CallForPapers
        fields = ('name', 'type_document', 'order', 'public', 'file_example')

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(CallForPapersForm, self).__init__(*args, **kwargs)
        self.fields['type_document'].queryset = TYPE_DOCUMENT
        for k, v in self.fields.items():
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'
