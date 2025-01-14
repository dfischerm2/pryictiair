from datetime import date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from core.funciones import addData, mi_paginador, salva_auditoria, secure_module, log
from core.funciones_adicionales import customgetattr
from .forms import EntidadFinancieraForm
from .models import EntidadFinanciera
from django.contrib import messages
from datetime import date, datetime

@login_required
@secure_module
def entidadFinancieraView(request):
    data = {'titulo': 'Entidad Financiera',
            'modulo': 'Financiero',
            'ruta': request.path,

            }
    model = EntidadFinanciera
    Formulario = EntidadFinancieraForm
    nombre_para_audit = 'nombre'
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
                            log(f"Agrego entidad financiera {form.instance.__str__()}", request, "add",obj=form.instance.id)
                            messages.success(request, "{} agregado correctamente.".format(customgetattr(form.instance, nombre_para_audit)))
                            res_json.append({'error': False,
                                             "to": request.path + "?action=add" if '_add' in request.POST else request.path
                                             })
                        else:
                            res_json.append({'error': True,
                                             "form": [{k: v[0]} for k, v in form.errors.items()],
                                             "message": "Error en el formulario"
                                             })
                elif action == 'change':
                    filtro = model.objects.get(pk=int(request.POST['pk']))
                    form = Formulario(request.POST, request.FILES, instance=filtro, request=request)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Modifico entidad financiera {form.instance.__str__()}", request, "change",obj=form.instance.id)
                        messages.success(request, "{} modificado correctamente.".format(
                            customgetattr(form.instance, nombre_para_audit)))
                        res_json.append({'error': False,
                                         "to": request.path + "?action=add" if '_add' in request.POST else request.path
                                         })
                    else:
                        res_json.append({'error': True,
                                         "form": [{k: v[0]} for k, v in form.errors.items()],
                                         "message": "Error en el formulario"
                                         })
                elif action == 'delete':
                    filtro = model.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save(request)
                    log(f"Elimino entidad financiera {filtro.__str__()}", request, "delete",obj=filtro.id)
                    return redirect(request.path)
        except ValueError as ex:
            res_json.append({'error': True,
                             "message": str(ex)
                             })
        except Exception as ex:
            res_json.append({'error': True,
                             "message": "Intente Nuevamente"
                             })
        return JsonResponse(res_json, safe=False)
    elif request.method == 'GET':
        addData(request, data)
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']
            if action == 'add':
                    data["form"] = Formulario()
                    return render(request, 'financiero/entidad_financiera/form.html', data)
            elif action == 'change':
                    pk = int(request.GET['pk'])
                    instancia = model.objects.get(pk=pk)
                    data["pk"] = pk
                    data["form"] = Formulario(instance=instancia)
                    return render(request, 'financiero/entidad_financiera/form.html', data)
            elif action == 'ver':
                    pk = int(request.GET['pk'])
                    instancia = model.objects.get(pk=pk)
                    data["pk"] = pk
                    data["form"] = Formulario(instance=instancia, ver=True)
                    return render(request, 'financiero/entidad_financiera/form.html', data)

        criterio, filtros, url_vars = request.GET.get('criterio', ''), Q(status=True), ''
        if criterio:
            filtros = filtros & Q(nombre__icontains=criterio)
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio
        listado = model.objects.filter(filtros)
        data["url_vars"] = url_vars
        mi_paginador(request, listado, 40, data)
        return render(request, 'financiero/entidad_financiera/listado.html', data)