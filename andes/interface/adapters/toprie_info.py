import requests
from typing import Dict, Any, Optional


class ToprieInfoAdapter:
    def __init__(self, *, server_clientId: str, authorization: str, server_userId: str, server_deviceNo: str):
        self.server_clientId = server_clientId
        self.authorization   = authorization
        self.server_userId   = server_userId
        self.server_deviceNo = server_deviceNo
        self.base_url = "https://app.dtuip.com"

    def getSingleDeviceDatas(self) -> Dict[str, Any]:
        url = f"{self.base_url}/api/device/getSingleDeviceDatas"
        headers = {
            "tlinkAppId": self.server_clientId,
            "Authorization": self.authorization,
        }
        body = {
            "userId": self.server_userId,
            "deviceNo": self.server_deviceNo,
            "currPage": 1,
            "pageSize": 10,
        }
        try:
            r = requests.post(url, headers=headers, json=body)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching device data: {e}. the info received was: {headers['tlinkAppId']}, {headers['Authorization']}, {body['userId']}, {body['deviceNo']}")
            return {}

    def transform_info(self) -> Dict[str, Any] | None:
        """
        Devuelve el dict procesado:
        {
          'deviceNo': str,
          'pressure': float|str|None,
          'temperature': float|str|None,
          'battery': float|str|None,
          'signal': float|str|None,
          'iccid': str|None,
          'heartbeatDate': 'YYYY-MM-DD HH:MM:SS' | None,
          'lat': float|None,
          'lng': float|None,
        }
        """
        data = self.getSingleDeviceDatas()
        device = data.get("device") or {}
        sensors = device.get("sensorsList") or []

        processed: Dict[str, Any] = {
            "deviceNo": device.get("deviceNo"),
            "pressure": None,
            "temperature": None,
            "battery": None,
            "signal": None,
            "iccid": None,
            "heartbeatDate": None,
            "lat": device.get("lat"),
            "lng": device.get("lng"),
        }
        # heartbeatDate (si viene en primer sensor)
        if sensors:
            processed["heartbeatDate"] = sensors[0].get("heartbeatDate")

        for s in sensors:
            name = s.get("sensorName")
            val  = s.get("value")
            if name == "压力":         # presión
                processed["pressure"] = 85.5 #val just to simulate.
            elif name == "温度":       # temperatura
                processed["temperature"] = val
            elif name == "电量":       # batería
                processed["battery"] = val
            elif name == "信号":       # señal
                processed["signal"] = val
            elif name == "流量卡":     # ICCID
                processed["iccid"] = val

        return processed
