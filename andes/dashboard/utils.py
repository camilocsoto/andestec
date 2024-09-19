from django.shortcuts import get_object_or_404
from .models import Sensor, Variable, User
from api.utils import process_sensor_data
from .maths import Math

# libs to sent mails:
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

# PROCESS FROM API'S DATA TO THE DB
"""
#this should execute when the sensor is previous registered:
    data_from_api = {
        'deviceNo': 'YAVMMQYKDANVXPYU', 
        'pressure': '96.86',
        'temperature': '17.20',
        'battery': 97,
        'signal': 27,
        'heartbeatDate': '2024-08-28 03:30:41'
    }
OR process to keep information of the sensor.    
data_from_api = process_sensor_data()

"""


def get_data_sensor():
    # connect with utils (api) to bring the organized data.
    data_from_api = {
        "deviceNo": "YAVMMQYKDANVXPYU",
        "pressure": "82.5",
        "temperature": "17.15",
        "battery": 97,
        "signal": 27,
        "heartbeatDate": "2024-08-28 07:34:41",
    }
    return data_from_api


def search_last_item():
    try:
        # connect with the db to bring the last record in variables table
        last_object = Variable.objects.latest("id")
        threted_date = str(last_object.var_time).split("+")[0]
        return threted_date
    except Variable.DoesNotExist:
        # case: the sensors doesn't any keep data in the db
        # always commit the first record.
        return 0


def compare_dates():
    # add first register to variables table
    is_variable = search_last_item()
    if is_variable == 0:
        return process_information()

    # if exists data in variables table:
    sensor_date = get_data_sensor()
    if sensor_date["heartbeatDate"] == is_variable:
        # won't keep the same register in the db
        return f"{False} - porque db {is_variable} es igual a {sensor_date} o((>ω< ))o"
    else:
        return process_information()

def process_information():
    """
    
    MOST IMPORTANT:Steps to set the current quantity mass (kg) of gas
    If you wanna understand how, go to the math.py file.
    
    """
    try:
        data_from_api = get_data_sensor()
        # link the sensor where the variable belongs
        sensor = get_object_or_404(Sensor, sen_serialno=data_from_api["deviceNo"])
        # extract info of the specific sensor:
        _id = int(sensor.sen_id)
        # get its user_id foreign key
        sensor_instance = get_object_or_404(Sensor, sen_id=_id)

        # section to set the top glp quanitity -> 65% propane & 35% butane.
        
        object_capacity = float(sensor.max_masa)*453.6  # lb to gr.
        mass_quantity = object_capacity*0.85 # It's standard to avoid increasing 85% of the substance in a cylinder
        
        #section to set the current quantity mass (kg) of gas
        aP = float(data_from_api["pressure"])/14.69   # psi to atm
        T = float(data_from_api["temperature"]) + 273.15 # °C to °K
        
        #calculations
        maths = Math(T, aP)
        maths.molarVolume()
        gas_quantity = round(maths.gasQuantity(), 2) # g
        
        # Now, gas Quantity and mass_quantity define the % of gas.        
        current_percentage =(gas_quantity*100)/mass_quantity
        # internal pressure
        # sensor.max_output_force, when it brakes
        
        current_output_force = (float(data_from_api["pressure"])*100)/ float(sensor.max_output_force)

        return keep_information(
            sensor, sensor_instance, data_from_api, current_output_force, current_percentage, gas_quantity)
    except Exception as e:
        return f"error en process information {e}"


def keep_information(sensor, sensor_instance, data_from_api, current_output_force, current_percentage, gas_quantity):
    # Upload the database:
    Variable.objects.create(
        var_temperature=data_from_api["temperature"],
        var_radiofrecuency=data_from_api["signal"],
        var_presure=data_from_api["pressure"],
        var_time=data_from_api["heartbeatDate"],
        var_battery=data_from_api["battery"],
        localizacion="not available yet!",
        var_grams=gas_quantity,
        var_current_capacity=current_percentage,  # most important than anything
        var_output_capacity=current_output_force,
        sensors_sen_id=sensor_instance,  # use the instance here
    )
    if current_percentage > 1 or current_output_force < 80:
        return True
    else:
        return get_mail(sensor)


# ********************************************* MAIL ZONE **************************************************
def get_mail(sensor):
    """
    the param sensor works to get all the info of the sensor
    the variable user_id get the id of the user_id of its respective sensor
    the variable user get all the info of the respective user
    """
    user_id = sensor.user_us_id_id
    user = User.objects.get(id=user_id)
    return send_email(sensor, user)


def send_email(sensor, user):
    # ⛔ It should create a record in the table alerts
    user_name = user.us_name
    user_mail = user.us_mail
    sen_name = sensor.sen_name
    # Define el contexto para la plantilla
    context = {
        'user': user_name,
        'sensor_name': sen_name
    }
    try:
        # Obtiene la plantilla
        template = get_template('email_template.html')  # Ajusta la ruta si es necesario
        content = template.render(context)
        # Define el asunto del correo antes de crear el mensaje
        subject_mail = f"¡Alerta en el cilindro {sen_name}!"
        # Crea el mensaje de correo electrónico
        message = EmailMultiAlternatives(
            subject=subject_mail,
            body='',
            from_email=settings.EMAIL_HOST_USER,
            to=[user_mail],
            cc=[]
        )
        # Adjunta el contenido HTML
        message.attach_alternative(content, 'text/html')
        message.send()
        return True
    except Exception as e:
        return e
    