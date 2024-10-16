import os, sys
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pryictiair.settings')

application = get_wsgi_application()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from landing.models import PersonNotificacion
from pryictiair.settings import BASE_DIR
from django.db import transaction


def notificar_conference():
    try:
        personas_nn = PersonNotificacion.objects.filter(notified=False)
        per_error_nn = []
        count = 1
        for person in personas_nn:
            try:
                print(f"{count}.- Persona notificada: ({person.id}) {person.__str__()}")
                count += 1
            except Exception as e:
                per_error_nn.append(person.id)
        print(f"Registros no notificados({len(per_error_nn)}): ", per_error_nn)
    except Exception as e:
        print(e)


notificar_conference()
