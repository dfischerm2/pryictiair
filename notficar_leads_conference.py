import os, sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pryictiair.settings')

application = get_wsgi_application()
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from landing.models import PersonNotificacion
from pryictiair.settings import BASE_DIR
from django.db import transaction

from time import sleep
from core.email_config import send_html_mail


def notificar_conference():
    try:
        personas_nn = PersonNotificacion.objects.all()[:1]
        per_error_nn = []
        count = 1
        # subject = 'DEADLINE REMINDER Call for Papers - ICTIAIR2025 | December 1st'
        subject = 'DEADLINE EXTENSION - Call for Papers - ICTIAIR2025 | December 22nd'

        for person in personas_nn:
            try:
                datos = {
                    'persona': person,
                }
                # to = person.email  # 'hllerenaa@unemi.edu.ec' #
                to = 'cozjosue0@gmail.com'  # 'hllerenaa@unemi.edu.ec' #
                send_html_mail(subject, "email/email_ictiair2.html", datos, [to], [], [])
                person.notified = True
                person.save()
                print(f"{count}.- Persona notificada: ({person.id}) {person.__str__()}")
                count += 1
                if count % 15 == 0:
                    sleep(15)
            except Exception as e:
                per_error_nn.append(person.id)
        print(f"Registros no notificados({len(per_error_nn)}): ", per_error_nn)
    except Exception as e:
        print(e)


notificar_conference()
