from django.db import models
from core.custom_models import ModeloBase


# Create your models here.

class SponsorCategory(ModeloBase):
    order = models.IntegerField(default=0)
    public = models.BooleanField(default=True)
    carrousel = models.BooleanField(default=False)
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sponsor Category'
        verbose_name_plural = 'Sponsor Categories'
        ordering = ['order']


class Sponsor(ModeloBase):
    category = models.ForeignKey(SponsorCategory, related_name='sponsors', on_delete=models.CASCADE, null=True, blank=True)
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=500)
    image = models.ImageField(upload_to='sponsor/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Sponsor'
        verbose_name_plural = 'Sponsors'
        ordering = ['name']


class TopicCategory(ModeloBase):
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Topic Category'
        verbose_name_plural = 'Topic Categories'
        ordering = ['name']


class Topic(ModeloBase):
    public = models.BooleanField(default=True)
    category = models.ForeignKey(TopicCategory, related_name='topics', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['name']


class GuidelineType(ModeloBase):
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Guideline Type'
        verbose_name_plural = 'Guideline Types'
        ordering = ['name']


class Guideline(ModeloBase):
    public = models.BooleanField(default=True)
    guideline_type = models.ForeignKey(GuidelineType, related_name='guidelines', on_delete=models.CASCADE)
    content = models.TextField()

    def __str__(self):
        return f"{self.guideline_type.name}: {self.content[:50]}"

    class Meta:
        verbose_name = 'Guideline'
        verbose_name_plural = 'Guidelines'
        ordering = ['guideline_type', 'content']


class ImportantDate(ModeloBase):
    public = models.BooleanField(default=True)
    title = models.CharField(max_length=200)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.start_date}"

    class Meta:
        verbose_name = 'Important Date'
        verbose_name_plural = 'Important Dates'
        ordering = ['start_date']

    def get_formatted_date_range(self):
        if self.start_date and self.end_date:
            start_month = self.start_date.strftime("%B")
            start_day = self.start_date.strftime("%d")

            end_month = self.end_date.strftime("%B")
            end_day = self.end_date.strftime("%d")

            if start_month == end_month:
                if start_day == end_day:
                    return f"{start_month} {start_day}, {self.start_date.year}"
                return f"{start_month} {start_day} - {end_day}, {self.start_date.year}"
            else:
                return f"{start_month} {start_day} - {end_month} {end_day}, {self.start_date.year}"
        elif self.start_date:
            start_month = self.start_date.strftime("%B")
            start_day = self.start_date.strftime("%d")
            return f"{start_month} {start_day}, {self.start_date.year}"
        return ""


class Summary(ModeloBase):
    public = models.BooleanField(default=True)
    title_principal = models.CharField(max_length=200, default='')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    activo = models.BooleanField(default=True)
    view_committe = models.BooleanField(default=False)
    text_committe = models.CharField(max_length=200, default='', null=True, blank=True)
    view_topics = models.BooleanField(default=False)
    text_topics = models.CharField(max_length=200, default='', null=True, blank=True)
    view_sponsors = models.BooleanField(default=False)
    text_sponsors = models.CharField(max_length=200, default='', null=True, blank=True)
    view_call_for_papers = models.BooleanField(default=False)
    text_call_for_papers = models.CharField(max_length=200, default='', null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Summary'
        verbose_name_plural = 'Summaries'
        ordering = ['title']

    def get_formatted_date_range(self):
        if self.start_date and self.end_date:
            start_month = self.start_date.strftime("%B")
            start_day = self.start_date.strftime("%d")
            start_suffix = self._get_day_suffix(self.start_date.day)

            end_month = self.end_date.strftime("%B")
            end_day = self.end_date.strftime("%d")
            end_suffix = self._get_day_suffix(self.end_date.day)

            if start_month == end_month:
                return f"{start_month} {start_day}{start_suffix} to {end_day}{end_suffix}, {self.start_date.year}"
            else:
                return f"{start_month} {start_day}{start_suffix} to {end_month} {end_day}{end_suffix}, {self.start_date.year}"
        return ""

    def _get_day_suffix(self, day):
        # Retorna el sufijo correcto para los días (1st, 2nd, 3rd, etc.)
        if 11 <= day <= 13:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")


class SummaryImage(ModeloBase):
    TYPE_POSITION = (
        (1, 'START'),
        (2, 'MIDDLE'),
        (3, 'END'),
    )
    public = models.BooleanField(default=True, )
    summary = models.ForeignKey(Summary, related_name='images', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='summary_images/')
    position = models.IntegerField(choices=TYPE_POSITION, default=1)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Summary Image'
        verbose_name_plural = 'Summary Images'
        ordering = ['name']
        unique_together = ['summary', 'position']


class CommitteeCategory(ModeloBase):
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=200)
    order = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Committee Category'
        verbose_name_plural = 'Committee Categories'
        ordering = ['order']


class CommitteeMember(ModeloBase):
    SEXO = (
        ("MASCULINO", "Masculino"),
        ("FEMENINO", "Femenino"),
        ("NINGUNO", "Sin definir"),
    )
    public = models.BooleanField(default=True)
    category = models.ForeignKey(CommitteeCategory, related_name='members', on_delete=models.CASCADE)
    sexo = models.CharField(verbose_name="Sexo", max_length=50, choices=SEXO, default="NINGUNO",  null=True, blank=True)
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
    date_notified = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.identification} - {self.last_name} {self.first_name} {self.middle_name}"

    def get_name_prefix_suffix(self):
        return f"{self.name_prefix} {self.last_name} {self.first_name} {self.middle_name} {self.name_suffix}".strip()

    class Meta:
        verbose_name = 'Person Notificacion'
        verbose_name_plural = 'Person Notificaciones'
        ordering = ['identification']


class PrincipalCarrousel(ModeloBase):
    public = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='principal_carrousel/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Principal Carrousel'
        verbose_name_plural = 'Principal Carrousel'
        ordering = ['name']


TYPE_DOCUMENT = (
    (1, 'DOCX'),
    (2, 'PDF'),
    (3, 'ZIP'),
    (4, 'WEB'),
)


class CallForPapers(ModeloBase):
    public = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    icon = models.FileField(upload_to='icon_callforpapers/', null=True, blank=True)
    type_document = models.IntegerField(choices=TYPE_DOCUMENT)
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=500, null=True, blank=True)
    name_button = models.CharField(max_length=100, null=True, blank=True)
    file_example = models.FileField(upload_to='callforpapers/', null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Call For Papers'
        verbose_name_plural = 'Call For Papers'
        ordering = ['order']

    def get_image_by_type_document(self):
        if self.type_document == 1:
            return '/static/images/icons/doc.png'
        if self.type_document == 2:
            return '/static/images/icons/pdf.png'
        if self.type_document == 3:
            return '/static/images/icons/latex.png'
        if self.type_document == 4:
            return '/static/images/icons/file.png'
        return '/static/images/icons/file.png'


class FeesConference(ModeloBase):
    public = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    tax = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    applied_tax = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Fees Conference'
        verbose_name_plural = 'Fees Conference'
        ordering = ['order']

class FeesConferenceDetail(ModeloBase):
    public = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Fees Conference Detail'
        verbose_name_plural = 'Fees Conference Detail'
        ordering = ['order']
