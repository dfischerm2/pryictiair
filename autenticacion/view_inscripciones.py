import os
import random
import sys
import zipfile
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import get_template

from autenticacion.forms import InscripcionConferenceForm, ChangeInscripcionConferenceForm
from autenticacion.models import Usuario, PerfilPersona
from core.custom_models import FormError
from core.funciones import addData, paginador, secure_module, remover_caracteres_especiales_unicode, log
from core.generacion_certificados import preview_certificado, generate_certificado

from landing.models import InscripcionConference, ROLES_FEE_CHOICE, Conference, PapersInscripcionConference, \
    TopicsInscripcionConference
from pryictiair.settings import SITE_STORAGE, ID_GRUPO_USUARIO
from seguridad.templatetags.templatefunctions import encrypt
from django.contrib.auth.models import Group


@login_required
@secure_module
def inscripcionesView(request):
    data = {
        'titulo': 'Inscripciones',
        'modulo': 'Landing',
        'ruta': request.path,
        'fecha': str(date.today())
    }
    addData(request, data)
    data['conference'] = conference = request.session['conference']
    if request.method == 'POST':
        res_json = []
        action = request.POST['action']
        try:
            with transaction.atomic():
                if action == 'addinscription':
                    filtro = Conference.objects.get(pk=int(request.POST['pk']))
                    form = InscripcionConferenceForm(request.POST, request.FILES, request=request)
                    if form.is_valid():
                        persona_ = form.cleaned_data['persona']
                        if InscripcionConference.objects.filter(persona=persona_, conference=filtro, status=True).exists():
                            raise NameError(f"La persona {persona_.__str__()} ya se encuentra inscrita en esta conferencia.")
                        form.instance.conference = filtro
                        form.save()
                        filtro = InscripcionConference.objects.get(pk=form.instance.pk)
                        user = filtro.persona
                        if not PerfilPersona.objects.filter(usuario=user).exists():
                            perfil_ = PerfilPersona.objects.create(usuario=user)
                        else:
                            perfil_ = PerfilPersona.objects.filter(usuario=user).first()
                        perfil_.status = True
                        perfil_.save(request)
                        grupo_ = Group.objects.get(pk=ID_GRUPO_USUARIO)
                        if not grupo_.user_set.filter(id=user.id).exists():
                            grupo_.user_set.add(user)
                            grupo_.save()
                        log(f"Registro una nueva inscripcion {form.instance.__str__()}", request, "add")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'changeinscription':
                    filtro = InscripcionConference.objects.get(pk=int(request.POST['pk']))
                    form = ChangeInscripcionConferenceForm(request.POST, request.FILES, request=request, instance=filtro)
                    if form.is_valid():
                        form.save()
                        log(f"Modificó la inscripcion {filtro.__str__()}", request, "change")
                        res_json.append({'error': False, "reload": True})
                    else:
                        raise FormError(form)
                elif action == 'deleteinscription':
                    filtro = InscripcionConference.objects.get(pk=int(encrypt(request.POST['id'])))
                    if not filtro:
                        raise ValueError("No se encontró el registro")
                    filtro.status=False
                    PapersInscripcionConference.objects.filter(cab=filtro, status=True).update(status=False)
                    TopicsInscripcionConference.objects.filter(cab=filtro, status=True).update(status=False)
                    messages.success(request, f"Inscripcion eliminada con exito")
                    log(f"Elimino la inscripcion {filtro.__str__()}", request, "delete")
                    res_json = {'error': False}
                elif action == 'preview_certificado':
                    filtro = InscripcionConference.objects.get(pk=int(request.POST['id']))
                    if not filtro:
                        raise ValueError("No se encontró el registro")
                    error, result = preview_certificado(request, filtro.id)
                    if not error:
                        raise NameError(result)
                    return result
                elif action == 'gen_certificado':
                    filtro = InscripcionConference.objects.get(pk=int(request.POST['pk']))
                    gen_type = request.POST.get('type', None)
                    if not filtro:
                        raise ValueError("No se encontró el registro")
                    error, result = generate_certificado(request, filtro.id)
                    if not error:
                        raise NameError(result)
                    log(f"Genero el certificado de la inscripcion {filtro.__str__()}", request, "change")
                    if not gen_type:
                        return result
                    else:
                        return JsonResponse(
                            {'error': False, 'message': f'{filtro.persona.datos()} certificado generado.'})
                elif action == 'deletecertificado':
                    filtro = InscripcionConference.objects.get(pk=int(encrypt(request.POST['id'])))
                    if not filtro:
                        raise ValueError("No se encontró el registro")
                    filtro.gen_certificado = False
                    filtro.certificado = ''
                    filtro.save(request)
                    messages.success(request, f"Certificado eliminado con exito")
                    log(f"Elimino el certificado de la inscripcion {filtro.__str__()}", request, "delete")
                    res_json = {'error': False}
                elif action == 'deleteuser':
                    usuario = Usuario.objects.get(pk=int(request.POST['id']))
                    usuario.is_active = False
                    usuario.status = False
                    usuario.save(request)
                    log('Desactivo Usuario', request, 'change')
                    messages.success(request, "El acceso para este usuario ha sido desactivado..")
                    res_json = {'error': False}
                elif action == 'activate':
                    usuario = Usuario.objects.get(pk=int(request.POST['id']))
                    usuario.is_active = True
                    usuario.status = True
                    usuario.save(request)
                    log('Activo Usuario', request, 'change')
                    messages.success(request, "Habilitado correctamente.")
                    res_json.append({'error': False, "reload": True})
                elif action == 'crearperfilusuario':
                    filtro = InscripcionConference.objects.get(pk=int(request.POST['id']))
                    usuario = filtro.persona
                    if not usuario.get_perfil_per():
                        grupo_ = Group.objects.get(pk=ID_GRUPO_USUARIO)
                        if not grupo_.user_set.filter(id=usuario.id).exists():
                            grupo_.user_set.add(usuario)
                            grupo_.save()
                        if not PerfilPersona.objects.filter(usuario=usuario).exists():
                            perfil_ = PerfilPersona.objects.create(usuario=usuario)
                        else:
                            perfil_ = PerfilPersona.objects.filter(usuario=usuario).first()
                        perfil_.status = True
                        perfil_.save()
                        messages.success(request, "Perfil estudiante habilitado.")
                        res_json.append({'error': False, "reload": True})
                    else:
                        res_json = {'error': True, "message": f"Ya tiene perfil de usuario activo {usuario}"}
                elif action == 'deleteperfilusuario':
                    try:
                        filtro = InscripcionConference.objects.get(pk=int(request.POST['id']))
                        usuario = filtro.persona
                        if usuario.get_perfil_per():
                            grupo = Group.objects.get(id=ID_GRUPO_USUARIO)
                            grupo.user_set.remove(usuario)
                            perfil_ = PerfilPersona.objects.filter(usuario=usuario).first()
                            perfil_.status = False
                            perfil_.save(request)
                            log(f"Desactivo el perfil usuario de {perfil_.__str__()}", request, "delete")
                            messages.success(request, f"Perfil Desactivado")
                            res_json = {"error": False}
                        else:
                            res_json = {'error': True, "message": f"No tiene perfil de usuario activo {usuario}"}
                    except Exception as ex:
                        res_json = {'error': True, "message": f"Error: {ex}"}
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
            if action == 'addinscription':
                try:
                    data['id'] = id = int(encrypt(request.GET['id']))
                    data['filtro'] = filtro = Conference.objects.get(pk=id)
                    form = InscripcionConferenceForm()
                    form.fields['persona'].queryset = Usuario.objects.none()
                    form.fields['fecha'].initial = date.today()
                    data['form'] = form
                    template = get_template("autenticacion/inscripciones/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
            elif action == 'changeinscription':
                try:
                    data['id'] = id = int(encrypt(request.GET['id']))
                    data['filtro'] = filtro = InscripcionConference.objects.get(pk=id)
                    form = ChangeInscripcionConferenceForm(instance=filtro)
                    data['form'] = form
                    template = get_template("autenticacion/inscripciones/form.html")
                    return JsonResponse({"result": True, 'data': template.render(data)})
                except Exception as ex:
                    return JsonResponse({"result": False, 'message': str(ex)})
            elif action == 'fecth_inscritos':
                try:
                    conference = Conference.objects.get(pk=int(request.GET['pk']))
                    queryset = InscripcionConference.objects.filter(status=True, conference=conference, gen_certificado=False, asistio=True).values('id', 'persona__last_name', 'persona__first_name').order_by('persona__last_name')
                    if not queryset.exists():
                        raise NameError(f"No se encontraron inscripciones sin certificados por generar.")
                    return JsonResponse( {'error': False, 'message': 'Inscripciones cargados', 'data': list(queryset)})
                except NameError as e:
                    return JsonResponse({'error': True, 'message': str(e)})
                except Exception as e:
                    return JsonResponse( {'error': True, 'message': f"Se produjo un error inesperado al cargar las inscripciones: {e}"})
            elif action == 'download_certificados_zip':
                nombre_persona = ''
                try:
                    totalinscritos = InscripcionConference.objects.filter(status=True, conference=conference, gen_certificado=True)
                    nombre_curso = remover_caracteres_especiales_unicode(conference.title.lower().replace(' ', '_')).lower().replace(' ', '_').replace('-', '').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('.', '')
                    directory = os.path.join(SITE_STORAGE, 'media', 'zip')
                    try:
                        os.stat(directory)
                    except:
                        os.mkdir(directory)
                    nombre_zip = '{}_{}.zip'.format(nombre_curso, random.randint(1, 10000).__str__())
                    url = os.path.join(SITE_STORAGE, 'media', 'zip', nombre_zip)
                    url_zip = url
                    fantasy_zip = zipfile.ZipFile(url, 'w')
                    for inscrito in totalinscritos:
                        nombre_persona = remover_caracteres_especiales_unicode(inscrito.persona.datos().lower().replace(' ', '_')).lower().replace(' ', '_')
                        if inscrito.gen_certificado:
                            fantasy_zip.write(inscrito.certificado.path, '{}.pdf'.format(nombre_persona))
                    fantasy_zip.close()
                    response = HttpResponse(open(url_zip, 'rb'), content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename={}'.format(nombre_zip)
                    return response
                except Exception as ex:
                    print(ex)
                    print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno))
                    text_error = 'Error on line {}, {}, Persona: {}'.format(sys.exc_info()[-1].tb_lineno, ex, nombre_persona)
                    return JsonResponse({"result": "bad", "mensaje": f"Error al obtener los datos. {text_error}"})
            elif action == 'buscarpersona':
                try:
                    q = request.GET['q'].upper().strip()
                    s = q.split(" ")
                    qspersona = Usuario.objects.filter(status=True).order_by('last_name')
                    if len(s) == 1:
                        qspersona = qspersona.filter(Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)).distinct()[:15]
                    elif len(s) == 2:
                        qspersona = qspersona.filter(
                            Q(last_name__icontains=s[0]) |
                            (Q(first_name__icontains=s[0]) & Q(first_name__icontains=s[1])) |
                            (Q(last_name__icontains=s[0]) & Q(last_name__icontains=s[1]))
                        ).distinct()[:15]
                    elif len(s) == 3:
                        qspersona = qspersona.filter(
                            (Q(first_name__icontains=s[0]) & Q(last_name__icontains=s[1]) & Q(last_name__icontains=s[2])) |
                            (Q(last_name__icontains=s[0]) & Q(last_name__icontains=s[1]) & Q(first_name__icontains=s[2]))
                        ).distinct()[:15]
                    else:
                        qspersona = qspersona.filter(
                            Q(first_name__icontains=s[0]) & Q(last_name__icontains=s[1]) & Q(last_name__icontains=s[2])
                        ).distinct()[:15]
                    data = {"result": "ok", "results": [{"id": x.pk, "name": f"{x.__str__()}"} for x in qspersona]}
                    return JsonResponse(data)
                except Exception as ex:
                    data = {"result": "ok", "results": []}
                    return JsonResponse(data)

        id, criterio, filtros, url_vars = request.GET.get('id', '').strip(), request.GET.get('criterio', '').strip(), Q(status=True, conference=conference), ''
        rolid = request.GET.get('rolid', '')
        if id:
            filtros = filtros & (Q(id=id))
            data["id"] = id
            url_vars += '&id=' + id
        if criterio:
            filtros = filtros & (Q(persona__first_name__icontains=criterio) | Q(persona__last_name__icontains=criterio) | Q(persona__email__icontains=criterio))
            data["criterio"] = criterio
            url_vars += '&criterio=' + criterio
        if rolid:
            filtros = filtros & (Q(role=rolid))
            data["rolid"] = rolid
            url_vars += '&rolid=' + rolid
        try:
            listado = InscripcionConference.objects.filter(filtros)
            data["list_count"] = listado.count()
            data["url_vars"] = url_vars
            data['ROLES_FEE_CHOICE'] = ROLES_FEE_CHOICE
            data['totgenerados'] = InscripcionConference.objects.filter(status=True, conference=conference, gen_certificado=True).count()
            paginador(request, listado.order_by('-id'), 20, data, url_vars)
            return render(request, 'autenticacion/inscripciones/listado.html', data)
        except Exception as ex:
            messages.error(request, f"Error: {ex}")
            return redirect(request.path)