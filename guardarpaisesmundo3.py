import os, sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pryictiair.settings')

application = get_wsgi_application()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from area_geografica.models import Pais, Provincia, Ciudad, Parroquia
from pryictiair.settings import BASE_DIR
from django.db import transaction

import json
from django.utils.text import slugify
with open(os.path.join(BASE_DIR, 'paises.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

if __name__ == '__main__':
    try:
        with transaction.atomic():
            Parroquia.objects.all().delete()
            Ciudad.objects.all().delete()
            Provincia.objects.all().delete()
            Pais.objects.all().delete()

            for p in data:
                npais = p["pais"].upper()
                if Pais.objects.filter(nombre=npais, status=True).exists():
                    pais = Pais.objects.get(nombre=npais, status=True)
                else:
                    pais = Pais.objects.create(nombre=npais)
                for e in p["estados"]:
                    nestado = e["nombre"].upper()
                    if Provincia.objects.filter(nombre=nestado, pais_id=pais.pk, status=True).exists():
                        estado = Provincia.objects.get(nombre=nestado, pais_id=pais.pk, status=True)
                    else:
                        estado = Provincia.objects.create(nombre=nestado, pais_id=pais.pk)
                    for c in e["ciudades"]:
                        nciudad = c["nombre"].upper()
                        if Ciudad.objects.filter(nombre=nciudad, provincia_id=estado.pk, status=True).exists():
                            ciudad = Ciudad.objects.get(nombre=nciudad, provincia_id=estado.pk, status=True)
                        else:
                            ciudad = Ciudad.objects.create(nombre=nciudad, provincia_id=estado.pk)

    except Exception as ex:
        print("Error: " + str(ex))