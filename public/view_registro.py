import json
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template

from area_geografica.models import Pais
from autenticacion.models import Usuario, PerfilPersona
from core.custom_models import FormError
from core.email_config import send_html_mail
from core.funciones import addData, paginador, secure_module, log, generar_nombre, validate_email_sponsor
from django.contrib import messages

from landing.forms import ConferenceForm
from landing.models import Conference, ConferenceFee, TopicCategory
from pedidos.models import Pedido, PapersAuthorPedido, TopicsAttendeePedido, HistorialPedido
from pryictiair.settings import ID_GRUPO_USUARIO, EXT_EMAILS_COLABORATORS, DEFAULT_PASSWORD_REGISTER
from public.forms import RegisterUserForm, StudentAttendeeForm
from seguridad.templatetags.templatefunctions import encrypt


def registerView(request):
    data = {
        'titulo': 'Registro',
        'modulo': 'Landing',
        'ruta': request.path,
        'fecha': str(date.today())
    }
    addData(request, data)
    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'create_order':
                    filtro = ConferenceFee.objects.get(id=encrypt(request.POST['pk']))
                    form = RegisterUserForm(request.POST, request.FILES)
                    if not form.is_valid():
                        raise FormError(form)
                    if not filtro:
                        raise NameError('Error trying to register')

                    first_name, last_name, email, country, institution = form.cleaned_data['first_name'].strip(), form.cleaned_data['last_name'].strip(), form.cleaned_data['email'].strip(), form.cleaned_data['country'], form.cleaned_data['institution'].strip()

                    if filtro.role == 1:
                        details = request.POST.get('papers', None)
                        if not details:
                            raise NameError('You must add at least 1 paper to be able to register your registration for the event')
                        details_ = json.loads(details)
                        if len(details_) == 0:
                            raise NameError('You must add at least 1 paper to be able to register your registration for the event')
                    elif filtro.role == 3 or filtro.special_price:
                        if not 'archivo_evidencia' in request.FILES:
                            if filtro.special_price:
                                raise NameError('You must upload a file verifying that you are a student or affiliated with one of the institutions promoting this event to complete your registration.')
                            else:
                                raise NameError('You must upload a file verifying that you are a student to complete your registration.')
                        if filtro.special_price:
                            if not validate_email_sponsor(email):
                                raise NameError('The email provided does not belong to a sponsor of the event. Please enter a valid email.')

                    new_user = False
                    qsUser = Usuario.objects.filter(email=email)
                    if not qsUser.exists():
                        user_ = Usuario.objects.create_user(username=email, first_name=first_name.upper(),last_name=last_name.upper(), email=email, password=DEFAULT_PASSWORD_REGISTER)
                        new_user = True
                    else:
                        user_ = qsUser.first()
                    user_.pais = country
                    user_.institucion = institution.upper() if institution else None
                    user_.is_active = True
                    user_.save()

                    if not PerfilPersona.objects.filter(usuario=user_).exists():
                        perfil_ = PerfilPersona.objects.create(usuario=user_)
                    else:
                        perfil_ = PerfilPersona.objects.filter(usuario=user_).first()
                    perfil_.status=True
                    perfil_.save()

                    grupo_ = Group.objects.get(pk=ID_GRUPO_USUARIO)
                    if not grupo_.user_set.filter(id=user_.id).exists():
                        grupo_.user_set.add(user_)
                        grupo_.save()

                    if new_user:
                        datos = {
                            'sucursal': request.config.nombre_empresa,
                            'instance': user_,
                            'url': f'{data["DOMINIO_DEL_SISTEMA"]}',
                            'correo': str(settings.EMAIL_HOST_USER),
                            'password': DEFAULT_PASSWORD_REGISTER
                        }
                        subject = f'¡Welcome to ICTIAIR – Registration Complete!'
                        to = user_.email
                        send_html_mail(subject, "email/registro_usuario.html", datos, [to], [], [])

                    if Pedido.objects.filter(user=user_, status=True, estado='PENDIENTE', cuota__conference=filtro.conference).exists():
                        raise NameError('You already have a pending request awaiting approval for this event.')
                    if Pedido.objects.filter(user=user_, status=True, estado='EN_ESPERA', cuota__conference=filtro.conference).exists():
                        raise NameError('You already have a pending payment for this event.')
                    if Pedido.objects.filter(user=user_, status=True, estado='COMPLETADO', cuota__conference=filtro.conference).exists():
                        raise NameError('You are already registered for this event.')

                    total_ = Decimal(request.POST['total_value'])

                    pedido = Pedido.objects.create(
                        user_id=user_.id,
                        estado="PENDIENTE",
                        subtotal=total_,
                        cuota=filtro
                    )

                    if filtro.role == 1:
                        details = json.loads(details)
                        for item in details:
                            PapersAuthorPedido.objects.create(pedido=pedido,idpaper=item['idpaper'],  title=item['title'], sheets=item['sheets'], value=item['value'])
                    else:
                        if filtro.role == 3 or filtro.special_price:
                            newfile = request.FILES['archivo_evidencia']
                            extension = newfile._name.split('.')
                            tam = len(extension)
                            exte = extension[tam - 1]
                            if newfile.size > 4194304:
                                raise NameError('The file size exceeds the 4 MB limit. Please upload a smaller file.')
                            if exte in ['pdf', 'jpg', 'jpeg', 'png', 'jpeg', 'peg']:
                                newfile._name = generar_nombre("pedido_", newfile._name)
                            else:
                                raise NameError('Error: Only files with the following extensions are allowed: .pdf, .jpg, .jpeg. Please upload a valid file.')

                            pedido.archivo_evidencia = newfile
                            pedido.special_price_student =  filtro.role == 3 and filtro.special_price

                    topics = request.POST.get('topics', [])
                    if topics:
                        topics = json.loads(topics)
                        for item in topics:
                            topic_ = TopicCategory.objects.get(id=item['id'])
                            TopicsAttendeePedido.objects.create(pedido=pedido, topic=topic_)

                    pedido.save()
                    historial_ = HistorialPedido(pedido=pedido, user=user_, estado='PENDIENTE', detalle=f'Conference registration request')
                    historial_.save()
                    datos = {
                        'filtro': pedido,
                        'user': user_,
                        'url': f'{data["DOMINIO_DEL_SISTEMA"]}',
                    }
                    subject = f'¡Order Received!'
                    to = user_.email
                    send_html_mail(subject, "email/pedido_recibido.html", datos, [to], [], [])
                    if not request.user.is_authenticated:
                        login(request, user_)
                    log(f"Registró pedido para evento {pedido.__str__()}", request, "add", obj=pedido.id, user=user_)
                    messages.success(request, f'Your registration has been successfully completed. You will receive an email with the details of your registration.')
                    res_json.append({'error': False, 'to': '/profile/?action=payments'})
        except ValueError as ex:
            res_json.append({'error': True, "message": str(ex)})
        except FormError as ex:
            res_json.append(ex.dict_error)
        except Exception as ex:
            res_json.append({'error': True, "message": f"{ex}"})
        return JsonResponse(res_json, safe=False)
    elif request.method == 'GET':
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']
            if action == 'buscarpais':
                try:
                    search = request.GET.get('q', '').strip()
                    queryset = Pais.objects.filter(status=True).order_by('nombre')
                    if search:
                        queryset = queryset.filter(nombre__icontains=search)
                    data = {"result": "ok", "results": [{"id": x.pk, "name": f"{x.__str__()}"} for x in queryset.distinct()[:10]]}
                    return JsonResponse(data)
                except Exception as ex:
                    data = {"result": "ok", "results": []}
                    return JsonResponse(data)

        id = request.GET.get('id', '')
        if not id:
            messages.error(request, 'Error trying to register')
            return redirect('/#section-register')
        id_ = encrypt(id)
        filtro = ConferenceFee.objects.get(id=id_)
        data['conference'] = filtro.conference
        data['filtro'] = filtro
        dict = {}
        if request.user.is_authenticated:
            dict['first_name'] = request.user.first_name
            dict['last_name'] = request.user.last_name
            dict['email'] = request.user.email
            dict['country'] = request.user.pais.id if request.user.pais else None
            dict['institution'] = request.user.institucion

        data['form'] = form = RegisterUserForm(initial=dict)
        if request.user.is_authenticated and request.user.pais:
            form.fields['country'].queryset = Pais.objects.filter(pk=request.user.pais.id)
        else:
            form.fields['country'].queryset = Pais.objects.none()



        return render(request, 'public/landing/register.html', data)
