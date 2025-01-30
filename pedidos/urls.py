from django.urls import re_path
from pedidos.view_order_register import solicitudesRegistroView
from pedidos.view_pedido import pedidoView

pedidos_urls = (
    {
        "nombre": "Orders",
        "url": 'orders/',
        "vista": pedidoView,
    },

    {
        "nombre": "Registration requests",
        "url": 'solicitudes-registro/',
        "vista": solicitudesRegistroView,
    },
)

urlpatterns = [

]

for u in pedidos_urls:
    urlpatterns.append(re_path(r'^{}$'.format(u["url"]), u["vista"]))
