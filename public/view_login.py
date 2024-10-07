import base64
from django.contrib import messages
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.funciones import addData, ip_client_address, get_decrypt, datetime
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.timezone import activate
from pryictiair import settings
from pryictiair.settings import EMAIL_HOST_USER, URL_GENERAL
from autenticacion.models import Usuario

activate(settings.TIME_ZONE)


def login_tienda(request):
    data = {'titulo': 'Iniciar Sesión', 'url_auth':True}
    addData(request, data)
    if request.method == 'GET':
        des, data['next'] = get_decrypt(request.GET.get('next'))
        if not des:
            data['next'] = request.GET.get('next')
        if request.user.username != "":
            return redirect('/')
        return render(request, 'public/seguridad/login.html', data)
    datos = {'resp': False}
    try:
        addData(request, data)
        if request.method == 'POST':
            usuario_, password = request.POST['usuario'], request.POST['password']
            if Usuario.objects.filter(username=usuario_).exists():
                user = authenticate(username=usuario_, password=password)
                if user is not None:
                    if user.is_active:
                        # if user.es_persona():
                        #     if not user.get_perfil_per().validado:
                        #         datos['error'] = 'Cuenta pendiente de validación, contactar con los administradores del public.'
                        #         return JsonResponse(datos)
                        login(request, user)
                        if user.get_perfil_per():
                            request.session['perfilprincipal'] = user.get_perfil_per()
                        datos['resp'] = True
                        if request.POST.get('next'):
                            datos['redirect'] = request.POST.get('next')
                    else:
                        datos['error'] = 'Este usuario a sido desvinculado del sistema'
                else:
                    datos['error'] = 'Credenciales Incorrectas'
            else:
                datos['error'] = 'Usuario no existe'
            return JsonResponse(datos)
    except Exception as ex:
        datos['error'] = 'Credenciales Incorrectas'
        messages.error(request, ex)
        return JsonResponse(datos)


def logout_tienda(request):
    logout(request)
    return redirect('/')
