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
    data = {
        'titulo': 'Inicio',
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
        if not VisitaEntorno.objects.filter(fecha_visita=datetime.now().date(),
                                            ip=ipresult, dispositivo=dispositivo).exists():
            if not request.user.is_authenticated:
                VisitaEntorno.objects.create(fecha_visita=datetime.now().date(), ip=ipresult, hora_visita=datetime.now().time(),
                                             dispositivo=dispositivo)
            else:
                VisitaEntorno.objects.create(fecha_visita=datetime.now().date(), ip=ipresult, hora_visita=datetime.now().time(), user_id=request.user.pk,
                                             dispositivo=dispositivo)


        return render(request, 'public/landing/landing.html', data)
