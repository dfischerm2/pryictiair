import os
import time
from decimal import Decimal

from django.core import mail
from django.db.models import Q
from django.http import JsonResponse
from django.template.loader import render_to_string, get_template
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.html import strip_tags
from core.funciones import addData, salva_auditoria, secure_module, generar_nombre, paginador
from autenticacion.models import Usuario
from datetime import timedelta, datetime

from landing.models import InscripcionConference, Conference, ScheduleConference
from pedidos.models import Pedido, HistorialPedido
from seguridad.templatetags.templatefunctions import encrypt


@login_required
def completePurchaseView(request):
    data = {
        'titulo': "Complete purchase",
        'modulo': 'Complete purchase',
        'ruta': request.path,
    }
    addData(request, data)

    if request.method == 'POST':
        res_json = []
        if 'action' in request.POST:
            action = request.POST['action']
            try:
                with transaction.atomic():
                    pass



            except ValueError as e:
                messages.error(request, str(e))
            except Exception as ex:
                res_json.append({"error": True, "message": ex})
            return JsonResponse(res_json, safe=False)
    elif request.method == 'GET':
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            pass
        try:
            orderid = request.GET.get('order', None)
            if not orderid:
                messages.error(request, 'Order not found')
                return redirect('/')
            order = Pedido.objects.get(pk=int(encrypt(orderid)))
            data['order'] = order
            subtotal_aplicable = float(order.subtotal)
            data['subtotal_aplicable'] = subtotal_aplicable
            data['impuesto_pago_online'] = impuesto_pago_online = round(float(subtotal_aplicable * float((data['confi'].porcentaje_pagoonline / Decimal('100')))), 2) if data['confi'].porcentaje_pagoonline else 0
            data['total'] = total_ = subtotal_aplicable + impuesto_pago_online
            return render(request, 'public/complete_purchase/view.html', data)
        except Exception as e:
            messages.error(request, str(e))
            return redirect('/')
