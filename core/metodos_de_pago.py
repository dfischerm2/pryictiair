import json

import requests
from _decimal import Decimal
from requests.auth import HTTPBasicAuth

from core.decoradores import sync_to_async_function
from pryictiair.settings import PAYPAL_CLIENT_ID, PREPARE_PAYPAL_URL, PAYPAL_SECRET_KEY, \
    PAYPAL_REEMBOLSO_URL, PAYPAL_ORDER_URL, CONFIRM_PAYPAL_URL, PAYPAL_ORDER_DETAIL_URL, PREPARE_PAYPAL_URL_TEST, PAYPAL_CLIENT_ID_TEST, PAYPAL_SECRET_KEY_TEST, PAYPAL_ORDER_URL_TEST, CONFIRM_PAYPAL_URL_TEST, PAYPAL_ORDER_DETAIL_URL_TEST, PAYPAL_REEMBOLSO_URL_TEST
from pedidos.models import Pedido, PagoPayPal, HistorialPedido


def reversar_pago_paypal(paypalCaptureId, requestId):
    '''Devuelve el dinero, como que nunca se hizo la transacción'''
    if paypalCaptureId:
        from seguridad.models import Configuracion
        confi = Configuracion.get_instancia()
        if confi.paypal_modo:
            PREPARE_PAYPAL_URL_ = PREPARE_PAYPAL_URL
            PAYPAL_CLIENT_ID_ = PAYPAL_CLIENT_ID
            PAYPAL_SECRET_KEY_ = PAYPAL_SECRET_KEY
            PAYPAL_REEMBOLSO_URL_ = PAYPAL_REEMBOLSO_URL
        else:
            PREPARE_PAYPAL_URL_ = PREPARE_PAYPAL_URL_TEST
            PAYPAL_CLIENT_ID_ = PAYPAL_CLIENT_ID_TEST
            PAYPAL_SECRET_KEY_ = PAYPAL_SECRET_KEY_TEST
            PAYPAL_REEMBOLSO_URL_ = PAYPAL_REEMBOLSO_URL_TEST
        s = requests.Session()
        tokenPaypal = s.post(
            PREPARE_PAYPAL_URL_,
            data={
                "grant_type": "client_credentials"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            auth=HTTPBasicAuth(PAYPAL_CLIENT_ID_, PAYPAL_SECRET_KEY_)
        ).json()

        if not "access_token" in tokenPaypal:
            raise ValueError("Error en el proceso")

        s = requests.Session()
        paypal = s.post(
            PAYPAL_REEMBOLSO_URL_ % paypalCaptureId,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + tokenPaypal['access_token'],
                "PayPal-Request-Id": requestId
            }
        ).json()

        return paypal


def capture_transaction_paypal(url):
    from seguridad.models import Configuracion
    confi = Configuracion.get_instancia()
    if confi.paypal_modo:
        PREPARE_PAYPAL_URL_ = PREPARE_PAYPAL_URL
        PAYPAL_CLIENT_ID_ = PAYPAL_CLIENT_ID
        PAYPAL_SECRET_KEY_ = PAYPAL_SECRET_KEY
    else:
        PREPARE_PAYPAL_URL_ = PREPARE_PAYPAL_URL_TEST
        PAYPAL_CLIENT_ID_ = PAYPAL_CLIENT_ID_TEST
        PAYPAL_SECRET_KEY_ = PAYPAL_SECRET_KEY_TEST
    s = requests.Session()
    tokenPaypal = s.post(
        PREPARE_PAYPAL_URL_,
        data={
            "grant_type": "client_credentials"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        auth=HTTPBasicAuth(PAYPAL_CLIENT_ID_, PAYPAL_SECRET_KEY_)
    ).json()

    if not "access_token" in tokenPaypal:
        raise ValueError("Error en el proceso")

    s = requests.Session()
    paypal = s.post(
        url,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + tokenPaypal['access_token']
        }
    ).json()

    return paypal


@sync_to_async_function
def request_completar_pago_paypal(data: dict, request, pedido: Pedido):
    datos = {}
    try:
        from seguridad.models import Configuracion
        confi = Configuracion.get_instancia()
        if confi.paypal_modo:
            PREPARE_PAYPAL_URL_ = PREPARE_PAYPAL_URL
            PAYPAL_CLIENT_ID_ = PAYPAL_CLIENT_ID
            PAYPAL_SECRET_KEY_ = PAYPAL_SECRET_KEY
            PAYPAL_ORDER_URL_ = PAYPAL_ORDER_URL
            CONFIRM_PAYPAL_URL_ = CONFIRM_PAYPAL_URL
            PAYPAL_ORDER_DETAIL_URL_ = PAYPAL_ORDER_DETAIL_URL
        else:
            PREPARE_PAYPAL_URL_ = PREPARE_PAYPAL_URL_TEST
            PAYPAL_CLIENT_ID_ = PAYPAL_CLIENT_ID_TEST
            PAYPAL_SECRET_KEY_ = PAYPAL_SECRET_KEY_TEST
            PAYPAL_ORDER_URL_ = PAYPAL_ORDER_URL_TEST
            CONFIRM_PAYPAL_URL_ = CONFIRM_PAYPAL_URL_TEST
            PAYPAL_ORDER_DETAIL_URL_ = PAYPAL_ORDER_DETAIL_URL_TEST
        paypalCaptureId = ""
        s = requests.Session()
        tokenPaypal = s.post(
            PREPARE_PAYPAL_URL_,
            data={
                "grant_type": "client_credentials"
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            auth=HTTPBasicAuth(PAYPAL_CLIENT_ID_, PAYPAL_SECRET_KEY_)
        ).json()

        if not "access_token" in tokenPaypal:
            raise ValueError("Error al procesar el pago")

        s = requests.Session()
        order = s.get(
            PAYPAL_ORDER_URL_ % request.POST['orderID'],
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + tokenPaypal['access_token'],
            },
            auth=HTTPBasicAuth(PAYPAL_CLIENT_ID_, PAYPAL_SECRET_KEY_)
        ).json()

        if not (
                "purchase_units" in order and len(order['purchase_units']) > 0 and
                'amount' in order['purchase_units'][0] and
                Decimal(order['purchase_units'][0]['amount']['value']) == pedido.total and
                order['purchase_units'][0]['amount']['currency_code'] == data['NOMBRE_MONEDA']
        ):
            raise ValueError("El valor pagado no es el correcto")

        s = requests.Session()
        paypal = s.post(
            CONFIRM_PAYPAL_URL_ % request.POST['authorizationID'],
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + tokenPaypal['access_token'],
                "PayPal-Request-Id": str(pedido.id)
            }
        ).json()

        # if str(paypal.get('status')).upper() != "COMPLETED":
        #     raise ValueError("Error al procesar el pago")

        s = requests.Session()
        respPaypal = s.get(
            PAYPAL_ORDER_DETAIL_URL_ + "{}".format(request.POST['orderID']),
            headers={
                "Content-Type": "application/json",
            },
            auth=HTTPBasicAuth(PAYPAL_CLIENT_ID_, PAYPAL_SECRET_KEY_)
        ).json()

        if "captures" in respPaypal['purchase_units'][0]['payments']:
            paypalCaptureId = respPaypal['purchase_units'][0]["payments"]["captures"][0]["id"]
        else:
            for x in respPaypal['purchase_units'][0]['payments']['authorizations'][0]["links"]:
                if x["rel"].lower() == "capture":
                    capture = capture_transaction_paypal(x["href"])
                    paypalCaptureId = capture["id"]
                    break

        PagoPayPal.registrar(pedido, respPaypal, request.POST['orderID'],
                             request.POST['authorizationID'], paypalCaptureId)
        pedido.comprobante = "ID: {}, Órden: {}, # de Autorización: {}".format(paypal['id'],
                                                                                request.POST['orderID'],
                                                                                request.POST[
                                                                                    'authorizationID'])
        pedido.comprobantejson = json.dumps(
            {
                "id": paypal['id'],
                "orderId": request.POST['orderID'],
                "authorizationID": request.POST['authorizationID'],
                "paypalCaptureId": paypalCaptureId
            }
        )
        pedido.estado = "COMPLETADO"
        pedido.save()
        datos['mensaje_correo'] = "Nos complace decirte que tu compra fue procesada."
    except Exception as ex:
        pedido.estado = "ERROR_METODO_PAGO"
        pedido.save()
    HistorialPedido.objects.create(
        pedido_id=pedido.id,
        user_id=request.user.id,
        estado=pedido.estado,
        archivo=pedido.archivo_pago,
        detalle="PAGO #{} {}{} PAGADO CON {}, ESTADO: {}".format(pedido.id, data["SIMBOLO_MONEDA"],
                                                                   pedido.total,
                                                                   pedido.get_metodo_pago_display(),
                                                                   pedido.get_estado_display())
    )