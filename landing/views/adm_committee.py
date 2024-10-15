from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.db.models import Q
from django.utils.dateformat import DateFormat
from django.utils.decorators import method_decorator
from landing.models import CommitteeMember
from landing.forms import CommitteeMemberForm
from core.funciones_adicionales import salva_logs, customgetattr
from core.custom_forms import FormError
from core.funciones import secure_module, log, paginador, addData, redirectAfterPostGet
import sys
from datetime import date


@login_required
@secure_module
def committeeMemberView(request):
    data = {'titulo': 'Miembros del Comité',
            'modulo': 'Comité',
            'ruta': request.path,
            'fecha': str(date.today())
            }
    model = CommitteeMember
    Formulario = CommitteeMemberForm

    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'add':
                    form = Formulario(request.POST, request.FILES, request=request)
                    if form.is_valid():
                        form.save()
                        log(f"Registró un nuevo miembro del comité {form.instance.name}", request, "add",
                            obj=form.instance.id)
                        messages.success(request, "Miembro del comité agregado exitosamente")
                        res_json.append({'error': False, "to": redirectAfterPostGet(request)})
                    else:
                        raise FormError(form)

                elif action == 'change':
                    filtro = model.objects.get(pk=int(request.POST['pk']))
                    form = Formulario(request.POST, request.FILES, instance=filtro, request=request)
                    if form.is_valid() and filtro:
                        form.save()
                        log(f"Editó el miembro del comité {filtro.name}", request, "change", obj=filtro.id)
                        messages.success(request, "Miembro del comité modificado con éxito")
                        res_json.append({'error': False, "to": redirectAfterPostGet(request)})
                    else:
                        raise FormError(form)

                elif action == 'delete':
                    filtro = model.objects.get(pk=int(request.POST['id']))
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
                return render(request, 'conference/committee_member/form.html', data)

            elif action == 'change':
                pk = int(request.GET['pk'])
                committee_member = model.objects.get(pk=pk)
                data["pk"] = pk
                data["form"] = Formulario(instance=committee_member)
                return render(request, 'conference/committee_member/form.html', data)

            elif action == 'ver':
                pk = int(request.GET['pk'])
                committee_member = model.objects.get(pk=pk)
                data["pk"] = pk
                data["form"] = Formulario(instance=committee_member, ver=True)
                return render(request, 'conference/committee_member/form.html', data)

        # Filtrado y listado
        criterio, filtros, url_vars = request.GET.get('criterio', '').strip(), Q(), ''
        if criterio:
            filtros = filtros & Q(name__icontains=criterio)
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio

        listado = model.objects.filter(filtros)
        data["list_count"] = listado.count()
        data["url_vars"] = url_vars
        paginador(request, listado, 20, data, url_vars)
        return render(request, 'conference/committee_member/listado.html', data)
