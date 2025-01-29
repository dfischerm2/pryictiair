from datetime import date
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template
from core.custom_models import FormError
from core.funciones import addData, paginador, secure_module, log, remover_caracteres_especiales_unicode, generar_nombre
from django.contrib import messages

from landing.forms import ScheduleConferenceForm, DetailScheduleConferenceForm
from landing.models import ScheduleConference, DetailScheduleConference
from seguridad.templatetags.templatefunctions import encrypt


@login_required
@secure_module
def conferenceScheduleView(request):
    data = {
        'titulo': 'Conference Schedule',
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
                    form = ScheduleConferenceForm(request.POST, request.FILES, request=request)
                    if form.is_valid():
                        if 'pdf' in request.FILES:
                            file = request.FILES['pdf']
                            nombredocumento = remover_caracteres_especiales_unicode(file._name)
                            file._name = generar_nombre(nombredocumento, file._name)
                            form.instance.pdf = file
                        form.instance.conference = conference
                        form.save()
                        log(f"Registro un dia de conferencia {form.instance.__str__()}", request, "add")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'change':
                    filtro = ScheduleConference.objects.get(pk=int(request.POST['pk']))
                    form = ScheduleConferenceForm(request.POST, request.FILES, request=request, instance=filtro)
                    if form.is_valid() and filtro:
                        if 'pdf' in request.FILES:
                            file = request.FILES['pdf']
                            nombredocumento = remover_caracteres_especiales_unicode(file._name)
                            file._name = generar_nombre(nombredocumento, file._name)
                            form.instance.pdf = file
                        form.save()
                        log(f"Edito un dia de conferencia {form.instance.__str__()}", request, "change")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'delete':
                    filtro = ScheduleConference.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save(request)
                    DetailScheduleConference.objects.filter(fee=filtro,status=True).update(status=False)
                    log(f"Elimino un dia de conferencia {filtro.__str__()}", request, "delete")
                    messages.success(request, f"Registro Eliminado")
                    res_json = {"error": False}
                elif action == 'adddetail':
                    filtro = ScheduleConference.objects.get(pk=int(request.POST['pk']))
                    form = DetailScheduleConferenceForm(request.POST, request.FILES, request=request)
                    if form.is_valid() and filtro:
                        form.instance.cab = filtro
                        form.save()
                        log(f"Edito un detalle para dia de conferencia {form.instance.__str__()}", request, "change")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'changedetail':
                    filtro = DetailScheduleConference.objects.get(pk=int(request.POST['pk']))
                    form = DetailScheduleConferenceForm(request.POST, request.FILES, request=request, instance=filtro)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Edito un detalle para dia de conferencia {form.instance.__str__()}", request, "change")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'deletedetail':
                    filtro = DetailScheduleConference.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save(request)
                    log(f"Elimino un detalle para dia de conferencia {filtro.__str__()}", request, "delete")
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
                    form = ScheduleConferenceForm()
                    data['form'] = form
                    template = get_template("conference/schedule/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
            elif action == 'change':
                try:
                    data['id'] = id = int(request.GET['id'])
                    data['filtro'] = filtro = ScheduleConference.objects.get(pk=id)
                    form = ScheduleConferenceForm(instance=filtro)
                    data['form'] = form
                    template = get_template("conference/schedule/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
            elif action == 'adddetail':
                try:
                    data['id'] = id = int(request.GET['id'])
                    data['filtro'] = filtro = ScheduleConference.objects.get(pk=id)
                    form = DetailScheduleConferenceForm()
                    data['form'] = form
                    template = get_template("conference/schedule/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
            elif action == 'changedetail':
                try:
                    data['id'] = id = int(request.GET['id'])
                    data['filtro'] = filtro = DetailScheduleConference.objects.get(pk=id)
                    form = DetailScheduleConferenceForm(instance=filtro)
                    data['form'] = form
                    template = get_template("conference/schedule/form.html")
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
        listado = ScheduleConference.objects.filter(filtros)
        data["list_count"] = listado.count()
        data["url_vars"] = url_vars
        paginador(request, listado.order_by('order'), 20, data, url_vars)
        return render(request, 'conference/schedule/view.html', data)