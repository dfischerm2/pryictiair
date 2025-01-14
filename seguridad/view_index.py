from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import get_template

from django.db.models import Value, Count, Sum, F, FloatField
from django.db.models.functions import Coalesce
from autenticacion.models import PerfilPersona
from core.funciones import addData, secure_module
from landing.models import Conference
from public.models import VisitaEntorno
from seguridad.models import *
from seguridad.templatetags.templatefunctions import encrypt


@login_required
@secure_module
def index(request):
    data = {
        'titulo': 'Inicio',
        'modulo': 'Menu',
        'ruta': '/',
        'fecha': datetime.now(),
    }
    addData(request, data)

    if request.method == 'POST':
        action = request.POST['action']
        if action == 'changeconference':
            try:
                id_ = encrypt(request.POST['id'])
                request.session['conference'] = Conference.objects.filter(pk=id_, status=True).order_by('-id').first()
                response = JsonResponse({'resp': True}, safe=False)
            except Exception as ex:
                response = JsonResponse({'resp': False, 'mensaje': ex}, safe=False)
            return response
    elif request.method == 'GET':
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']

        rangofechas = []
        rangofechasstr = []
        fechadesde = datetime.now().date() - timedelta(days=15)
        fechahasta = datetime.now().date()
        for day in range((fechahasta - fechadesde).days + 1):
            fechafiltro = fechadesde + timedelta(days=day)
            rangofechas.append("{} {}".format((fechadesde + timedelta(days=day)).strftime("%d"), (fechadesde + timedelta(days=day)).strftime("%b")))
            rangofechasstr.append(str(fechafiltro))
        visita = VisitaEntorno.objects.filter(fecha_visita__gte=fechadesde).values('fecha_visita').annotate(total=Coalesce(Count('fecha_visita'), 0)).values_list('total', 'fecha_visita')
        data['rangofechas'] = rangofechas
        data['rangofechasstr'] = rangofechasstr
        data['ultimasvisitas'] = visita
        data['totalvisitas'] = totaltodos = VisitaEntorno.objects.filter(fecha_visita__gte=fechadesde).count()
        maxvisitasday = max(VisitaEntorno.objects.filter(fecha_visita__gte=fechadesde).values('fecha_visita').annotate(total=Coalesce(Count('fecha_visita'), 0)).values_list('total', flat=True))
        if maxvisitasday <= 5:
            maxvisitasday = 10
        data['maxvisitaday'] = maxvisitasday

        return render(request, 'seguridad/index.html', data)
