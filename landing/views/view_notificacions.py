import urllib

from django.shortcuts import render
from django.db.models import Q
from django.utils.dateformat import DateFormat
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from landing.models import PersonNotificacion
from core.funciones_adicionales import salva_logs, customgetattr
from core.custom_forms import FormError
from core.funciones import secure_module, log, paginador, addData, redirectAfterPostGet
from datetime import date


@login_required
@secure_module
def personNotificacionView(request):
    data = {
        'titulo': 'Personas Notificadas',
        'modulo': 'Notificaciones',
        'ruta': request.path,
        'fecha': str(date.today()),
    }

    model = PersonNotificacion

    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
    elif request.method == 'GET':
        addData(request, data)
        if 'action' in request.GET:
            pass
        else:
            # Filtros
            criterio = request.GET.get('criterio', '').strip()
            notified = request.GET.get('notified', '')
            url_vars = ''

            filtros = Q()

            # Filtrar por nombres, identificación (identification)
            if criterio:
                filtros = filtros & (
                        Q(first_name__icontains=criterio) |
                        Q(last_name__icontains=criterio) |
                        Q(middle_name__icontains=criterio) |
                        Q(identification__icontains=criterio) |
                        Q(prefered_name__icontains=criterio)
                )
                data['criterio'] = criterio
                url_vars += '&criterio=' + urllib.parse.quote(criterio) if criterio else ''

            # Filtrar por estado de notificación (notified)
            if notified:
                notified_bool = notified == '1'
                filtros = filtros & Q(notified=notified_bool)
                data['notified'] = notified
                url_vars += '&notified=' + urllib.parse.quote(notified)

            # Obtener listado filtrado
            listado = model.objects.filter(filtros)

            # Contar resultados
            data['list_count'] = listado.count()

            data['url_vars'] = url_vars
            # Paginación
            paginador(request, listado, 20, data, url_vars)

            return render(request, 'person_notificacion/listado.html', data)
