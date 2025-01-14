from django.urls import re_path

from financiero.view_cuentafinanciera import cuentaFinancieraView
from financiero.view_entidadfinanciera import entidadFinancieraView
financiero_urls = (
    {
        "nombre": "Entidad Financiera",
        "url": 'entidad-financiera/',
        "vista": entidadFinancieraView,
    },
    {
        "nombre": "Cuentas Financieras",
        "url": 'cuentas-financieras/',
        "vista": cuentaFinancieraView,
    },
)

urlpatterns = [

]


for u in financiero_urls:
    urlpatterns.append(re_path(r'^{}$'.format(u["url"]), u["vista"]))
