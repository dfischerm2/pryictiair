from decimal import Decimal
from django.http import JsonResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect

from core.custom_forms import FormError
from core.funciones import addData, generar_nombre, get_client_ip, log

from financiero.forms import PagoTransferenciaForm
from financiero.models import CuentaFinancieraEmpresa
from pedidos.models import Pedido, HistorialPedido, INVOICE_OPTIONS, PagoTransferencia
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
                    if action == 'pago_transferencia':
                        pedido = Pedido.objects.get(pk=int(request.POST['pk']))
                        cuentaBancaria = CuentaFinancieraEmpresa.objects.get(pk=int(request.POST['cuenta_id']))
                        form = PagoTransferenciaForm(request.POST, request.FILES)
                        if not form.is_valid():
                            raise FormError(form)
                        if not cuentaBancaria:
                            raise NameError("Error: Bank account not found")
                        if not 'archivo' in request.FILES:
                            raise NameError("You must upload a file")
                        newfile = request.FILES['archivo']
                        extension = newfile._name.split('.')
                        tam = len(extension)
                        exte = extension[tam - 1]
                        if newfile.size > 4194304:
                            raise NameError(f"Error: The file size exceeds 4 MB.")
                        if exte in ['jpg', 'jpeg', 'png', 'jpeg']:
                            newfile._name = generar_nombre("order_", newfile._name)
                        else:
                            raise NameError(f"Error: Only .png, .jpg, and .jpeg files are allowed.")
                        billing_info = request.POST.get('billing_info', None)
                        if billing_info == 'true':
                            billing_name = request.POST.get('billing_name', None)
                            billing_email = request.POST.get('billing_email', None)
                            billing_phone = request.POST.get('billing_phone', None)
                            billing_tax_id = request.POST.get('billing_tax_id', None)
                            billing_address = request.POST.get('billing_address', None)
                            if not all([billing_name, billing_email, billing_tax_id, billing_address]):
                                raise NameError("Error: You must complete all the required fields for invoicing.")
                        else:
                            billing_name = pedido.user.datos()
                            billing_phone = ''
                            billing_tax_id = ''
                            billing_email = pedido.user.email
                            billing_address = pedido.user.pais.__str__()
                        pedido.billing_tax_id = billing_tax_id
                        pedido.billing_company_name = billing_name
                        pedido.billing_email_address = billing_email
                        pedido.billing_phone = billing_phone
                        pedido.billing_address = billing_address
                        pedido.ip = get_client_ip(request)
                        pedido.modo_pago = True
                        pedido.entidad_fin = cuentaBancaria
                        pedido.archivo_pago = newfile
                        pedido.estado = "EN_ESPERA"
                        pedido.total = pedido.subtotal
                        observaciones = request.POST.get('observacion', '')
                        if observaciones:
                            pedido.observacion = observaciones
                        pedido.save(request)
                        PagoTransferencia.objects.create(
                            modelo=pedido,
                            infobanco="Banco {}, con tipo de cuenta {} número {}".format(
                                pedido.entidad_fin.ent_fin.nombre, pedido.entidad_fin.get_tipo_display(),
                                pedido.entidad_fin.num_cuenta),
                            infopersona="{}: {}, {} email: {}".format(pedido.entidad_fin.get_tipo_documento_display(),
                                                                      pedido.entidad_fin.documento,
                                                                      pedido.entidad_fin.nombres,
                                                                      pedido.entidad_fin.email)
                        )
                        historial_ = HistorialPedido(pedido=pedido, user=pedido.user, estado='EN_ESPERA', detalle=observaciones if observaciones else 'Payment by bank transfer', archivo=newfile)
                        historial_.save(request)
                        log(f"Payment by bank transfer for order {pedido.__str__()}", request, "add", obj=pedido.id)
                        messages.success(request,f"Your order has been completed, and your payment is currently under review. Once your payment receipt has been validated, a notification will be sent to the email address associated with your account.")
                        res_json.append({'error': False, "to": '/profile/?action=payments'})
            except ValueError as ex:
                res_json.append({'error': True, "message": str(ex)})
            except FormError as ex:
                res_json.append(ex.dict_error)
            except Exception as ex:
                res_json.append({'error': True, "message": f"{ex}"})
            return JsonResponse(res_json, safe=False)
    elif request.method == 'GET':
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']

            if action == 'pago_transferencia':
                try:
                    id = int(encrypt(request.GET['id']))
                    filtro = Pedido.objects.get(pk=id)
                    form = PagoTransferenciaForm()
                    data['cuenta_id'] = request.GET.get('cuenta_id', None)
                    data['filtro'] = filtro
                    data['form'] = form
                    template = get_template("public/complete_purchase/modal_transferencia.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})
        try:
            orderid = request.GET.get('order', None)
            if not orderid:
                raise NameError("Error: Order not found")
            order = Pedido.objects.get(pk=int(encrypt(orderid)))
            if order.estado == 'EN_ESPERA':
                messages.error(request, 'Your order is currently under review, please wait for confirmation.')
                return redirect('/profile/?action=payments')
            if order.estado != 'PENDIENTE_PAGO':
                messages.error(request, 'Order not available for payment.')
                return redirect('/profile/?action=payments')
            data['order'] = order
            subtotal_aplicable = float(order.subtotal)
            data['subtotal_aplicable'] = subtotal_aplicable
            data['impuesto_pago_online'] = impuesto_pago_online = round(float(subtotal_aplicable * float((data['confi'].porcentaje_pagoonline / Decimal('100')))), 2) if data['confi'].porcentaje_pagoonline else 0
            data['total'] = total_ = subtotal_aplicable + impuesto_pago_online
            data['INVOICE_OPTIONS'] = INVOICE_OPTIONS
            data['cuentas_bancarias'] = CuentaFinancieraEmpresa.objects.filter(status=True)
            return render(request, 'public/complete_purchase/view.html', data)
        except Exception as e:
            messages.error(request, str(e))
            return redirect('/')
