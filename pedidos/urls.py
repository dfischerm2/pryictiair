from django.urls import re_path
from pedidos.view_pedido import solicitudesRegistroView

pedidos_urls = (

    {
        "nombre": "Solicitudes de registro",
        "url": 'solicitudes-registro/',
        "vista": solicitudesRegistroView,
    },
)

urlpatterns = [

]

for u in pedidos_urls:
    urlpatterns.append(re_path(r'^{}$'.format(u["url"]), u["vista"]))
