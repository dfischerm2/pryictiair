from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template

from area_geografica.models import Pais, Ciudad
from autenticacion.models import PerfilPersona

from pryictiair import settings
from core.email_config import send_html_mail
from core.funciones import addData, mi_paginador, get_decrypt, get_client_ip
from core.notificacion_config import enviar_not_push
from public.models import VisitaEntorno
from seguridad.models import *


def index(request):
    from landing.models import Summary, GuidelineType, TopicCategory, CommitteeCategory, SponsorCategory, ImportantDate, CallForPapers
    data = {
        'titulo': 'Landing page',
        'ruta': request.path,
        'fecha': datetime.now(),
    }
    addData(request, data)

    if request.method == 'POST':
        action = request.POST['action']
    elif request.method == 'GET':
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']

        # CONTADOR ENTORNO
        ipresult = get_client_ip(request)
        dispositivo = request.META['HTTP_USER_AGENT']
        summary = Summary.objects.filter(status=True, activo=True, public=True).order_by('-id').first()
        sponsors = SponsorCategory.objects.prefetch_related('sponsors').filter(status=True, public=True)
        importan_dates = ImportantDate.objects.filter(status=True, public=True)
        call_for_papers = CallForPapers.objects.filter(status=True, public=True)
        guidelines_by_type = GuidelineType.objects.prefetch_related('guidelines').filter(status=True, public=True)
        topics_by_category = TopicCategory.objects.prefetch_related('topics').filter(status=True, public=True)
        committe_principal = CommitteeCategory.objects.prefetch_related('members').filter(status=True, public=True, order=0).first()
        committe_all = CommitteeCategory.objects.prefetch_related('members').filter(status=True, public=True).exclude(order=0)
        if not VisitaEntorno.objects.filter(fecha_visita=datetime.now().date(),
                                            ip=ipresult, dispositivo=dispositivo).exists():
            if not request.user.is_authenticated:
                VisitaEntorno.objects.create(fecha_visita=datetime.now().date(), ip=ipresult,
                                             hora_visita=datetime.now().time(),
                                             dispositivo=dispositivo)
            else:
                VisitaEntorno.objects.create(fecha_visita=datetime.now().date(), ip=ipresult,
                                             hora_visita=datetime.now().time(), user_id=request.user.pk,
                                             dispositivo=dispositivo)

        data['summary'] = summary
        data['sponsor'] = sponsors
        data['importan_dates'] = importan_dates
        data['guidelines_by_type'] = guidelines_by_type
        data['topics_by_category'] = topics_by_category
        data['committe_principal'] = committe_principal
        data['committe_all'] = committe_all
        data['call_for_papers'] = call_for_papers

        return render(request, 'public/landing/landing.html', data)
        # return render(request, 'public/landing/landing_copy.html', data)


def index_copy(request):
    from landing.models import Summary, GuidelineType, TopicCategory, CommitteeCategory, SponsorCategory, ImportantDate, CallForPapers
    data = {
        'titulo': 'Landing page',
        'ruta': request.path,
        'fecha': datetime.now(),
    }
    addData(request, data)

    if request.method == 'POST':
        action = request.POST['action']
    elif request.method == 'GET':
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']

        # CONTADOR ENTORNO
        ipresult = get_client_ip(request)
        dispositivo = request.META['HTTP_USER_AGENT']
        summary = Summary.objects.filter(status=True, activo=True, public=True).order_by('-id').first()
        sponsors = SponsorCategory.objects.prefetch_related('sponsors').filter(status=True, public=True)
        importan_dates = ImportantDate.objects.filter(status=True, public=True)
        call_for_papers = CallForPapers.objects.filter(status=True, public=True)
        guidelines_by_type = GuidelineType.objects.prefetch_related('guidelines').filter(status=True, public=True)
        topics_by_category = TopicCategory.objects.prefetch_related('topics').filter(status=True, public=True)
        committe_principal = CommitteeCategory.objects.prefetch_related('members').filter(status=True, public=True, order=0).first()
        committe_all = CommitteeCategory.objects.prefetch_related('members').filter(status=True, public=True).exclude(order=0)
        if not VisitaEntorno.objects.filter(fecha_visita=datetime.now().date(),
                                            ip=ipresult, dispositivo=dispositivo).exists():
            if not request.user.is_authenticated:
                VisitaEntorno.objects.create(fecha_visita=datetime.now().date(), ip=ipresult,
                                             hora_visita=datetime.now().time(),
                                             dispositivo=dispositivo)
            else:
                VisitaEntorno.objects.create(fecha_visita=datetime.now().date(), ip=ipresult,
                                             hora_visita=datetime.now().time(), user_id=request.user.pk,
                                             dispositivo=dispositivo)

        data['summary'] = summary
        data['sponsor'] = sponsors
        data['importan_dates'] = importan_dates
        data['guidelines_by_type'] = guidelines_by_type
        data['topics_by_category'] = topics_by_category
        data['committe_principal'] = committe_principal
        data['committe_all'] = committe_all
        data['call_for_papers'] = call_for_papers

        # return render(request, 'public/landing/landing.html', data)
        return render(request, 'public/landing/landing_copy.html', data)

