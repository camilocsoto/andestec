import requests
from dotenv import load_dotenv
import os
"""
THIS FILE HAS THE CONNECTION TO THE API TO GET THE TOKEN.
ALL THE SENSITIVE VARIABLES ARE LOCATED IN A ENVIRONMENT VARIABLES FILE
"""

load_dotenv()

def get_access_token():
    #this take the token that changes currently
    url = 'https://app.dtuip.com/oauth/token'
    params = {
        'grant_type': 'password',
        'username': os.getenv('USERNAME'),
        'password': os.getenv('PASSWORD')
    }
    headers = {
        'Authorization': os.getenv('AUTHORIZATION')
    }

    response = requests.post(url, headers=headers, params=params)
    response.raise_for_status() 

    data = response.json()
    return data.get('access_token')

def getSingleDeviceDatas():
    # it gives the long JSON. That we shall to extract its data
    url = 'https://app.dtuip.com/api/device/getSingleDeviceDatas'
    headers = {
        'tlinkAppId': os.getenv('TLINKAPPID'),
        'Authorization': f"bearer {get_access_token()}" # 🟠 Bearer may change in the future.
    }
    body = {
        "userId": os.getenv('USERID'),
        "deviceNo": "YAVMMQYKDANVXPYU", # 🟠🦠 this value should change dynamically
        "currPage": 1,
        "pageSize": 10
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()

    data = response.json()
    return data


def process_sensor_data():
    # This return a dictionary that has every important data
    data = getSingleDeviceDatas()
    sensors = data['device']['sensorsList']
    processed_data = {
        'deviceNo': data['device']['deviceNo'],  # ID of sensor
        'pressure': None,
        'temperature': None,
        'battery': None,
        'signal': None,
        'iccid': None,
        'heartbeatDate':data['device']['sensorsList'][0]['heartbeatDate'],
        'lat': data['device']['lat'],
        'lng': data['device']['lng']
    }

    for sensor in sensors:
        if sensor['sensorName'] == "压力":  # presión
            processed_data['pressure'] = sensor['value']
        elif sensor['sensorName'] == "温度":  # temperatura
            processed_data['temperature'] = sensor['value']
        elif sensor['sensorName'] == "电量":  # batería
            processed_data['battery'] = sensor['value']
        elif sensor['sensorName'] == "信号":  # señal
            processed_data['signal'] = sensor['value']
        elif sensor['sensorName'] == "流量卡":  # ICCID
            processed_data['iccid'] = sensor['value']
    
    return processed_data
