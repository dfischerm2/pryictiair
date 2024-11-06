from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import get_template
from django.utils.dateformat import DateFormat
from django.utils.decorators import method_decorator
from landing.models import SummaryImage, Summary
from landing.forms import SummaryImageForm
from core.funciones_adicionales import salva_logs, customgetattr
from core.custom_forms import FormError
from core.funciones import secure_module, log, paginador, addData, redirectAfterPostGet
import sys
from datetime import date


@login_required
# @secure_module
def summaryImageView(request):
    data = {'titulo': 'Imagenes del resumen',
            'modulo': 'Conferencia',
            'ruta': request.path,
            'fecha': str(date.today())
            }
    model = SummaryImage
    Formulario = SummaryImageForm

    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'add':
                    form = Formulario(request.POST, request.FILES, request=request)
                    if form.is_valid():
                        form.save()
                        log(f"Registró un nueva imagen resumen {form.instance.__str__()}", request, "add",
                            obj=form.instance.id)
                        messages.success(request, "Resumen agregado exitosamente")
                        path = redirectAfterPostGet(request)
                        path += '&summary_id={}'.format(form.instance.summary.id)
                        res_json.append({'error': False, "to": path})
                    else:
                        raise FormError(form)

                elif action == 'change':
                    filtro = model.objects.get(pk=int(request.POST['pk']))
                    form = Formulario(request.POST, instance=filtro, request=request)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Editó la imagen resumen {filtro.__str__()}", request, "change", obj=filtro.id)
                        messages.success(request, "Resumen modificado con éxito")
                        path = redirectAfterPostGet(request)
                        path += '&summary_id={}'.format(form.instance.summary.id)
                        res_json.append({'error': False, "to": path})
                    else:
                        raise FormError(form)

                elif action == 'delete':
                    filtro = model.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save()
                    log(f"Eliminó la imagen resumen {filtro.__str__()}", request, "del", obj=filtro.id)
                    messages.success(request, "Resumen eliminado exitosamente")
                    res_json.append({'error': False})

        except ValueError as ex:
            res_json.append({'error': True, "message": str(ex)})
        except FormError as ex:
            res_json.append(ex.dict_error)
        except Exception as ex:
            salva_logs(request, __file__, request.method, action, type(ex).__name__,
                       'Error on line {}'.format(sys.exc_info()[-1].tb_lineno), ex)
            res_json.append({'error': True, "message": "Intente nuevamente"})

        return JsonResponse(res_json, safe=False)

    elif request.method == 'GET':
        addData(request, data)
        if 'action' in request.GET:
            data["action"] = action = request.GET['action']
            if action == 'add':
                summary_id = request.GET.get('id', 0)
                data['summary'] = summary = Summary.objects.get(pk=summary_id)
                data["form"] = Formulario(
                    initial={
                        'summary': summary
                    }
                )
                template = get_template("conference/summary/form.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'change':
                pk = int(request.GET['id'])
                summary = model.objects.get(pk=pk)
                data["id"] = pk
                data['summary'] = summary.summary
                data["form"] = Formulario(instance=summary)
                template = get_template("conference/summary/form.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'ver':
                pk = int(request.GET['id'])
                summary = model.objects.get(pk=pk)
                data["id"] = pk
                data['summary'] = summary.summary
                data["form"] = Formulario(instance=summary, ver=True)
                template = get_template("conference/summary/form.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

        # Filtrado y listado
        summary_id, criterio, filtros, url_vars = request.GET.get('summary_id', 0), request.GET.get('criterio',
                                                                                                    '').strip(), Q(status=True), ''
        if criterio:
            filtros = filtros & Q(title__icontains=criterio)
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio
        if summary_id:
            filtros = filtros & Q(summary_id=int(summary_id))
            data["summary"] = Summary.objects.get(pk=summary_id)
            url_vars += '&summary_id=' + summary_id

        listado = model.objects.filter(filtros)
        data["list_count"] = listado.count()
        data["url_vars"] = url_vars
        paginador(request, listado, 20, data, url_vars)
        return render(request, 'conference/summary/listado_image.html', data)
