from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Configura el módulo de configuración predeterminado para Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andes.settings')

app = Celery('andes')

# Carga la configuración de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodiscover tasks.py en todas las apps registradas
app.autodiscover_tasks()

# new service to update

app.conf.beat_schedule = {
    'check-and-update-data-every-minute': {
        'task': 'interface.tasks.check_and_update_data',
        'schedule': crontab(minute='*/1'),  # Ejecuta cada minuto
    },
}
