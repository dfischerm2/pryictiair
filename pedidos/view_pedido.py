import json
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.utils import timezone

from core.correos_background import enviar_correo_html
from core.custom_models import FormError
from core.decoradores import custom_atomic_request
from core.email_config import send_html_mail
from core.funciones import addData, paginador, salva_auditoria, redirectAfterPostGet, secure_module, get_decrypt, \
    get_datos_email_html, get_encrypt, log
from core.funciones_adicionales import customgetattr
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from seguridad.templatetags.templatefunctions import encrypt
from .forms import ValidateRequestInscriptionForm
from .models import Pedido, ESTADO_PEDIDO, METODO_PAGOS, HistorialPedido
import os

from django.db.models import Value, Count, Sum, F, FloatField
from django.db.models.functions import Coalesce

@login_required
@secure_module
@custom_atomic_request
def solicitudesRegistroView(request):
    data = {
        'titulo': 'Solicitudes de registro',
        'modulo': 'Pedidos',
        'ruta': request.path,
        'fecha': str(date.today()),
    }
    addData(request, data)
    model = Pedido
    persona = request.user
    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'validateRequest':
                    filtro = Pedido.objects.get(pk=int(request.POST['pk']))
                    form = ValidateRequestInscriptionForm(request.POST)
                    if not form.is_valid():
                        raise FormError(form)
                    estado, observacion = form.cleaned_data['estado'], form.cleaned_data['observacion']
                    isStudent = filtro.cuota.role == 3 and filtro.special_price_student
                    estado_ = (('PENDIENTE_PAGO' if estado == '1' else 'RECHAZADO') if not isStudent else 'COMPLETADO' if estado == '1' else 'RECHAZADO')
                    filtro.estado = estado_
                    filtro.observacion = observacion
                    filtro.save(request)
                    historial_ = HistorialPedido(pedido=filtro,user=persona, estado=estado_, detalle=observacion)
                    historial_.save(request)
                    user_ =  filtro.user
                    datos = {
                        'user': user_,
                        'conference': filtro.cuota.conference,
                        'payment_link': f'',
                        'confi': data['confi'],
                        'observacion': observacion,
                        'estado': estado,
                        'filtro': filtro,
                        'isStudent': isStudent
                    }
                    subject = f'Validation of Your Registration Request for: {filtro.cuota.conference.title}'
                    # to = user_.email
                    to = 'cozjosue0@gmail.com'
                    send_html_mail(subject, "email/validacion_inscripcion.html", datos, [to], [], [])
                    log(f"Validó la solicitud de inscripción {filtro.__str__()}", request, "change", obj=filtro.id)
                    messages.success(request, "Solicitud validada con éxito")
                    res_json.append({'error': False, "reload": True})
        except ValueError as ex:
            res_json.append({'error': True, "message": str(ex)})
        except FormError as ex:
            res_json.append(ex.dict_error)
        except Exception as ex:
            res_json.append({'error': True, "message": f"Intente nuevamente {ex}"})
        return JsonResponse(res_json, safe=False)
    elif request.method == 'GET':
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']

            if action == 'detailsRequest':
                try:
                    id = int(encrypt(request.GET['id']))
                    filtro = Pedido.objects.get(pk=id)
                    data['filtro'] = filtro
                    template = get_template("pedidos/solicitudes_inscripcion/details.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})

            if action == 'validateRequest':
                try:
                    id = int(encrypt(request.GET['id']))
                    filtro = Pedido.objects.get(pk=id)
                    form = ValidateRequestInscriptionForm()
                    data['filtro'] = filtro
                    data['form'] = form
                    template = get_template("pedidos/solicitudes_inscripcion/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})

            elif action == "historial_pedido":
                try:
                    pk = int(get_decrypt(request.GET['pk'])[1])
                    data['pedido'] = pedido = Pedido.objects.get(id=pk)
                    data["historial"] = historial = HistorialPedido.objects.filter(status=True, pedido_id=pk).order_by('pk')
                    template = get_template('pedidos/pedido/historial_pedido.html')
                    return JsonResponse({"result": True, 'data': template.render(data), 'titulo': 'PAGO #{} - {}'.format(pk, pedido.user.get_full_name())})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})

        id, criterio, fecha_desde, fecha_hasta, filtros, url_vars = request.GET.get('id', ''), request.GET.get(
            'criterio', '').strip(), request.GET.get('fecha_desde', ''), request.GET.get('fecha_hasta', ''), Q(status=True, estado__in=['PENDIENTE', 'RECHAZADO']), ''
        metodopago, estado = request.GET.get('metodopago', '').strip(), request.GET.get('estado', '').strip()
        if criterio:
            filtros = filtros & (Q(user__first_name__icontains=criterio) | Q(user__last_name__icontains=criterio))
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio
        if metodopago:
            filtros = filtros & (Q(metodopago=metodopago))
            data["metodopago"] = metodopago
            url_vars += '&metodopago=' + metodopago
        if estado:
            filtros = filtros & (Q(estado=estado))
            data["estado"] = estado
            url_vars += '&estado=' + estado
        if fecha_desde:
            filtros = filtros & Q(fecha_registro__gte=fecha_desde)
            data["fecha_desde"] = fecha_desde
            url_vars += '&fecha_desde=' + fecha_desde
        if fecha_hasta:
            filtros = filtros & Q(fecha_registro__lte=fecha_hasta)
            data["fecha_hasta"] = fecha_hasta
            url_vars += '&fecha_hasta=' + fecha_hasta
        if id:
            filtros = filtros & Q(id=id)
            data["id"] = id
            url_vars += f'&id={id}'
        listado = Pedido.objects.filter(filtros).order_by('-pk')
        data["url_vars"] = url_vars
        data["pag"] = pag = 10
        paginador(request, listado, pag, data, url_vars)
        data['ESTADO_PEDIDO'] = ESTADO_PEDIDO[0:2]
        data["list_count"] = len(listado)
        return render(request, 'pedidos/pedido/listado.html', data)
