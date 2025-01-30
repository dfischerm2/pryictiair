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

from core.metodos_de_pago import reversar_pago_paypal
from landing.models import InscripcionConference, PapersInscripcionConference, TopicsInscripcionConference
from seguridad.templatetags.templatefunctions import encrypt
from .models import Pedido, ESTADO_PEDIDO, METODO_PAGOS, HistorialPedido
import os

from django.db.models import Value, Count, Sum, F, FloatField
from django.db.models.functions import Coalesce

@login_required
@secure_module
@custom_atomic_request
def pedidoView(request):
    data = {
        'titulo': 'Pagos Online',
        'modulo': 'Pagos Online',
        'ruta': request.path,
        'fecha': str(date.today()),
    }
    addData(request, data)
    model = Pedido
    nombre_para_audit = '__str__'
    nombre_app, nombre_model = model._meta.app_label, model._meta.model_name
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
                            raise ValueError("Receipt has already been validated. Please reload the window to confirm.")
                        ht = HistorialPedido.objects.create(pedido_id=filtro.pk, detalle=request.POST['observacion'], estado=request.POST['estado'], user_id=request.user.pk, archivo=request.FILES.get('archivo'))
                        pedido.estado = ht.estado
                        pedido.save(request)
                        # correos_a_enviar = []
                        # subject = 'PAGO #{} {}'.format(pedido.id, pedido.get_estado_display())
                        # correos_a_enviar.append(
                        #     get_datos_email_html({
                        #         'titulo': f'Validación de Pago',
                        #         'url_compras': "/cursos-inscrito/id={}".format(get_encrypt(pedido.id)[1]), 'pedido': pedido,
                        #         "mensaje_correo": 'Tu transacción está con estado "{}".'.format(pedido.get_estado_display()),
                        #         "subject": subject,
                        #     }, pedido.user, subject,
                        #         'email/pago_validado.html')
                        # )
                        if pedido.estado == "COMPLETADO":
                            pedido.save(request)
                            papers_pedido = pedido.get_papers()
                            topics_pedido = pedido.get_topics_interest()
                            if InscripcionConference.objects.filter(status=True, persona=pedido.user, conference=pedido.cuota.conference).exists():
                                raise NameError("An enrollment for this conference has already been registered")
                            inscription_ = InscripcionConference(
                                pedido=pedido,
                                conference=pedido.cuota.conference,
                                persona=pedido.user,
                                fecha=date.today(),
                                role=pedido.cuota.role,
                                special_price=pedido.cuota.special_price,
                            )
                            inscription_.save(request)
                            if papers_pedido:
                                for paper in papers_pedido:
                                    paper_ = PapersInscripcionConference(cab=inscription_, idpaper=paper.idpaper, title=paper.title, sheets=paper.sheets)
                                    paper_.save(request)
                            if topics_pedido:
                                for topic in topics_pedido:
                                    topic_ = TopicsInscripcionConference(cab=inscription_, topic=topic.topic)
                                    topic_.save(request)
                            log(f'Inscripcion registrada {inscription_.__str__()}', request, 'add', obj=inscription_.id)
                        log(f"{pedido.__str__()}", request, "add",obj=pedido.id)
                        # for correo in correos_a_enviar:
                        #     enviar_correo_html(correo)
                        messages.success(request, "Transacción [{}] modificada correctamente.".format(customgetattr(filtro, nombre_para_audit)))
                        res_json.append({'error': False, "to": request.path + "?action=add" if '_add' in request.POST else request.path})
                    else:
                        res_json.append({'error': True,"message": "Error en el formulario" })
                elif action == 'reversar_pago':
                    filtro = Pedido.objects.get(id=int(request.POST['pk']), pago_reversado=False)
                    if filtro and request.user.is_superuser:
                        if filtro.metodo_pago == "PAYPAL":
                            comprobante = json.loads(filtro.comprobantejson)
                            response = reversar_pago_paypal(
                                comprobante["paypalCaptureId"],
                                comprobante["id"],
                            )
                        if response == True or (isinstance(response, dict) and response.get("status") == "COMPLETED"):
                            filtro.pago_reversado = True
                            filtro.fecha_reversado = timezone.now()
                            filtro.pago_reversado_por_id = request.user.id
                            filtro.razon_reverso = request.POST['razon_reverso']
                            # filtro.estado = "DEVUELTO"
                            filtro.save(request)
                        else:
                            raise ValueError("Hubo un error al reversar el pago de {} con ID {}".format(filtro.get_metodo_pago_display(), filtro.comprobante))

                        log(f"Reverso Pago {filtro.__str__()}", request, "change",obj=filtro.id)

                        HistorialPedido.objects.create(
                            pedido_id=filtro.id,
                            user_id=request.user.id,
                            estado="DEVUELTO",
                            archivo="",
                            detalle=f"Pago anulado, razón: {request.POST['razon_reverso']}"
                        )

                        messages.success(request, "Transacción [{}] reversado correctamente.".format(customgetattr(filtro, "__str__")))
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
                try:
                    pk = int(request.GET['pk'])
                    instancia = model.objects.get(pk=pk)
                    data["pk"] = pk
                    data["obj"] = instancia
                    data["compra"] = instancia
                    data["detallepapers"] = instancia.get_papers()
                    data["detalletopics"] = instancia.get_topics_interest()
                    return render(request, 'pedidos/pedido/pago_pendiente.html', data)
                except Exception as ex:
                    messages.success(request, ex)
                    return redirect(request.path)
            elif action == "historial_pedido":
                pk = int(get_decrypt(request.GET['pk'])[1])
                data['pedido'] = pedido = Pedido.objects.get(id=pk)
                data["historial"] = historial = HistorialPedido.objects.filter(status=True, pedido_id=pk).order_by('pk')
                template = get_template('pedidos/pedido/historial_pedido.html')
                return JsonResponse({"result": True, 'data': template.render(data), 'titulo': 'PAGO #{} - {}'.format(pk, pedido.user.get_full_name())})
            elif action == "anular_pedido":
                pk = int(get_decrypt(request.GET['pk'])[1])
                instancia = Pedido.objects.get(pk=pk)
                data["pk"] = pk
                data["compra"] = instancia
                return render(request, 'pedidos/pedido/anular_pedido.html', data)
            elif action == "reversar_pago":
                pk = int(get_decrypt(request.GET['pk'])[1])
                instancia = Pedido.objects.get(pk=pk)
                if request.user.is_superuser and instancia.es_pago_electronico and not instancia.pago_reversado:
                    data["pk"] = pk
                    data["compra"] = instancia
                    return render(request, 'pedidos/pedido/reversar_pago.html', data)
                else:
                    messages.success(request, f"Acción no permitida")
                    return redirect('/')

            elif action == "historial_pedido":
                try:
                    pk = int(get_decrypt(request.GET['pk'])[1])
                    data['pedido'] = pedido = Pedido.objects.get(id=pk)
                    data["historial"] = historial = HistorialPedido.objects.filter(status=True, pedido_id=pk).order_by('pk')
                    template = get_template('pedidos/pedido/historial_pedido.html')
                    return JsonResponse({"result": True, 'data': template.render(data), 'titulo': 'PAGO #{} - {}'.format(pk, pedido.user.get_full_name())})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})

            elif action == 'detailsRequest':
                try:
                    id = int(encrypt(request.GET['id']))
                    filtro = Pedido.objects.get(pk=id)
                    data['filtro'] = filtro
                    template = get_template("pedidos/solicitudes_inscripcion/details.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})

        id, criterio, fecha_desde, fecha_hasta, filtros, url_vars = request.GET.get('id', ''),  request.GET.get('criterio', '').strip(), request.GET.get('fecha_desde', ''),request.GET.get('fecha_hasta', ''), (Q(status=True)), ''
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
        try:
            listado = Pedido.objects.filter(filtros).exclude(estado__in=['PENDIENTE', 'RECHAZADO']).order_by('-pk')
            data["url_vars"] = url_vars
            data["pag"] = pag = 10
            paginador(request, listado, pag, data, url_vars)
            data['METODO_PAGOS'] = METODO_PAGOS
            data['ESTADO_PEDIDO'] = ESTADO_PEDIDO[2:]
            data["list_count"] = len(listado)
            data['totalreversado'] = totalreversado = listado.filter(pago_reversado=True).aggregate(total=Coalesce(Sum(F('total'), output_field=FloatField()), 0.0)).get('total')
            data['totalvalido'] = totalvalido = listado.filter(pago_reversado=False).aggregate(total=Coalesce(Sum(F('total'), output_field=FloatField()), 0.0)).get('total')
            data['totalrecaudado'] = totalrecaudado = listado.aggregate(total=Coalesce(Sum(F('total'), output_field=FloatField()), 0.0)).get('total')
            return render(request, 'pedidos/pedido/listado.html', data)
        except Exception as ex:
            messages.error(request, ex)
            return redirect(request.path)
