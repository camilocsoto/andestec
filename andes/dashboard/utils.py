from django.shortcuts import get_object_or_404
from interface.models import Sensor, Variable, User
from interface.sensors import process_sensor_data
from .maths import Math

# libs to sent mails:
from django.conf import settings
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives

# PROCESS FROM API'S DATA TO THE DB
"""
#this should execute when the sensor is previous registered:
    data_from_api = {
        "deviceNo": "YAVMMQYKDANVXPYU",
        "pressure": "11.5",
        "temperature": "15.15",
        "battery": 97,
        "signal": 27,
        "heartbeatDate": "2024-08-29 07:34:41",
        "lat": "4.294071",
        "lng": "-74.028749"
    }
OR process to keep information of the sensor.    
data_from_api = process_sensor_data()

"""

def get_data_sensor():
    # connect with utils (api) to bring the organized data.
    data_from_api = process_sensor_data()
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
        #when is the first register, it has to been configured by itself. 🟠
        return process_information()

    # if exists data in variables table:
    sensor_date = get_data_sensor()
    if sensor_date["heartbeatDate"] == is_variable:
        # won't keep the same register in the db
        return False
    else:
        return process_information()

def process_information():
    """
    1. The first part of the function, link the information of the db with the current info.
    2. Transform the total mass, the pressure and the temperature to international units.
    3. The total volume is calculated with the compressibility factor (z), the max pressure and the max mol's quantity.
    4. The current mol's quantity (n) is calculated with the current pressure.
    5. The Avogadro's law let us find the current volume.
    6. Calculate the % of volume and pressure.
    """
    try: # first part of the function
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
        max_pressure = float(round(sensor.max_output_force, 2))
        #section to set the current quantity mass (kg) of gas
        aP = float(data_from_api["pressure"])/14.69   # psi to atm
        T = float(data_from_api["temperature"]) + 273.15 # °C to °K
        
        # section to set the total volume
        t_volume = Math(T, max_pressure)
        z = t_volume.getZ()
        n_max = float(mass_quantity)/49.01
        total_volume = (z*n_max*0.082*T)/max_pressure
        #calculations
        maths = Math(T, aP) # maths = Math(290.15, 0.54) print(maths.getZ())
        gas_quantity = round(maths.gasQuantity(total_volume), 2) # mol
        current_volume = maths.avogadro_law(total_volume, n_max, gas_quantity) # L
        
        # Now, gas Quantity and mass_quantity define the % of gas.        
        current_percentage =(current_volume*100)/total_volume
        current_output_force = (aP*100)/ max_pressure
        return keep_information(
            sensor, sensor_instance, data_from_api, current_output_force, current_percentage, current_volume)
    except:
        return False

def keep_information(sensor, sensor_instance, data_from_api, current_output_force, current_percentage, current_volume):
    # Upload the database:
    Variable.objects.create(
        var_temperature=data_from_api["temperature"],
        var_radiofrecuency=data_from_api["signal"],
        var_presure=data_from_api["pressure"],
        var_time=data_from_api["heartbeatDate"],
        var_battery=data_from_api["battery"],
        localizacion= f'{data_from_api["lat"]} {data_from_api["lng"]}',
        var_litres=current_volume,
        var_current_capacity=current_percentage,  # most important than anything
        var_output_capacity=current_output_force,
        sensors_sen_id=sensor_instance,  # use the instance here
    )
    if current_percentage > 9 or current_output_force >20:
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
    