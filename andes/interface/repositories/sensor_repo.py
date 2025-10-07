from ..models import Sensor, GasRestante, TipoSensor, CaracteristicasCilindro, ComposicionGas, ResultsGasRestante
from typing import Tuple, Dict, Any, List, Optional
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import OuterRef, Subquery, QuerySet
from django.db import transaction
import json
class SensorTPRepository:
    
    def get_all(self):
        return Sensor.objects.all()
    
    def get_sensor_with_related(self, pk: int) -> Sensor:
        return Sensor.objects.select_related("empresa", "tipoSensor").get(pk=pk)

    @transaction.atomic
    def create_gas_tp_sensor( self, *, nombre: str | None, estado_bytes: bytes | None, empresa, tipo_id: int, localizacion: str | None, bateria: str | None, server_deviceNo: str | None, server_credentials) -> Sensor:
        """Crea Sensor + GasRestante para tipoSensor"""
        tipo = TipoSensor.objects.get(pk=tipo_id)
        sensor = Sensor.objects.create(
            nombre=nombre,
            estado=estado_bytes,
            empresa=empresa,
            tipoSensor=tipo,
        )
        GasRestante.objects.create(
            Sensor_idSensor=sensor,
            localizacion=localizacion,
            bateria=bateria,
            server_deviceNo=server_deviceNo,
            server_credentials=server_credentials,
        )
        return sensor
    
    @transaction.atomic
    def update_gas_tpsensor( self, *, sensor_id: int, nombre, estado_bytes, empresa, localizacion, bateria, server_deviceNo, server_credentials) -> Sensor:
        sensor = Sensor.objects.select_for_update().select_related("tipoSensor").get(pk=sensor_id)
        # actualizar Sensor
        sensor.nombre = nombre
        sensor.estado = estado_bytes
        sensor.empresa = empresa
        sensor.save(update_fields=["nombre", "estado", "empresa"])

        # actualizar GasRestante (pk = sensor)
        gas = GasRestante.objects.select_for_update().get(Sensor_idSensor_id=sensor_id)
        gas.localizacion = localizacion
        gas.bateria = bateria
        gas.server_deviceNo = server_deviceNo
        gas.server_credentials = server_credentials
        gas.save(update_fields=["localizacion", "bateria", "server_deviceNo", "server_credentials"])
        return sensor
    
    @transaction.atomic
    def delete_sensor(self, sensor_id: int) -> int:
        """
        Borra el sensor (y en cascada GasRestante). Devuelve cantidad eliminada (1 si ok).
        """
        try:
            obj = Sensor.objects.select_for_update().get(pk=sensor_id)
        except ObjectDoesNotExist:
            return 0
        obj.delete()  # GasRestante cae por cascade
        return 1
    
class SensorTPDetailRepository:
    def get_sensor_base(self, sensor_id: int) -> Sensor:
        return (Sensor.objects
                .select_related("empresa__usuario", "tipoSensor")
                .get(pk=sensor_id))

    def get_gasrestante_for_sensor(self, sensor_id: int) -> GasRestante | None:
        try:
            return (GasRestante.objects
                    .select_related("server_credentials", "Sensor_idSensor")
                    .get(Sensor_idSensor_id=sensor_id))
        except GasRestante.DoesNotExist:
            return None

    def get_cylinders_with_latest_result(self, gas: GasRestante) -> Tuple[QuerySet, Dict[int, ResultsGasRestante]]:
        """
        Devuelve (cilindros_qs, latest_results_map)
        - cilindros_qs: queryset de CaracteristicasCilindro anotado con latest_result_id
        - latest_results_map: dict {latest_result_id: ResultsGasRestante}
        """
        if gas is None:
            return CaracteristicasCilindro.objects.none(), {}

        latest_result_subq = (
            ResultsGasRestante.objects
            .filter(CaracterísticasCilindro=OuterRef('pk'))
            .order_by('-timestamp')
            .values('id')[:1]
        )

        cilindros_qs = (
            CaracteristicasCilindro.objects
            .select_related('ComposicionGas', 'GasRestante')
            .filter(GasRestante=gas)
            .annotate(latest_result_id=Subquery(latest_result_subq))
        )

        # Extraer los ids anotados sin acceder a atributos dinámicos en instancias
        ids_qs = cilindros_qs.values_list('latest_result_id', flat=True)
        # materializar y filtrar None/0/'' (lo que sea no válido)
        ids = [int(i) for i in ids_qs if i]

        latest_results = ResultsGasRestante.objects.in_bulk(ids) if ids else {}

        return cilindros_qs, latest_results
    
    
class GasDashboardRepository:
    def _get_gas_by_sensor(self, sensor_id: int) -> Optional[GasRestante]:
        try:
            return (GasRestante.objects.select_related("Sensor_idSensor", "server_credentials").get(Sensor_idSensor_id=sensor_id))
        except GasRestante.DoesNotExist:
            return None

    def _get_primary_cylinder(self, gas: GasRestante) -> Optional[CaracteristicasCilindro]:
        return (CaracteristicasCilindro.objects.select_related("ComposicionGas", "GasRestante").filter(GasRestante=gas).order_by("pk").first())

    def latest_5_reg(self, *, sensor_id: int) -> Dict[str, Any]:
        """
        Construye el contexto para la estrategia 'latest_5_reg':
        - Un cilindro 'principal' asociado al sensor.
        - Su ComposicionGas .
        - Últimos 5 ResultsGasRestante del cilindro.
        """
        gas = self._get_gas_by_sensor(sensor_id)
        cyl = self._get_primary_cylinder(gas) if gas else None

        # Composición | None
        comp = cyl.ComposicionGas if cyl else None
        comp_ctx: Optional[Dict[str, Any]] = None
        if comp:
            comp_ctx = {
                "nombre": comp.nombre,
                "descripcion": comp.descripcion,
                "masa_molar": comp.masa_molar,
                "y_entropia": comp.y_entropia,
                "z_factor": comp.z_factor,
                "densidad": comp.densidad,
            }
        # Últimos 5 regs o menos
        results_qs: QuerySet[ResultsGasRestante] = ResultsGasRestante.objects.none()
        if cyl:
            results_qs = (ResultsGasRestante.objects.select_related("CaracterísticasCilindro").filter(CaracterísticasCilindro=cyl).order_by("-timestamp")[:5])
        results_ctx: List[Dict[str, Any]] = [
            {
                "timestamp": r.timestamp,
                "presion_gauge_pa": r.presion_gauge_pa,
                "presion_abs_pa": r.presion_abs_pa,
                "temperature_k": r.temperature_k,
                "estado_fase": r.estado_fase,
                "caudal_masa_kg_s": r.caudal_masa_kg_s,
                "masa_remov_kg": r.masa_remov_kg,
                "masa_restante_kg": r.masa_restante_kg,
                "moles_restantes_kg": r.moles_restantes_kg,
                "metodo_calculo": r.metodo_calculo,
                "masa_balanza_kg": r.masa_balanza_kg,
                "porc_masa_gas_restant":r.porc_masa_gas_restant,
                "valido": r.valido,
            }
            for r in results_qs
        ]
        # order results_ctx for charts
        results_sorted = sorted(results_ctx, key=lambda x: x["timestamp"] or 0)

        labels = [ (v["timestamp"].isoformat() if v["timestamp"] else None) for v in results_sorted ]
        charts_payload = {
            "labels": labels,
            "series": {
                # agrega/ajusta las series que vayas a graficar
                "presion_gauge_pa": [ v["presion_gauge_pa"] for v in results_sorted ],
                "presion_abs_pa":   [ v["presion_abs_pa"]   for v in results_sorted ],
                "temperature_k":    [ v["temperature_k"]    for v in results_sorted ],
                "caudal_masa_kg_s": [ v["caudal_masa_kg_s"] for v in results_sorted ],
                "masa_remov_kg":    [ v["masa_remov_kg"]    for v in results_sorted ],
                "masa_restante_kg": [ v["masa_restante_kg"] for v in results_sorted ],
                "porc_masa_gas_restant": [v["porc_masa_gas_restant"] for v in results_sorted],                
            },
        }
        charts_json = json.dumps(charts_payload, default=str)  # default=str para serializar datetimes
        
        return {
            "sensor_id": sensor_id,
            "gas": {
                "ubicacion": getattr(gas, "localizacion", None) if gas else None, 
                "bateria": getattr(gas, "bateria", None) if gas else None,
                "server_deviceNo": getattr(gas, "server_deviceNo", None) if gas else None,
            } if gas else None,
            "cilindro": {
                "id": getattr(cyl, "pk", None),
                "nombre": getattr(cyl, "nombre", None) if cyl else None,
                "notas": getattr(cyl, "notas", None) if cyl else None
            } if cyl else None,
            "composicion_gas": comp_ctx,
            "list_info": results_ctx,      # lista (0..5)
            "charts": charts_payload, 
            "charts_json": charts_json,    # string JSON
        }
        