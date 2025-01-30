from datetime import date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template

from core.custom_models import FormError
from core.funciones import addData, paginador, salva_auditoria, secure_module, redirectAfterPostGet, log
from .forms import CertificadosFormatoForm
from .models import *
from django.contrib import messages
from core.funciones_adicionales import salva_logs, customgetattr
import sys


@login_required
@secure_module
def formatoCertificadosView(request):
    data = {
        'titulo': 'Formatos para Certificados',
        'modulo': 'Seguridad',
        'ruta': request.path,
        'fecha': str(date.today())
    }
    addData(request, data)
    model = CertificadosFormato
    Formulario = CertificadosFormatoForm
    nombre_para_audit = '__str__'
    nombre_app, nombre_model = model._meta.app_label, model._meta.model_name
    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'add':
                    form = Formulario(request.POST, request.FILES, request=request)
                    if form.is_valid():
                        form.save()
                        log(f"Agrego formato certificado {form.instance.__str__()}", request, "add",obj=form.instance.id)
                        messages.success(request,"{} agregado".format(customgetattr(form.instance, nombre_para_audit)))
                        res_json.append({'error': False,
                                         "to": redirectAfterPostGet(request)
                                         })
                    else:
                        raise FormError(form)
                elif action == 'change':
                        filtro = model.objects.get(pk=int(request.POST['pk']))
                        form = Formulario(request.POST, request.FILES, instance=filtro, request=request)
                        if form.is_valid() and filtro:
                            form.save()
                            log(f"Modifico formato certificado {form.instance.__str__()}", request, "change",obj=form.instance.id)
                            messages.success(request,
                                             "{} agregado".format(customgetattr(form.instance, nombre_para_audit)))
                            res_json.append({'error': False,
                                             "to": redirectAfterPostGet(request)
                                             })
                        else:
                            raise FormError(form)
                elif action == 'delete':
                    filtro = model.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save(request)
                    log(f"Elimino formato certificado {filtro.__str__()}", request, "delete",obj=filtro.id)
                    messages.success(request, f"Registro Eliminado")
                    res_json = {"error": False}
                    return JsonResponse(res_json, safe=False)
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
            if action == 'add':
                data["form"] = Formulario()
                return render(request, 'seguridad/formatocertificado/form.html', data)
            elif action == 'change':
                pk = int(request.GET['pk'])
                filtro = model.objects.get(pk=pk)
                data["pk"] = pk
                data["form"] = Formulario(instance=filtro)
                return render(request, 'seguridad/formatocertificado/form.html', data)
            elif action == 'ver':
                pk = int(request.GET['pk'])
                filtro = model.objects.get(pk=pk)
                data["pk"] = pk
                data["form"] = Formulario(instance=filtro, ver=True)
                return render(request, 'seguridad/formatocertificado/form.html', data)
        id, criterio, filtros, url_vars = request.GET.get('id', '').strip(), request.GET.get('criterio', '').strip(), Q(status=True), ''
        if id:
            filtros = filtros & (Q(id=id))
            data["id"] = id
            url_vars += '&id=' + id
        if criterio:
            filtros = filtros & (Q(nombre__icontains=criterio))
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio
        listado = model.objects.filter(filtros)
        data["list_count"] = listado.count()
        data["url_vars"] = url_vars
        paginador(request, listado.order_by('-id'), 20, data, url_vars)
        return render(request, 'seguridad/formatocertificado/listado.html', data)