from datetime import date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from core.custom_models import FormError
from core.funciones import addData, paginador, secure_module, log
from django.contrib import messages

from landing.forms import ConferenceForm
from landing.models import Conference


@login_required
@secure_module
def conferenceView(request):
    data = {
        'titulo': 'Conference',
        'modulo': 'Landing',
        'ruta': request.path,
        'fecha': str(date.today())
    }
    addData(request, data)
    model = Conference
    Formulario = ConferenceForm
    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'add':
                    form = Formulario(request.POST, request.FILES, request=request)
                    if form.is_valid():
                        form.save()
                        log(f"Registro un evento {form.instance.__str__()}", request, "add")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'change':
                    filtro = model.objects.get(pk=int(request.POST['pk']))
                    form = Formulario(request.POST, request.FILES, request=request, instance=filtro)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Edito un evento {form.instance.__str__()}", request, "change")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'delete':
                    filtro = model.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save(request)
                    log(f"Elimino un evento {filtro.__str__()}", request, "delete")
                    messages.success(request, f"Registro Eliminado")
                    res_json = {"error": False}
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
                try:
                    form = Formulario()
                    data['form'] = form
                    template = get_template("conference/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
            elif action == 'change':
                try:
                    data['id'] = id = int(request.GET['id'])
                    data['filtro'] = filtro = model.objects.get(pk=id)
                    form = Formulario(instance=filtro)
                    data['form'] = form
                    template = get_template("conference/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
        id, criterio, filtros, url_vars = request.GET.get('id', '').strip(), request.GET.get('criterio', '').strip(), Q(status=True), ''
        if id:
            filtros = filtros & (Q(id=id))
            data["id"] = id
            url_vars += '&id=' + id
        if criterio:
            filtros = filtros & (Q(title__icontains=criterio))
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio
        listado = model.objects.filter(filtros)
        data["list_count"] = listado.count()
        data["url_vars"] = url_vars
        paginador(request, listado.order_by('-active','-end_date'), 20, data, url_vars)
        return render(request, 'conference/listado.html', data)