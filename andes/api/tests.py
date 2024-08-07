import unittest
from unittest.mock import patch
import requests
from .utils import get_access_token, getSingleDeviceDatas  # Importar la función desde el módulo correcto

class TestGetAccessToken(unittest.TestCase):
# GET THE TOKEN FROM THE SERVER OF EATEC
    @patch('api.utils.requests.post')
    def test_get_access_token_success(self, mock_post):
        # Configurar el mock para simular una respuesta exitosa
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'fake_token'}

        token = get_access_token()
        self.assertEqual(token, 'fake_token')

    @patch('api.utils.requests.post')
    def test_get_access_token_failure(self, mock_post):
        # Configurar el mock para simular una respuesta fallida
        mock_response = mock_post.return_value
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with self.assertRaises(requests.exceptions.HTTPError):
            get_access_token()
            
# --------------------------------------------------------------------------------------
class TestGetSingleDeviceDatas(unittest.TestCase):
    # It should return the 
    @patch('api.utils.requests.post')
    @patch('api.utils.get_access_token', return_value='fake_token')  # Mockear get_access_token
    def test_getSingleDeviceDatas_success(self, mock_get_access_token, mock_post):
        # Configurar el mock para simular una respuesta exitosa
        mock_response = mock_post.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "deviceData": "some_device_data"
            }
        }

        data = getSingleDeviceDatas()
        self.assertEqual(data['data']['deviceData'], 'some_device_data')

    @patch('api.utils.requests.post')
    @patch('api.utils.get_access_token', return_value='fake_token')  # Mockear get_access_token
    def test_getSingleDeviceDatas_failure(self, mock_get_access_token, mock_post):
        # Configurar el mock para simular una respuesta fallida
        mock_response = mock_post.return_value
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

        with self.assertRaises(requests.exceptions.HTTPError):
            getSingleDeviceDatas()

if __name__ == '__main__':
    unittest.main()
    # run it with: python3 manage.py test api