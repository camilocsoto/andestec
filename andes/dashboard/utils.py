from django.shortcuts import get_object_or_404
from .models import Sensor, Variable
from api.utils import process_sensor_data
"""
this should execute when the sensor is previous registered:
process to keep information of the sensor.
        data_from_api = {
        'deviceNo': 'YAVMMQYKDANVXPYU', 
        'pressure': '96.86',
        'temperature': '17.20',
        'battery': 97,
        'signal': 27,
        'heartbeatDate': '2024-08-20 12:26:48+00:00'
        }

"""
def get_data_sensor():
    #connect with utils (api) to bring the organized data.
    data_from_api = process_sensor_data()
    return data_from_api

def search_last_item():
    try:
        # connect with the db to bring the last record in variables table
        last_object = Variable.objects.latest('id')
        threted_date = str(last_object.var_time).split('+')[0]
        return threted_date
    except Variable.DoesNotExist:
        # case: the sensors doesn't any keep data in the db 
        # always commit the first record.
        return 0
    
def compare_dates():
    # add first register to variables table
    is_variable = search_last_item()
    if is_variable == 0:
        return keep_variables()
    
    # if exists data in variables table:
    sensor_date = get_data_sensor()
    if sensor_date['heartbeatDate'] == is_variable:
        # won't keep the same register in the db
        return False
    else:
        return keep_variables()

    
def keep_variables():
# 🟠 processing information and make every operation to upload the data at variables table. 
    try:
        data_from_api = get_data_sensor()
        # link the sensor where the variable belongs
        sensor = get_object_or_404(Sensor, sen_serialno = data_from_api['deviceNo'])
        # extract info of the specific sensor:
        _id = int(sensor.sen_id)
        sen_max_output_force = sensor.max_output_force
        """
        steps to find the current output of gas
        1° you gotta find the relative preassure: Prel = Pmed + Patm
        Where:
        Prel = real pressure of the bowl in psi
        Pmed = data_from_api['pressure'] in psi
        Patm = 14,7 psi
        2° rule of 3 => get the % of gas: (Prel/sen_max_output_force)*100
        """
        Prel = float(data_from_api['pressure']) + 14,7
        current_output_force = (Prel[0]/float(sen_max_output_force))*100
        
        """
        MOST IMPORTANT:Steps to set the current porcentage of gas
        max_volume = mass of the cylinder (kg)/ gas density (kg/m^3)
        current_volume = (n * R * T)/ aP
        n = mass of cylinder (g) / molas mass of gas (g/mol)
        R = constant of noble gases
        T = current temperature from sensor (K)
        aP = current pressure data from sensor (Pa)
        """
        # section to set the first material and find the max volume -> 65% propane & 35% butane.
        gas_density = 2.14 # kg/m^3
        molar_mass = 49 #g/mol
        mass_capacity = sensor.max_masa # kg
        #section to convert the units and find the current volume 
        # aP -> psi to Pa
        aP = float(data_from_api['pressure']) * 6894 
        # T -> °C to °K
        T = float(data_from_api['temperature']) + 273,15 #exec it as T[0]
        # R -> (J/mol*k)
        R = 8.314
        # n -> (kg -> g) to (1/mol)
        n = (mass_capacity*1000)/molar_mass
        # get the volumes
        max_volume = mass_capacity/gas_density
        current_volume = (n * R * T[0])/aP
        # rule of 3 🖖
        current_percentage = (current_volume*100)/max_volume
        # create instance to foreign key
        sensor_instance = get_object_or_404(Sensor, sen_id=_id)
        # Upload the database: 
        Variable.objects.create(
            var_temperature = data_from_api['temperature'],
            var_radiofrecuency = data_from_api['signal'],
            var_presure = Prel[0],
            var_time = data_from_api['heartbeatDate'], 
            var_battery =data_from_api['battery'],
            localizacion = "not available yet!",
            var_current_capacity = current_percentage, #most important than anything
            var_output_capacity = current_output_force, 
            sensors_sen_id = sensor_instance, #use the instance here
            
        )
        return True
    except Exception as e:
        return e
    
    # keep the threated information.
     
    
    