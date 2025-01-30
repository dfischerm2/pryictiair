from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from core.custom_models import FormError
from core.funciones import addData, paginador, secure_module
from core.generacion_certificados import preview_certificado

from landing.models import InscripcionConference, ROLES_FEE_CHOICE
from seguridad.templatetags.templatefunctions import encrypt


@login_required
@secure_module
def inscripcionesView(request):
    data = {
        'titulo': 'Inscripciones',
        'modulo': 'Landing',
        'ruta': request.path,
        'fecha': str(date.today())
    }
    addData(request, data)
    conference = request.session['conference']
    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
               if action == 'preview_certificado':
                    filtro = InscripcionConference.objects.get(pk=int(request.POST['id']))
                    if not filtro:
                        raise ValueError("No se encontró el registro")
                    error, result = preview_certificado(request, filtro.id)
                    if not error:
                        raise NameError(result)
                    return result
        except ValueError as ex:
            res_json.append({'error': True, "message": str(ex)})
        except FormError as ex:
            res_json.append(ex.dict_error)
        except Exception as ex:
            res_json.append({'error': True, "message": f"Intente Nuevamente: {ex}"})
        return JsonResponse(res_json, safe=False)
    elif request.method == 'GET':
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']
            pass
        id, criterio, filtros, url_vars = request.GET.get('id', '').strip(), request.GET.get('criterio', '').strip(), Q(status=True, conference=conference), ''
        rolid = request.GET.get('rolid', '')
        if id:
            filtros = filtros & (Q(id=id))
            data["id"] = id
            url_vars += '&id=' + id
        if criterio:
            filtros = filtros & (Q(persona__first_name__icontains=criterio) | Q(persona__last_name__icontains=criterio) | Q(persona__email__icontains=criterio))
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio
        if rolid:
            filtros = filtros & (Q(role=rolid))
            data["rolid"] = rolid
            url_vars += '&rolid=' + rolid
        try:
            listado = InscripcionConference.objects.filter(filtros)
            data["list_count"] = listado.count()
            data["url_vars"] = url_vars
            data['ROLES_FEE_CHOICE'] = ROLES_FEE_CHOICE
            paginador(request, listado.order_by('-id'), 20, data, url_vars)
            return render(request, 'autenticacion/inscripciones/listado.html', data)
        except Exception as ex:
            messages.error(request, f"Error: {ex}")
            return redirect(request.path)