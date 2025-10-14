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
    "refresh_toprie_credential_every_hour": {
        "task": "interface.tasks.token.refresh_toprie_credential",
        "schedule": crontab(minute='0'), 
        "args": (1,),  # cred.pk=1
    },
    "eval_connection_every_3_min": {
        "task": "interface.tasks.eval_conn.eval_connection",
        "schedule": crontab(minute="*/3"),
    },
    "connect_sensor_each_1_min": {
        "task": "interface.tasks.conn_sen.connect_sensor",
        "schedule": crontab(minute="*/1")
    },
}
