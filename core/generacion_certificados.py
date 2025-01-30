import os
import sys
from datetime import datetime

import pyqrcode
from django.db import transaction

from core.funcionesxhtml2pdf import conviert_html_to_pdf, conviert_html_to_pdfsaveqrcertificado
from landing.models import InscripcionConference
from pryictiair.settings import MEDIA_ROOT


def preview_certificado(request, idinscripcion):
    try:
        datos_pdf = {}
        datos_pdf["DOMINIO_DEL_SISTEMA"] = dominio_sistema = request.build_absolute_uri('/')[:-1].strip("/")
        datos_pdf['inscrito'] = inscrito = InscripcionConference.objects.get(status=True, id=int(idinscripcion))
        datos_pdf['evento'] = evento = inscrito.conference
        tipo = 1 if inscrito.role == 1 else 2
        if tipo == 1 and not evento.certificado_autores:
            raise NameError('El evento no tiene un formato de certificado para autores configurado.')
        if tipo == 2 and not evento.certificado_asistentes:
            raise NameError('El evento no tiene un formato de certificado para asistentes configurado.')
        datos_pdf['certificado'] = evento.certificado_autores if tipo == 1 else evento.certificado_asistentes
        mes = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
               "noviembre", "diciembre"]
        datos_pdf['fecha'] = u"%s / %s / %s" % (datetime.now().day, str(mes[datetime.now().month - 1]), datetime.now().year)
        directory_certificados = os.path.join(MEDIA_ROOT, 'certificados')
        try:
            os.stat(directory_certificados)
        except:
            os.mkdir(directory_certificados)
        directory_qr = os.path.join(MEDIA_ROOT, 'certificados', 'qr', '')
        try:
            os.stat(directory_qr)
        except:
            os.mkdir(directory_qr)
        qrname = 'qr_certificado_{}'.format(inscrito.id)
        rutapdf = '{}/{}.pdf'.format(directory_qr, qrname)
        rutaimg = '{}/{}.png'.format(directory_qr, qrname)
        if os.path.isfile(rutapdf):
            os.remove(rutaimg)
            os.remove(rutapdf)
        url = pyqrcode.create('{}certificate-verification/?cod={}'.format(dominio_sistema, inscrito.id))
        url.png('{}{}.png'.format(directory_qr, qrname), 16, '#000000')
        datos_pdf['qrname'] = '{}'.format(qrname)
        tipo_certificado = (evento.certificado_autores.tipocertificado if tipo == 1 else evento.certificado_asistentes.tipocertificado)
        template = 'certificados/horizontal.html' if tipo_certificado == 1 else 'certificados/vertical.html'
        return True, conviert_html_to_pdf(template, {'pagesize': 'A4', 'data': datos_pdf})
    except Exception as ex:
        text_error = 'Error on line {}, {}'.format(sys.exc_info()[-1].tb_lineno, ex)
        return False, text_error


def generate_certificado(request, idinscripcion):
    try:
        with transaction.atomic():
            datos_pdf = {}
            datos_pdf["DOMINIO_DEL_SISTEMA"] = dominio_sistema = request.build_absolute_uri('/')[:-1].strip("/")
            datos_pdf['inscrito'] = inscrito = InscripcionConference.objects.get(status=True, id=int(idinscripcion))
            datos_pdf['evento'] = evento = inscrito.conference
            tipo = 1 if inscrito.role == 1 else 2
            if tipo == 1 and not evento.certificado_autores:
                raise NameError('El evento no tiene un formato de certificado para autores configurado.')
            if tipo == 2 and not evento.certificado_asistentes:
                raise NameError('El evento no tiene un formato de certificado para asistentes configurado.')
            datos_pdf['certificado'] = evento.certificado_autores if tipo == 1 else evento.certificado_asistentes
            mes = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            datos_pdf['fecha'] = u"%s / %s / %s" % (datetime.now().day, str(mes[datetime.now().month - 1]), datetime.now().year)
            directory_certificados = os.path.join(MEDIA_ROOT, 'certificados')
            try:
                os.stat(directory_certificados)
            except:
                os.mkdir(directory_certificados)
            directory_qr = os.path.join(MEDIA_ROOT, 'certificados', 'qr', '')
            try:
                os.stat(directory_qr)
            except:
                os.mkdir(directory_qr)
            qrname = 'qr_certificado_{}'.format(inscrito.id)
            rutapdf = '{}/{}.pdf'.format(directory_certificados, qrname)
            rutaimg = '{}/{}.png'.format(directory_qr, qrname)
            if os.path.isfile(rutapdf):
                os.remove(rutaimg)
                os.remove(rutapdf)
            url = pyqrcode.create('{}certificate-verification/?cod={}'.format(dominio_sistema, inscrito.id))
            url.png('{}{}.png'.format(directory_qr, qrname), 16, '#000000')
            datos_pdf['qrname'] = '{}'.format(qrname)
            tipo_certificado = (evento.certificado_autores.tipocertificado if tipo == 1 else evento.certificado_asistentes.tipocertificado)
            template = 'certificados/horizontal.html' if tipo_certificado == 1 else 'certificados/vertical.html'
            valid = conviert_html_to_pdfsaveqrcertificado(template, {'pagesize': 'A4', 'data': datos_pdf}, qrname + '.pdf')
            if not valid:
                raise NameError('Error al generar el certificado.')
            inscrito.certificado = f'certificados/{qrname}.pdf'
            inscrito.gen_certificado = True
            inscrito.fecha_certificado = datetime.now()
            inscrito.user_certificado = request.user
            inscrito.save(request)
            return True, conviert_html_to_pdf(template, {'pagesize': 'A4', 'data': datos_pdf})
    except Exception as ex:
        text_error = 'Error on line {}, {}'.format(sys.exc_info()[-1].tb_lineno, ex)
        return False, text_error
