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

from landing.forms import ConferenceFeeForm, DetailConferenceFeeForm
from landing.models import ConferenceFee, DetailConferenceFee
from seguridad.templatetags.templatefunctions import encrypt


@login_required
@secure_module
def conferenceFeesView(request):
    data = {
        'titulo': 'Conference Fees',
        'modulo': 'Landing',
        'ruta': request.path,
        'fecha': str(date.today())
    }
    addData(request, data)
    conference = request.session['conference']
    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'add':
                    form = ConferenceFeeForm(request.POST, request.FILES, request=request)
                    if form.is_valid():
                        form.instance.conference = conference
                        form.save()
                        log(f"Registro una tarifa de conferencia {form.instance.__str__()}", request, "add")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'change':
                    filtro = ConferenceFee.objects.get(pk=int(request.POST['pk']))
                    form = ConferenceFeeForm(request.POST, request.FILES, request=request, instance=filtro)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Edito una tarifa de conferencia {form.instance.__str__()}", request, "change")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'delete':
                    filtro = ConferenceFee.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save(request)
                    DetailConferenceFee.objects.filter(fee=filtro,status=True).update(status=False)
                    log(f"Elimino una tarifa de conferencia {filtro.__str__()}", request, "delete")
                    messages.success(request, f"Registro Eliminado")
                    res_json = {"error": False}
                elif action == 'adddetail':
                    filtro = ConferenceFee.objects.get(pk=int(request.POST['pk']))
                    form = DetailConferenceFeeForm(request.POST, request.FILES, request=request)
                    if form.is_valid() and filtro:
                        form.instance.cab = filtro
                        form.save()
                        log(f"Edito un detalle para tarifa de conferencia {form.instance.__str__()}", request, "change")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'changedetail':
                    filtro = DetailConferenceFee.objects.get(pk=int(request.POST['pk']))
                    form = DetailConferenceFeeForm(request.POST, request.FILES, request=request, instance=filtro)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Edito un detalle para tarifa de conferencia {form.instance.__str__()}", request, "change")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'deletedetail':
                    filtro = DetailConferenceFee.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save(request)
                    log(f"Elimino un detalle para tarifa de conferencia {filtro.__str__()}", request, "delete")
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
                    form = ConferenceFeeForm()
                    data['form'] = form
                    template = get_template("conference/conference_fee/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
            elif action == 'change':
                try:
                    data['id'] = id = int(request.GET['id'])
                    data['filtro'] = filtro = ConferenceFee.objects.get(pk=id)
                    form = ConferenceFeeForm(instance=filtro)
                    data['form'] = form
                    template = get_template("conference/conference_fee/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
            elif action == 'adddetail':
                try:
                    data['id'] = id = int(request.GET['id'])
                    data['filtro'] = filtro = ConferenceFee.objects.get(pk=id)
                    form = DetailConferenceFeeForm()
                    data['form'] = form
                    template = get_template("conference/conference_fee/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
            elif action == 'changedetail':
                try:
                    data['id'] = id = int(request.GET['id'])
                    data['filtro'] = filtro = DetailConferenceFee.objects.get(pk=id)
                    form = DetailConferenceFeeForm(instance=filtro)
                    data['form'] = form
                    template = get_template("conference/conference_fee/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
        id, criterio, filtros, url_vars = request.GET.get('id', '').strip(), request.GET.get('criterio', '').strip(), Q(status=True, conference=conference), ''
        if id:
            filtros = filtros & (Q(id=id))
            data["id"] = id
            url_vars += '&id=' + id
        if criterio:
            filtros = filtros & (Q(descripcion__icontains=criterio))
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio
        listado = ConferenceFee.objects.filter(filtros)
        data["list_count"] = listado.count()
        data["url_vars"] = url_vars
        paginador(request, listado.order_by('order'), 20, data, url_vars)
        return render(request, 'conference/conference_fee/listado.html', data)