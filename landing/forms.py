from django import forms
from .models import Sponsor, TopicCategory, Topic, GuidelineType, Guideline, ImportantDate, Summary, CommitteeCategory, \
    CommitteeMember
from core.custom_models import ModelFormBase


class SponsorForm(ModelFormBase):
    class Meta:
        model = Sponsor
        fields = ('name', 'image', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(SponsorForm, self).__init__(*args, **kwargs)
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
        fields = ('title', 'date', 'public',)

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
        fields = ('title', 'description', 'activo', 'public',)

    def __init__(self, *args, **kwargs):
        ver = kwargs.pop('ver', False)
        self.editando = 'instance' in kwargs
        super(SummaryForm, self).__init__(*args, **kwargs)
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
        self.fields['category'].queryset = self.fields['category'].queryset.all().order_by('-id')
        for k, v in self.fields.items():
            if k == 'category':  # Aplica jselect2 solo al campo ForeignKey
                self.fields[k].widget.attrs['class'] = "jselect2"
            if ver:
                self.fields[k].widget.attrs['disabled'] = 'disabled'
