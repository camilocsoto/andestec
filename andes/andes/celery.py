from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab



# Configura el módulo de configuración predeterminado para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andes.settings')

app = Celery('andes')
app.config_from_object('django.conf:settings', namespace='CELERY') # Carga la configuración de Django
app.autodiscover_tasks() # Autodiscover tasks.py en todas las apps registradas

# new service to update

app.conf.beat_schedule = {
    #'check-and-update-data-every-minute': {
    #    'task': 'interface.tasks.check_and_update_data',
    #    'schedule': crontab(minute='*/1'),  # Ejecuta cada minuto
    #},
    "refresh_toprie_credential_every_hour": {
        "task": "interface.tasks.token.refresh_toprie_credential",
        "schedule": crontab(minute='0'), 
        "args": (1,),  # cred.pk=1
    },
}
