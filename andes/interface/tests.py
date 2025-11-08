from django.test import TestCase
from django.utils import timezone
from interface.repositories.gas_maths import GasMaths
from interface.models import Sensor, GasRestante, ComposicionGas, CaracteristicasCilindro, ResultsGasRestante, TipoSensor, ServerCredentials

class GasMathsTestCase(TestCase):
    def setUp(self):
        # Create test data
        self.tipo_sensor = TipoSensor.objects.create(nombre="Test Type", descripcion="Test")
        self.server_cred = ServerCredentials.objects.create(
            nombre="Test Server",
            user="user",
            password="pass",
            authorization="auth",
            descripcion="desc"
        )
        self.sensor = Sensor.objects.create(
            tipoSensor=self.tipo_sensor,
            nombre="Test Sensor",
            estado=b'1'  # BinaryField for active
        )
        self.comp = ComposicionGas.objects.create(
            masa_molar=0.04901,
            y_entropia=1.13,
            z_factor=None,
            densidad=None
        )
        self.gr = GasRestante.objects.create(
            Sensor_idSensor=self.sensor,
            toleranciaMins=5,
            server_credentials=self.server_cred
        )
        self.cil = CaracteristicasCilindro.objects.create(
            volumen_interno_m3=1.0,
            masa_cil_vacio_kg=10.0,
            masa_cil_lleno_kg=50.0,
            masa_gas_restant_kg=40.0,
            coef_descarga_cd=0.62,
            diametro_orificio_m=0.01,
            notas="Test cylinder",
            ComposicionGas=self.comp,
            GasRestante=self.gr
        )

    def test_choked_calculation(self):
        gm = GasMaths()
        info = {
            "sensor_id": self.sensor.pk,
            "pressure": 100.0,  # psi
            "temperature": 300.0  # K
        }
        ctx = {
            "sensor_id": self.sensor.pk,
            "p0_abs_pa": 100 * 6894.757 + 101325,
            "p2_pa": 101325,
            "T0_K": 300.0,
            "gamma": 1.13,
            "R_spec": 8.314462618 / 0.04901,
            "cd": 0.62,
            "area_m2": 7.854e-5,
            "volumen_m3": 1.0,
            "cilindro": self.cil,
            "masa_lleno_kg": 50.0,
            "masa_tara_kg": 10.0,
            "masa_gas_restante_kg": 40.0,
            "M_kg_mol": 0.04901,
            "z_factor": None,
        }
        result = gm.choked(info=info, ctx=ctx)
        self.assertIn("mdot_kg_s", result)
        self.assertIn("masa_restante_kg", result)
        self.assertEqual(result["estado_fase"], "choked")

    def test_no_choked_calculation(self):
        gm = GasMaths()
        info = {
            "sensor_id": self.sensor.pk,
            "pressure": 50.0,  # psi, assuming not choked
            "temperature": 300.0
        }
        ctx = {
            "sensor_id": self.sensor.pk,
            "p0_abs_pa": 50 * 6894.757 + 101325,
            "p2_pa": 101325,
            "T0_K": 300.0,
            "gamma": 1.13,
            "R_spec": 8.314462618 / 0.04901,
            "cd": 0.62,
            "area_m2": 7.854e-5,
            "volumen_m3": 1.0,
            "cilindro": self.cil,
            "masa_lleno_kg": 50.0,
            "masa_tara_kg": 10.0,
            "masa_gas_restante_kg": 40.0,
            "M_kg_mol": 0.04901,
            "z_factor": None,
        }
        result = gm.no_choked(info=info, ctx=ctx)
        self.assertIn("mdot_kg_s", result)
        self.assertIn("masa_restante_kg", result)
        self.assertEqual(result["estado_fase"], "no_choked")

    def test_save_results(self):
        gm = GasMaths()
        info = {
            "sensor_id": self.sensor.pk,
            "pressure": 100.0,
            "temperature": 300.0
        }
        calc = {
            "sensor_id": self.sensor.pk,
            "cilindro": self.cil,
            "p0_abs_pa": 100 * 6894.757 + 101325,
            "T0_K": 300.0,
            "mdot_kg_s": 0.01,
            "masa_removida_kg": 0.6,
            "masa_restante_kg": 39.4,
            "porc_masa_gas_restant": 78.8,
            "estado_fase": "choked",
            "M_kg_mol": 0.04901,
        }
        initial_count = ResultsGasRestante.objects.count()
        result = gm.save_results(info=info, calc=calc, metodo="choked")
        self.assertIsNotNone(result)
        self.assertEqual(ResultsGasRestante.objects.count(), initial_count + 1)

    def test_save_low_pressure(self):
        gm = GasMaths()
        info = {
            "sensor_id": self.sensor.pk,
            "pressure": 3.0,  # low pressure
            "temperature": 300.0
        }
        ctx = {
            "sensor_id": self.sensor.pk,
            "cilindro": self.cil,
            "p0_abs_pa": 3 * 6894.757 + 101325,
            "T0_K": 300.0,
            "M_kg_mol": 0.04901,
        }
        initial_count = ResultsGasRestante.objects.count()
        result = gm.save_low_pressure(info=info, ctx=ctx)
        self.assertIsNotNone(result)
        self.assertEqual(ResultsGasRestante.objects.count(), initial_count + 1)

"""
Ejecuta en la carpeta raíz del proyecto Andes:

cd andes && DJANGO_SETTINGS_MODULE=andes.settings python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andes.settings')
import django
django.setup()

from interface.repositories.gas_maths import GasMaths
import math

# Test static methods without DB
ctx = {
    'area_m2': 7.854e-5,
    'cd': 0.62,
    'p0_abs_pa': 100 * 6894.757 + 101325,
    'p2_pa': 101325,
    'T0_K': 300.0,
    'gamma': 1.13,
    'R_spec': 8.314462618 / 0.04901,
    'masa_lleno_kg': 50.0,
    'masa_tara_kg': 10.0,
    'masa_gas_restante_kg': 40.0,
    'M_kg_mol': 0.04901,
}

# Test choked calc
result_choked = GasMaths._choked_calc(ctx=ctx)
print('Choked calc result:', result_choked['mdot_kg_s'], result_choked['estado_fase'])

# Test no choked calc
result_no_choked = GasMaths._no_choked_calc(ctx=ctx)
print('No choked calc result:', result_no_choked['mdot_kg_s'], result_no_choked['estado_fase'])

# Test is choked calc
sp = {
    'p_atm_pa': 101325,
    'gamma': 1.13,
    'M_kg_mol': 0.04901,
    'cd': 0.62,
    'area_m2': 7.854e-5,
    'volumen_m3': 1.0,
    'cilindro': None,
    'masa_lleno_kg': 50.0,
    'masa_tara_kg': 10.0,
    'masa_gas_restante_kg': 40.0,
    'z_factor': None,
    'diam_m': 0.01,
}
result_is_choked = GasMaths._is_choked_calc(sp=sp, sensor_id=1, P_gauge_psi=100.0, T0_K=300.0)
print('Is choked result:', result_is_choked['is_choked'], result_is_choked['skip_calc'])
"
        
"""