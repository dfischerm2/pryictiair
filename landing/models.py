from django.db import models
from core.custom_models import ModeloBase


# Create your models here.


class Sponsor(ModeloBase):
    name = models.CharField(max_length=500)
    image = models.ImageField(upload_to='sponsor/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sponsor'
        verbose_name_plural = 'Sponsors'
        ordering = ['name']


class TopicCategory(ModeloBase):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Topic Category'
        verbose_name_plural = 'Topic Categories'
        ordering = ['name']


class Topic(ModeloBase):
    category = models.ForeignKey(TopicCategory, related_name='topics', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['name']


class GuidelineType(ModeloBase):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Guideline Type'
        verbose_name_plural = 'Guideline Types'
        ordering = ['name']


class Guideline(ModeloBase):
    guideline_type = models.ForeignKey(GuidelineType, related_name='guidelines', on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"{self.guideline_type.name}: {self.content[:50]}"

    class Meta:
        verbose_name = 'Guideline'
        verbose_name_plural = 'Guidelines'
        ordering = ['guideline_type', 'content']


class ImportantDate(ModeloBase):
    title = models.CharField(max_length=200)
    date = models.DateField()

    def __str__(self):
        return f"{self.title} - {self.date}"

    class Meta:
        verbose_name = 'Important Date'
        verbose_name_plural = 'Important Dates'
        ordering = ['date']


class Summary(ModeloBase):
    title = models.CharField(max_length=200)
    description = models.TextField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Summary'
        verbose_name_plural = 'Summaries'
        ordering = ['title']


class CommitteeCategory(ModeloBase):
    name = models.CharField(max_length=200)
    order = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Committee Category'
        verbose_name_plural = 'Committee Categories'
        ordering = ['order']


class CommitteeMember(ModeloBase):
    category = models.ForeignKey(CommitteeCategory, related_name='members', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    degree = models.CharField(max_length=100)
    rol = models.CharField(max_length=500, default='')
    description_rol = models.TextField(default='')
    photo = models.ImageField(upload_to='committee_members/', null=True, blank=True)
    linkedin = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    x = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Committee Member'
        verbose_name_plural = 'Committee Members'
        ordering = ['name']


class PersonNotificacion(ModeloBase):
    identification = models.CharField(max_length=200, unique=True, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    last_name = models.CharField(max_length=300, null=True, blank=True)
    first_name = models.CharField(max_length=300, null=True, blank=True)
    middle_name = models.CharField(max_length=300, null=True, blank=True)
    prefered_name = models.CharField(max_length=400, null=True, blank=True)
    name_prefix = models.CharField(max_length=200, null=True, blank=True)
    name_suffix = models.CharField(max_length=200, null=True, blank=True)
    country = models.CharField(max_length=200, null=True, blank=True)
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f"{ self.identification } - {self.last_name} {self.first_name} {self.middle_name}"

    def get_name_prefix_suffix(self):
        return f"{ self.name_prefix } {self.last_name} {self.first_name} {self.middle_name} { self.name_suffix}".strip()

    class Meta:
        verbose_name = 'Person Notificacion'
        verbose_name_plural = 'Person Notificaciones'
        ordering = ['identification']