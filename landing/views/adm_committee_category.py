from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import get_template
from django.utils.dateformat import DateFormat
from django.utils.decorators import method_decorator
from landing.models import CommitteeCategory, CommitteeMember
from landing.forms import CommitteeCategoryForm, CommitteeMemberForm
from core.funciones_adicionales import salva_logs, customgetattr
from core.custom_forms import FormError
from core.funciones import secure_module, log, paginador, addData, redirectAfterPostGet
import sys
from datetime import date


@login_required
@secure_module
def committeeCategoryView(request):
    data = {'titulo': 'Categorías de Comité',
            'modulo': 'Comité',
            'ruta': request.path,
            'fecha': str(date.today())
            }
    model = CommitteeCategory
    Formulario = CommitteeCategoryForm
    conference = request.session['conference']

    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'add':
                    form = Formulario(request.POST, request=request)
                    if form.is_valid():
                        form.instance.conference = conference
                        form.save()
                        log(f"Registró una nueva categoría de comité {form.instance.__str__()}", request, "add",
                            obj=form.instance.id)
                        messages.success(request, "Categoría de comité agregada exitosamente")
                        res_json.append({'error': False, "to": redirectAfterPostGet(request)})
                    else:
                        raise FormError(form)

                elif action == 'change':
                    filtro = model.objects.get(pk=int(request.POST['pk']))
                    form = Formulario(request.POST, instance=filtro, request=request)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Editó la categoría de comité {filtro.__str__()}", request, "change", obj=filtro.id)
                        messages.success(request, "Categoría de comité modificada con éxito")
                        res_json.append({'error': False, "to": redirectAfterPostGet(request)})
                    else:
                        raise FormError(form)

                elif action == 'delete':
                    filtro = model.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save()
                    log(f"Eliminó la categoría de comité {filtro.__str__()}", request, "del", obj=filtro.id)
                    messages.success(request, "Categoría de comité eliminada exitosamente")
                    res_json.append({'error': False})

                if action == 'addmember':
                    filtro = model.objects.get(pk=int(request.POST['pk']))
                    form = CommitteeMemberForm(request.POST, request.FILES, request=request)
                    if form.is_valid():
                        form.instance.category = filtro
                        form.save()
                        log(f"Registró un nuevo miembro del comité {form.instance.name}", request, "add",
                            obj=form.instance.id)
                        messages.success(request, "Miembro del comité agregado exitosamente")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)

                elif action == 'changemember':
                    filtro = CommitteeMember.objects.get(pk=int(request.POST['pk']))
                    form = CommitteeMemberForm(request.POST, request.FILES, instance=filtro, request=request)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Editó el miembro del comité {filtro.name}", request, "change", obj=filtro.id)
                        messages.success(request, "Miembro del comité modificado con éxito")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)

                elif action == 'deletemember':
                    filtro = CommitteeMember.objects.get(pk=int(request.POST['id']))
                    filtro.status = False
                    filtro.save()
                    log(f"Eliminó el miembro del comité {filtro.name}", request, "del", obj=filtro.id)
                    messages.success(request, "Miembro del comité eliminado exitosamente")
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
                template = get_template("conference/summary/form_summary.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'change':
                pk = int(request.GET['id'])
                committee_category = model.objects.get(pk=pk)
                data["id"] = pk
                data["form"] = Formulario(instance=committee_category)
                template = get_template("conference/summary/form_summary.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'ver':
                pk = int(request.GET['id'])
                committee_category = model.objects.get(pk=pk)
                data["id"] = pk
                data["form"] = Formulario(instance=committee_category, ver=True)
                template = get_template("conference/summary/form_summary.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'members':
                try:
                    # Filtrado y listado
                    data['cab'] = cab = model.objects.get(pk=int(request.GET['id']))
                    data['titulo'] = f'Miembros de la categoría {cab.__str__()}'
                    criterio, filtros, url_vars = request.GET.get('criterio', '').strip(), Q(status=True, category=cab), f'&action={action}&id={cab.pk}'
                    if criterio:
                        filtros = filtros & Q(name__icontains=criterio)
                        data["criterio"] = criterio
                        url_vars += '&criterio=' + criterio

                    listado = CommitteeMember.objects.filter(filtros)
                    data["list_count"] = listado.count()
                    data["url_vars"] = url_vars
                    paginador(request, listado, 20, data, url_vars)
                    return render(request, 'conference/committee_category/members/listado.html', data)
                except Exception as ex:
                    pass

            if action == 'addmember':
                data['filtro'] = model.objects.get(pk=int(request.GET['id']))
                data["form"] = CommitteeMemberForm()
                template = get_template("conference/committee_category/members/form.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'changemember':
                pk = int(request.GET['id'])
                data['filtro'] = filtro = CommitteeMember.objects.get(pk=pk)
                data["form"] = CommitteeMemberForm(instance=filtro)
                template = get_template("conference/committee_category/members/form.html")
                return JsonResponse({"result": True, 'data': template.render(data)})

            elif action == 'vermember':
                pk = int(request.GET['id'])
                filtro = CommitteeMember.objects.get(pk=pk)
                data["id"] = pk
                data["form"] = CommitteeMemberForm(instance=filtro, ver=True)
                template = get_template("conference/guidelinetype/guidelines/form.html")
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
        return render(request, 'conference/committee_category/listado.html', data)
