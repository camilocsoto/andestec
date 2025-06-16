# tasks.py en la app 'interface'

from celery import shared_task
from .utils import get_latest_data
from .utils import compare_dates

@shared_task
def check_and_update_data():
    # Verifica si los datos deben actualizarse
    if compare_dates():
        get_latest_data()
