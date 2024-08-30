from django.shortcuts import get_object_or_404
from .models import Sensor, Variable
from api.utils import process_sensor_data
"""
#this should execute when the sensor is previous registered:
#process to keep information of the sensor.
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
        return process_information()
    
    # if exists data in variables table:
    sensor_date = get_data_sensor()
    if sensor_date['heartbeatDate'] == is_variable:
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
        sensor = get_object_or_404(Sensor, sen_serialno = data_from_api['deviceNo'])
        # extract info of the specific sensor:
        _id = int(sensor.sen_id)
        # create instance to foreign key
        sensor_instance = get_object_or_404(Sensor, sen_id=_id)
        
        sen_max_output_force = sensor.max_output_force # in the forms transform(kPa -> psi)
        # Current output force
        P = data_from_api['pressure'] #(psi)
        Prel = float(P[0])
        # section to set the max volume -> 65% propane & 35% butane.
        gas_density = 0.524 # g/cm^3
        mass_capacity = sensor.max_masa # kg
        max_volume = (mass_capacity*1000)/gas_density #cm^3
        
        #section to set the current volume 
        # aP -> psi to Pa
        aP = float(data_from_api['pressure']) * 6894
        
        if aP > 0:
            # T -> °C to °K
            T = float(data_from_api['temperature']) + 273,15
            if T[0] >= 288.15 and T[0] <= 298.15:
                #boyl's law under normal conditions V(1) = P(1)*V(2)/P(2)
                current_volume = (aP * max_volume)/sen_max_output_force
                #rule of 3 🖖
                current_percentage = (current_volume*100)/max_volume
                
                #output force
                current_output_force = (Prel/float(sen_max_output_force))*100 #🟠
                
            else: 
                # ⚡no normal conditions
                #Charles's law V(2) = V(1)*T(2)/T(1)
                V_normal_c = max_volume
                T_normal_c = 293.15
                new_max_volume = (V_normal_c*T_normal_c)/T[0]
                
                #Gay-Lussac's law P(2) = P(1)*T(2)/T(1)
                new_max_pressure = (sen_max_output_force*T[0])/T_normal_c
                
                #boyl's law under no normal conditions V(1) = P(1)*V(2)/P(2)
                current_volume = (aP * new_max_volume)/new_max_pressure
                #rule of 3 to set the %
                current_percentage = (current_volume*100)/new_max_volume
                
                #output force
                current_output_force = (Prel/new_max_volume)*100 
        else:
            current_output_force = 0
            current_percentage = 0
            
        return keep_information(sensor_instance, data_from_api, Prel, current_output_force, current_percentage)
    except Exception:
        return False
    

def keep_information(sensor_instance, data_from_api, Prel, current_output_force, current_percentage):
    # Upload the database: 
    Variable.objects.create(
        var_temperature = data_from_api['temperature'],
        var_radiofrecuency = data_from_api['signal'],
        var_presure = Prel,
        var_time = data_from_api['heartbeatDate'], 
        var_battery =data_from_api['battery'],
        localizacion = "not available yet!",
        var_current_capacity = current_percentage, #most important than anything
        var_output_capacity = current_output_force, 
        sensors_sen_id = sensor_instance, #use the instance here   
        )
    return True
    # keep the threated information.
     
    
    