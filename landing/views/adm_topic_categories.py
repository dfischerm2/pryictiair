from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import get_template
from django.utils.dateformat import DateFormat
from django.utils.decorators import method_decorator
from landing.models import TopicCategory, Topic
from landing.forms import TopicCategoryForm, TopicForm
from core.funciones_adicionales import salva_logs, customgetattr
from core.custom_forms import FormError
from core.funciones import secure_module, log, paginador, addData, redirectAfterPostGet
import sys
from datetime import date


@login_required
@secure_module
def topicCategoryView(request):
    data = {'titulo': 'Categorías de Temas',
            'modulo': 'Conferencia',
            'ruta': request.path,
            'fecha': str(date.today())
            }
    model = TopicCategory
    Formulario = TopicCategoryForm
    conference = request.session['conference']

    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'add':
                    form = Formulario(request.POST, request=request)
                    if form.is_valid():
                        form.save()
                        log(f"Registró una nueva categoría de tema {form.instance.__str__()}", request, "add",
                            obj=form.instance.id)
                        messages.success(request, "Categoría de tema agregada exitosamente")
                        res_json.append({'error': False, "to": redirectAfterPostGet(request)})
                    else:
                        raise FormError(form)

                elif action == 'change':
                    filtro = model.objects.get(pk=int(request.POST['pk']))
                    form = Formulario(request.POST, instance=filtro, request=request)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Editó la categoría de tema {filtro.__str__()}", request, "change", obj=filtro.id)
                        messages.success(request, "Categoría de tema modificada con éxito")
                        res_json.append({'error': False, "to": redirectAfterPostGet(request)})
                    else:
                        raise FormError(form)

                elif action == 'delete':
                    filtro = model.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save()
                    log(f"Eliminó la categoría de tema {filtro.__str__()}", request, "del", obj=filtro.id)
                    messages.success(request, "Categoría de tema eliminada exitosamente")
                    res_json.append({'error': False})

                if action == 'addtopic':
                    filtro = TopicCategory.objects.get(pk=int(request.POST['pk']))
                    form = TopicForm(request.POST, request=request)
                    if form.is_valid():
                        form.instance.category = filtro
                        form.save()
                        log(f"Registró un nuevo tema {form.instance.__str__()}", request, "add", obj=form.instance.id)
                        messages.success(request, "Tema agregado exitosamente")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)

                elif action == 'changetopic':
                    filtro = Topic.objects.get(pk=int(request.POST['pk']))
                    form = TopicForm(request.POST, instance=filtro, request=request)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Editó el tema {filtro.__str__()}", request, "change", obj=filtro.id)
                        messages.success(request, "Tema modificado con éxito")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)

                elif action == 'deletetopic':
                    filtro = Topic.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save()
                    log(f"Eliminó el tema {filtro.__str__()}", request, "del", obj=filtro.id)
                    messages.success(request, "Tema eliminado exitosamente")
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
                data["form"] = Formulario()
                template = get_template("autenticacion/usuario/formmodal.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'change':
                pk = int(request.GET['id'])
                topic_category = model.objects.get(pk=pk)
                data["id"] = pk
                data["form"] = Formulario(instance=topic_category)
                template = get_template("autenticacion/usuario/formmodal.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'ver':
                pk = int(request.GET['id'])
                topic_category = model.objects.get(pk=pk)
                data["id"] = pk
                data["form"] = Formulario(instance=topic_category, ver=True)
                template = get_template("autenticacion/usuario/formmodal.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'topics':
                try:
                    # Filtrado y listado
                    data['cab'] = cab = TopicCategory.objects.get(pk=int(request.GET['id']))
                    data['titulo'] = f'Temas de la categoría {cab.__str__()}'
                    criterio, filtros, url_vars = request.GET.get('criterio', '').strip(), Q(status=True, category=cab), f'&action={action}&id={cab.pk}'
                    if criterio:
                        filtros = filtros & Q(name__icontains=criterio)
                        data["criterio"] = criterio
                        url_vars += '&criterio=' + criterio

                    listado = Topic.objects.filter(filtros)
                    data["list_count"] = listado.count()
                    data["url_vars"] = url_vars
                    paginador(request, listado, 20, data, url_vars)
                    return render(request, 'conference/topic_category/topics/listado.html', data)
                except Exception as ex:
                    pass

            elif action == 'addtopic':
                data['filtro'] = TopicCategory.objects.get(pk=int(request.GET['id']))
                data["form"] = TopicForm()
                template = get_template("conference/topic_category/topics/form.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'changetopic':
                pk = int(request.GET['id'])
                data['filtro'] = filtro = Topic.objects.get(pk=pk)
                data["form"] = TopicForm(instance=filtro)
                template = get_template("conference/topic_category/topics/form.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'vertopic':
                pk = int(request.GET['id'])
                topic = Topic.objects.get(pk=pk)
                data["id"] = pk
                data["form"] = TopicForm(instance=topic, ver=True)
                template = get_template("conference/topic_category/topics/form.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

        # Filtrado y listado
        criterio, filtros, url_vars = request.GET.get('criterio', '').strip(), Q(status=True, conference=conference), ''
        if criterio:
            filtros = filtros & Q(name__icontains=criterio)
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio

        listado = model.objects.filter(filtros)
        data["list_count"] = listado.count()
        data["url_vars"] = url_vars
        paginador(request, listado, 20, data, url_vars)
        return render(request, 'conference/topic_category/listado.html', data)
