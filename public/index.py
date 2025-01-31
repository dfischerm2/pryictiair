from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template

from area_geografica.models import Pais, Ciudad
from autenticacion.models import PerfilPersona
from landing.models import Conference, ConferenceFee

from pryictiair import settings
from core.email_config import send_html_mail
from core.funciones import addData, mi_paginador, get_decrypt, get_client_ip
from core.notificacion_config import enviar_not_push
from public.models import VisitaEntorno
from seguridad.models import *


def index(request):
    from landing.models import Summary, GuidelineType, TopicCategory, CommitteeCategory, SponsorCategory, ImportantDate, \
        CallForPapers
    data = {
        'titulo': 'Home',
        'ruta': request.path,
        'fecha': datetime.now(),
    }
    addData(request, data)
    confi_ = Configuracion.get_instancia()

    if request.method == 'POST':
        res_json = []
        try:
            action = request.POST['action']
            if action == 'send_mail':
                nombre, email, telefono, mensaje = request.POST['name'], request.POST['email'], request.POST['phone'], \
                    request.POST['message']
                datos = {
                    'sucursal': request.config.nombre_empresa,
                    'nombres': nombre,
                    'correo': email,
                    'telefono': telefono,
                    'mensaje': mensaje
                }
                to = confi_.email_notificacion
                subject = f"New Message Received from the 'Contact Us' Landing Page"
                send_html_mail(subject, "email/email_contactanos.html", datos, [to], [], [])
                messages.success(request, 'Your message has been sent successfully.')
                res_json.append({'error': False, 'reload': True})

        except Exception as ex:
            res_json.append({'error': True, "message": f"Sorry, error occured this time sending your message. {ex}"})
        return JsonResponse(res_json, safe=False)
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
        committe_principal = CommitteeCategory.objects.prefetch_related('members').filter(status=True, public=True,
                                                                                          order=0).first()
        committe_all = CommitteeCategory.objects.prefetch_related('members').filter(status=True, public=True).exclude(
            order=0)
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
    from landing.models import Summary, GuidelineType, TopicCategory, CommitteeCategory, SponsorCategory, ImportantDate, \
        CallForPapers, PrincipalCarrousel
    data = {
        'titulo': 'Home',
        'ruta': request.path,
        'fecha': datetime.now(),
    }
    addData(request, data)
    confi_ = Configuracion.get_instancia()

    if request.method == 'POST':
        res_json = []
        try:
            action = request.POST['action']
            if action == 'send_mail':
                nombre, email, telefono, mensaje = request.POST['name'], request.POST['email'], request.POST['phone'], \
                    request.POST['message']
                datos = {
                    'sucursal': request.config.nombre_empresa,
                    'nombres': nombre,
                    'correo': email,
                    'telefono': telefono,
                    'mensaje': mensaje
                }
                to = confi_.email_notificacion
                subject = f"New Message Received from the 'Contact Us' Landing Page"
                send_html_mail(subject, "email/email_contactanos.html", datos, [to], [], [])
                messages.success(request, 'Your message has been sent successfully.')
                res_json.append({'error': False, 'reload': True})

        except Exception as ex:
            res_json.append({'error': True, "message": f"Sorry, error occured this time sending your message. {ex}"})
        return JsonResponse(res_json, safe=False)
    elif request.method == 'GET':
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']

        # CONTADOR ENTORNO
        ipresult = get_client_ip(request)
        dispositivo = request.META['HTTP_USER_AGENT']
        conference = Conference.objects.filter(status=True, active=True).order_by('-active', '-end_date').first()
        summary = Summary.objects.filter(status=True, activo=True, public=True, conference=conference).order_by('-id').first()
        sponsors = SponsorCategory.objects.filter(status=True, public=True, conference=conference)
        importan_dates = ImportantDate.objects.filter(status=True, public=True, conference=conference)
        call_for_papers = CallForPapers.objects.filter(status=True, public=True, conference=conference)
        guidelines_by_type = GuidelineType.objects.filter(status=True, public=True, conference=conference)
        topics_by_category = TopicCategory.objects.filter(status=True, public=True, conference=conference)
        committe_principal = CommitteeCategory.objects.filter(status=True, public=True, order=0, conference=conference).first()
        committe_all = CommitteeCategory.objects.filter(status=True, public=True, conference=conference).exclude(order=0)
        carrousel = PrincipalCarrousel.objects.filter(status=True, public=True)
        fees = ConferenceFee.objects.filter(status=True, conference=conference, published=True).order_by('order')

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
        data['carrousel'] = carrousel
        data['fees'] = fees

        # return render(request, 'public/landing/landing.html', data)
        return render(request, 'public/landing/landing_copy.html', data)
