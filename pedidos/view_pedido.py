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
from core.funciones import addData, paginador, salva_auditoria, redirectAfterPostGet, secure_module, get_decrypt, \
    get_datos_email_html, get_encrypt, log
from core.funciones_adicionales import customgetattr
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Pedido, ESTADO_PEDIDO, METODO_PAGOS, HistorialPedido
import os

from django.db.models import Value, Count, Sum, F, FloatField
from django.db.models.functions import Coalesce

@login_required
@secure_module
@custom_atomic_request
def pedidoView(request):
    data = {
        'titulo': 'Solicitudes de registro',
        'modulo': 'Pedidos',
        'ruta': request.path,
        'fecha': str(date.today()),
    }
    addData(request, data)
    model = Pedido
    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'pago_pendiente':
                    filtro = model.objects.get(Q(estado="EN_ESPERA"), pk=int(request.POST['pk']))
                    if filtro:
                        pedido = Pedido.objects.get(id=filtro.id)
                        if not pedido.estado == "EN_ESPERA":
                            raise ValueError("Comprobante ya fue validado, recargue la ventana para confirmar'")
                        ht = HistorialPedido.objects.create(pedido_id=filtro.pk, detalle=request.POST['observacion'], estado=request.POST['estado'], user_id=request.user.pk, archivo=request.FILES.get('archivo'))
                        pedido.estado = ht.estado
                        pedido.save(request)
                        correos_a_enviar = []
                        subject = 'PAGO #{} {}'.format(pedido.id, pedido.get_estado_display())
                        correos_a_enviar.append(
                            get_datos_email_html({
                                'titulo': f'Validación de Pago',
                                'url_compras': "/cursos-inscrito/id={}".format(get_encrypt(pedido.id)[1]), 'pedido': pedido,
                                "mensaje_correo": 'Tu transacción está con estado "{}".'.format(pedido.get_estado_display()),
                                "subject": subject,
                            }, pedido.user, subject,
                                'email/pago_validado.html')
                        )
                        if pedido.estado == "COMPLETADO":
                            pedido.save(request)
                            det_ped = pedido.get_detalle()
                            for det in det_ped:
                                det.inscribir(request)
                        log(f"{pedido.__str__()}", request, "add",obj=pedido.id)
                        for correo in correos_a_enviar:
                            enviar_correo_html(correo)
                        messages.success(request, "Transacción [{}] modificada correctamente.".format(filtro.__str__()))
                        res_json.append({'error': False, "to": request.path + "?action=add" if '_add' in request.POST else request.path})
                    else:
                        res_json.append({'error': True,
                                         "message": "Error en el formulario"
                                         })
                elif action == 'anular_pedido':
                    filtro = Pedido.objects.get(id=int(request.POST['pk']))
                    if filtro and request.user.is_superuser:
                        filtro.estado = "ANULADO"
                        filtro.save(request)
                        for l in filtro.get_detalle():
                            l.retirar(request)
                        ht = HistorialPedido.objects.create(pedido_id=filtro.pk,
                                                            detalle=request.POST['detalle'],
                                                            estado="ANULADO", user_id=request.user.pk,
                                                            archivo=request.FILES.get('archivo'))
                        log(f"Anulo pedido {filtro.__str__()}", request, "change",obj=filtro.id)
                        messages.success(request, "Transacción [{}] anulada correctamente.".format(customgetattr(filtro, "__str__")))
                        res_json.append({'error': False, "to": request.path + "?action=add" if '_add' in request.POST else request.path})

                    else:
                        res_json.append({'error': True,
                                         "message": "Error en el formulario"
                                         })

        except Exception as ex:
            res_json.append({'error': True,
                             "message": f"Intente Nuevamente, {ex}"
                             })
        return JsonResponse(res_json, safe=False)
    elif request.method == 'GET':
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']
            if action == 'pago_pendiente':
                pk = int(request.GET['pk'])
                instancia = model.objects.get(pk=pk)
                data["pk"] = pk
                data["obj"] = instancia
                data["compra"] = instancia
                data["detallepedido"] = instancia.get_detalle()
                return render(request, 'venta/pedido/pago_pendiente.html', data)
            elif action == "historial_pedido":
                pk = int(get_decrypt(request.GET['pk'])[1])
                data['pedido'] = pedido = Pedido.objects.get(id=pk)
                data["historial"] = historial = HistorialPedido.objects.filter(status=True, pedido_id=pk).order_by('pk')
                template = get_template('venta/pedido/historial_pedido.html')
                return JsonResponse({"result": True, 'data': template.render(data), 'titulo': 'PAGO #{} - {}'.format(pk, pedido.user.get_full_name())})
                return render(request, 'venta/pedido/detalle.html', data)
            elif action == "anular_pedido":
                pk = int(get_decrypt(request.GET['pk'])[1])
                instancia = Pedido.objects.get(pk=pk)
                data["pk"] = pk
                data["compra"] = instancia
                return render(request, 'venta/pedido/anular_pedido.html', data)
            elif action == "reversar_pago":
                pk = int(get_decrypt(request.GET['pk'])[1])
                instancia = Pedido.objects.get(pk=pk)
                if request.user.is_superuser and instancia.es_pago_electronico and not instancia.pago_reversado:
                    data["pk"] = pk
                    data["compra"] = instancia
                    return render(request, 'venta/pedido/reversar_pago.html', data)
                else:
                    messages.success(request, f"Acción no permitida")
                    return redirect('/')

        id, criterio, fecha_desde, fecha_hasta, filtros, url_vars = request.GET.get('id', ''),  request.GET.get('criterio', '').strip(), request.GET.get('fecha_desde', ''),request.GET.get('fecha_hasta', ''), (Q(status=True) ), ''
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
        data['METODO_PAGOS'] = METODO_PAGOS
        data['ESTADO_PEDIDO'] = ESTADO_PEDIDO[1:]
        data["list_count"] = len(listado)
        # data['totalreversado'] = totalreversado = listado.filter(pago_reversado=True).aggregate(total=Coalesce(Sum(F('total'), output_field=FloatField()), 0)).get('total')
        # data['totalvalido'] = totalvalido = listado.filter(pago_reversado=False).aggregate(total=Coalesce(Sum(F('total'), output_field=FloatField()), 0)).get('total')
        # data['totalrecaudado'] = totalrecaudado = listado.aggregate(total=Coalesce(Sum(F('total'), output_field=FloatField()), 0)).get('total')
        return render(request, 'pedidos/pedido/listado.html', data)
