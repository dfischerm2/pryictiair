from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from area_geografica.models import Provincia, Pais, Ciudad
from autenticacion.models import Usuario, PerfilPersona
from autenticacion.recuperar_clave import generarclave
from core.email_config import send_html_mail
from core.funciones import addData, get_decrypt, generar_nombre, convertir_fecha_invertida, codnombre
from pryictiair import settings

from seguridad.models import *


def registro(request):
    data = {'titulo': 'Registro', 'url_auth':True}
    addData(request, data)
    if request.method == 'POST':
        with transaction.atomic():
            try:
                if not 'terminoscondiciones' in request.POST:
                    raise ValueError("Para continuar, debe aceptar los términos y condiciones & políticas de privacidad.")
                if Usuario.objects.filter(email=request.POST['email'], status=True, is_active=True).exists():
                    raise ValueError("Correo electrónico ya se encuentra en uso por otro usuario..")
                if Usuario.objects.filter(documento=request.POST['documento'], status=True, is_active=True).exists():
                    raise ValueError("Número de identidad ya se encuentra en uso por otro usuario..")
                else:
                    correo_, password_ = request.POST['email'], request.POST['documento']
                    nombre_, apellido_ = request.POST['first_name'], request.POST['last_name']
                    telefono_ = request.POST['telefono']
                    # lugartrabajo_, posicionlaboral_ = request.POST['lugartrabajo'], request.POST['posicionlaboral']
                    # fecha_nacimiento_ = request.POST['fecha_nacimiento']
                    # anio_nacimiento, anio_actual = convertir_fecha_invertida(request.POST['fecha_nacimiento']).year, datetime.now().year
                    # if (anio_actual - anio_nacimiento) < 18:
                    #     raise ValueError("Acción no permitida, debe ser mayor de edad para completar el registro de usuario.")
                    # fecha_nacimiento_ = datetime.now() - timedelta(days=int(request.POST["edad_registro"])*365)
                    ciudad_ = Ciudad.objects.get(id=request.POST['ciudad'])
                    username_ = codnombre(nombre_, apellido_)
                    tpdocumento = "PASAPORTE"
                    if len(tpdocumento) == 10:
                        tpdocumento = "CEDULA"
                    if len(tpdocumento) == 13:
                        tpdocumento = "RUC"
                    usuario_ = Usuario.objects.create_user(username=username_, first_name=nombre_, last_name=apellido_,
                                                           telefono=telefono_, tipo_documento=tpdocumento, ciudad=ciudad_,
                                                           sexo='NINGUNO', email=correo_, password=password_, documento=password_, is_active=True, is_staff=False, is_superuser=False)
                    perfil_ = PerfilPersona.objects.create(usuario=usuario_)
                    perfil_.save()
                    datos = {
                        'sucursal': request.config.nombre_empresa,
                        'instancia': usuario_,
                        'url': f'{data["DOMINIO_DEL_SISTEMA"]}',
                        'correo': str(settings.EMAIL_HOST_USER)
                    }
                    subject = f'¡Registro completado!'
                    to = correo_
                    send_html_mail(subject, "email/registro_usuario.html", datos, [to], [], [])
                    messages.success(request, 'Registro completado, revise su bandeja de correo electronico para obtener sus credenciales de acceso.')
                    user = authenticate(username=username_, password=password_)
                    if user is not None:
                        login(request, user)
                        su = SessionUser.nuevo(request)
                    response = JsonResponse({'respuesta': True, 'to': request.POST.get('next') or '/'})
                    return HttpResponse(response.content)
            except ValueError as ex:
                transaction.set_rollback(True)
                response = JsonResponse({'respuesta': False, 'mensaje': str(ex)})
                return HttpResponse(response.content)
            except Exception as ex:
                transaction.set_rollback(True)
                response = JsonResponse({'respuesta': False, "mensaje": f"Intente nuevamente. {ex}"})
                return HttpResponse(response.content)
    elif request.method == 'GET':
        des, data['next'] = get_decrypt(request.GET.get('next'))
        if not des:
            data['next'] = request.GET.get('next')
        if request.user.username != "":
            return redirect('/')
        return render(request, 'public/seguridad/registrarse.html', data)