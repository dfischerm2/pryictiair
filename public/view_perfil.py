import os
import time
from django.core import mail
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.template.loader import render_to_string, get_template
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.html import strip_tags

from area_geografica.models import Provincia, Pais
from core.custom_forms import FormError
from core.funciones import addData, salva_auditoria, secure_module, generar_nombre, paginador, log, get_client_ip
from autenticacion.models import Usuario
from datetime import timedelta, datetime, date

from financiero.forms import PagoTransferenciaForm
from landing.models import InscripcionConference, Conference, ScheduleConference, DetailScheduleConference
from pedidos.models import Pedido, HistorialPedido
from public.forms import RegistroPersonaForm, EditProfileForm
from seguridad.templatetags.templatefunctions import encrypt


@login_required
def myProfileView(request):
    data = {
        'titulo': "Profile",
        'modulo': 'Profile',
        'ruta': request.path,
    }
    addData(request, data)
    persona = request.user

    if request.method == 'POST':
        res_json = []
        if 'action' in request.POST:
            action = request.POST['action']
            try:
                with transaction.atomic():

                    if action == 'changeperfil':
                        usuario = Usuario.objects.get(pk=int(request.user.pk))
                        usuario.first_name = request.POST['first_name']
                        usuario.last_name = request.POST['last_name']
                        usuario.telefono = request.POST['telefono']
                        usuario.ciudad_id =  request.POST['ciudad']
                        fecha_nacimiento_ = request.POST["fechanacimiento"]
                        usuario.fecha_nacimiento = fecha_nacimiento_
                        usuario.save()
                        messages.success(request, 'Información de perfil actualizada')
                        res_json.append({'error': False, "to": request.path})

                    elif action == 'changepass':
                        try:
                            usuario = Usuario.objects.get(pk=int(request.user.pk))
                            user_login = authenticate(username=usuario.username, password=request.POST['clave_actual'])
                            if user_login is not None:
                                if request.POST['clave_actual'] != request.POST['clave']:
                                    user_login.set_password(request.POST['clave'])
                                    user_login.save()
                                    messages.success(request, 'Contraseña cambiada satisfactoriamente.')
                                    res_json.append({'error': False, "to": f'{request.path}?action=changepass'})
                                else:
                                    res_json.append({"error": True, "message": 'La contraseña nueva debe ser diferente a la contraseña actual'})
                                    return JsonResponse(res_json, safe=False)
                            else:
                                res_json.append({"error": True, "message": 'Contraseña actual incorrecta'})
                                return JsonResponse(res_json, safe=False)
                        except ValueError as e:
                            messages.error(request, str(e))
                        except Exception as ex:
                            res_json.append({"error": True, "message": ex})
                        return JsonResponse(res_json, safe=False)

                    elif action == 'saveAttendance':
                        filtro = InscripcionConference.objects.get(pk=int(encrypt(request.POST['idinscripcion'])))
                        cronograma = DetailScheduleConference.objects.get(pk=int(encrypt(request.POST['iddetail'])))
                        if filtro and cronograma:
                            if not filtro.asistio:
                                filtro.asistio = True
                                filtro.fecha_asistencia = date.today()
                                filtro.save(request)
                                log(f"Registro de asistencia para {filtro.__str__()}", request, "change")
                            res_json.append({'error': False, "url": f'{cronograma.link}'})
                        else:
                            raise NameError('Something went wrong. Contact the administrator for assistance.')
                    elif action == 'cargar_comprobante_paypal':
                        pedido = Pedido.objects.get(pk=int(request.POST['pk']))
                        form = PagoTransferenciaForm(request.POST, request.FILES)
                        if not form.is_valid():
                            raise FormError(form)
                        if not 'archivo' in request.FILES:
                            raise NameError("You must upload a file")
                        newfile = request.FILES['archivo']
                        extension = newfile._name.split('.')
                        tam = len(extension)
                        exte = extension[tam - 1]
                        if newfile.size > 4194304:
                            raise NameError(f"Error: The file size exceeds 4 MB.")
                        if exte in ['pdf',]:
                            newfile._name = generar_nombre("order_", newfile._name)
                        else:
                            raise NameError(f"Error: Only .pdf files are allowed.")
                        pedido.ip = get_client_ip(request)
                        pedido.modo_pago = True
                        pedido.metodo_pago = 'PAYPAL'
                        pedido.archivo_pago = newfile
                        pedido.estado = "EN_ESPERA"
                        pedido.total = pedido.subtotal
                        pedido.save(request)
                        historial_ = HistorialPedido(pedido=pedido, user=pedido.user, estado='EN_ESPERA', detalle='PayPal payment receipt uploaded ', archivo=newfile)
                        historial_.save(request)
                        log(f"Payment by bank transfer for order {pedido.__str__()}", request, "add", obj=pedido.id)
                        messages.success(request,f"Your order has been completed, and your payment is currently under review, once your payment receipt has been validated, you will receive an email with the details . Please check your SPAM FOLDER if you dont see it in your inbox")
                        res_json.append({'error': False, "to": '/profile/?action=payments'})
                    elif action == 'editprofile':
                        form = EditProfileForm(request.POST, request.FILES)
                        if form.is_valid():
                            persona.pais = form.cleaned_data['pais']
                            persona.institucion = form.cleaned_data['institucion']
                            persona.save(request)
                            log(f"Edito el perfil de {request.user.__str__()}", request, "change", obj=request.user.id)
                            messages.success(request, "Profile edited successfully")
                            res_json.append({'error': False, "reload": True})
                        else:
                            raise FormError(form)
            except ValueError as ex:
                res_json.append({'error': True, "message": str(ex)})
            except FormError as ex:
                res_json.append(ex.dict_error)
            except Exception as ex:
                res_json.append({'error': True, "message": f"Something went wrong: {ex}"})
            return JsonResponse(res_json, safe=False)
    elif request.method == 'GET':
        if 'action' in request.GET:
            data['action'] = action = request.GET['action']
            if action == 'changepass':
                data['titulo'] = 'Cambiar Contraseña'
                data['viewprofile'] = 4
                return render(request, 'public/perfil/changepass.html', data)
            elif action == 'payments':
                try:
                    # filtros, url_vars = Q(status=True), f'&action={action}'
                    filtros, url_vars = Q(status=True, user=persona), f'&action={action}'
                    data['title'] = 'My orders'
                    listado = Pedido.objects.filter(filtros)
                    data["list_count"] = listado.count()
                    data["url_vars"] = url_vars
                    data['viewprofile'] = 3
                    paginador(request, listado.order_by('-id'), 10, data, url_vars)
                    return render(request, 'public/perfil/orders/view_payments.html', data)
                except Exception as ex:
                    messages.error(request, ex)
                    return redirect(request.path)
            elif action == "historial_pedido":
                try:
                    pk = int(encrypt(request.GET['id']))
                    data['pedido'] = pedido = Pedido.objects.get(id=pk)
                    data["historial"] = historial = HistorialPedido.objects.filter(status=True, pedido_id=pk).order_by('pk')
                    template = get_template('public/perfil/orders/modal_historial.html')
                    return JsonResponse({"result": True, 'data': template.render(data), 'titulo': 'PAGO #{} - {}'.format(pk, pedido.user.get_full_name())})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})
            elif action == 'detailsRequest':
                try:
                    id = int(encrypt(request.GET['id']))
                    filtro = Pedido.objects.get(pk=id)
                    data['filtro'] = filtro
                    template = get_template("public/perfil/orders/modal_detalle.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})
            elif action == 'inscriptions':
                try:
                    # filtros, url_vars = Q(status=True), f'&action={action}'
                    filtros, url_vars = Q(status=True, persona=persona), f'&action={action}'
                    data['title'] = 'My Inscriptions'
                    listado = InscripcionConference.objects.filter(filtros)
                    data["list_count"] = listado.count()
                    data["url_vars"] = url_vars
                    data['viewprofile'] = 2
                    paginador(request, listado.order_by('-id'), 10, data, url_vars)
                    return render(request, 'public/perfil/inscriptions/view.html', data)
                except Exception as ex:
                    messages.error(request, ex)
                    return redirect(request.path)
            elif action == 'schedule':
                try:
                    filtro = InscripcionConference.objects.get(pk=int(encrypt(request.GET['id'])))
                    data['filtro'] = filtro
                    conference = filtro.conference
                    filtros, url_vars = Q(status=True, conference=conference, published=True), f'&action={action}'
                    data['atras'] = f'?action=inscriptions'
                    data['title'] = f'Schedule - {conference.title}'
                    listado = ScheduleConference.objects.filter(filtros).order_by('order')
                    data['listado'] = listado
                    data['viewprofile'] = 2
                    return render(request, 'public/perfil/inscriptions/schedule.html', data)
                except Exception as ex:
                    messages.error(request, ex)
                    return redirect(request.path)
            elif action == 'paperslist':
                try:
                    id = int(encrypt(request.GET['id']))
                    filtro = InscripcionConference.objects.get(pk=id)
                    data['filtro'] = filtro
                    template = get_template("public/perfil/orders/papers_list.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})
            elif action == 'cargar_comprobante_paypal':
                try:
                    id = int(encrypt(request.GET['id']))
                    filtro = Pedido.objects.get(pk=id)
                    form = PagoTransferenciaForm()
                    data['filtro'] = filtro
                    data['form'] = form
                    template = get_template("public/complete_purchase/modal_transferencia.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})
            elif action == 'editprofile':
                try:
                    form = EditProfileForm(initial=model_to_dict(persona))
                    data['form'] = form
                    template = get_template("public/perfil/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({'result': False, 'message': f"{ex}"})
    data['fecha_nacimiento'] = str(request.user.fecha_nacimiento)
    data['viewprofile'] = 1
    return render(request, 'public/perfil/perfil.html', data)
