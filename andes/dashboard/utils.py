from django.shortcuts import get_object_or_404
from .models import Sensor, Variable, User
from api.utils import process_sensor_data

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
        "pressure": "1.53",
        "temperature": "-273.15",
        "battery": 97,
        "signal": 27,
        "heartbeatDate": "2024-08-28 06:34:41",
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
        return False
    else:
        return process_information()


def process_information():
    """
    MOST IMPORTANT:Steps to set the current Volume (L) of gas
    1. Calcule the maximum volume of gas in the cylinder:
    max_volume = mass of the cylinder (g)/ gas density (g/cm^3)
    2. Calculate the current volume of gas in the cylinder under normal conditions:
    #boyl's law under normal conditions V(1) = P(1)*V(2)/P(2)
    3. Calculate the current volume of gas in the cylinder under no normal conditions:
    #Charles's law V(2) = V(1)*T(2)/T(1)
    #Gay-Lussac's law P(2) = P(1)*T(2)/T(1)
    #boyl's law under no normal conditions V(1) = P(1)*V(2)/P(2)
    4. Use the rule of three.
    -----------------------------------------------------------------
    steps to find the current output of gas
    Prel = real pressure of the bowl in psi
    2° rule of 3 => get the % of gas: (Prel/sen_max_output_force)*100
    """
    try:
        data_from_api = get_data_sensor()
        # link the sensor where the variable belongs
        sensor = get_object_or_404(Sensor, sen_serialno=data_from_api["deviceNo"])
        # extract info of the specific sensor:
        _id = int(sensor.sen_id)
        # get its user_id foreign key
        sensor_instance = get_object_or_404(Sensor, sen_id=_id)

        sen_max_output_force = (
            sensor.max_output_force
        )  # in the forms transform(kPa -> psi)
        # section to set the max volume -> 65% propane & 35% butane.
        gas_density = 0.524  # g/cm^3
        mass_capacity = sensor.max_masa  # kg
        max_volume = (mass_capacity * 1000) / gas_density  # cm^3

        # section to set the current volume
        # aP -> psi
        aP = float(data_from_api["pressure"])  # (psi)
        # T -> °C to °K
        T = float(data_from_api["temperature"]) + 273.15

        if aP >= 0 and T >= 1:
            if T >= 288.15 and T <= 298.15:
                # boyl's law under normal conditions V(1) = P(1)*V(2)/P(2)
                current_volume = (aP * max_volume) / sen_max_output_force
                # rule of 3 🖖
                current_percentage = (current_volume * 100) / max_volume

                # output force
                current_output_force = (aP * 100) / sen_max_output_force  # 🟠
            else:
                # ⚡no normal conditions
                # Charles's law V(2) = V(1)*T(2)/T(1)
                V_normal_c = max_volume
                T_normal_c = 293.15
                new_max_volume = (V_normal_c * T_normal_c) / T

                # Gay-Lussac's law P(2) = P(1)*T(2)/T(1)
                new_max_pressure = (sen_max_output_force * T) / T_normal_c

                # boyl's law under no normal conditions V(1) = P(1)*V(2)/P(2)
                current_volume = (aP * new_max_volume) / new_max_pressure
                # rule of 3 to set the %
                current_percentage = (current_volume * 100) / new_max_volume

                # output force
                current_output_force = (aP * 100) / new_max_volume
        else:
            current_volume = 0
            current_output_force = 0
            current_percentage = 0

        return keep_information(
            sensor,
            sensor_instance,
            data_from_api,
            aP,
            current_output_force,
            current_percentage,
            current_volume,
        )
    except Exception as e:
        return e


def keep_information(sensor, sensor_instance, data_from_api, aP, current_output_force, current_percentage, current_volume):
    # Upload the database:
    Variable.objects.create(
        var_temperature=data_from_api["temperature"],
        var_radiofrecuency=data_from_api["signal"],
        var_presure=aP,
        var_time=data_from_api["heartbeatDate"],
        var_battery=data_from_api["battery"],
        localizacion="not available yet!",
        var_litres=current_volume,
        var_current_capacity=current_percentage,  # most important than anything
        var_output_capacity=current_output_force,
        sensors_sen_id=sensor_instance,  # use the instance here
    )
    if current_percentage > 1 or current_output_force < 0:
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
    