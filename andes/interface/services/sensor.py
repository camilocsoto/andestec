from ..repositories.sensor_repo import SensorTPRepository
from ..strategies.sensor import SensorStrategy, SensorDetailStrategy, DetailSensor, SelectpDataStrategy, ConnectionEvalStrategy
from ..models import Sensor, GasRestante, TipoSensor
from typing import cast, Dict, Any
from django.db.models import QuerySet

from io import BytesIO
from datetime import datetime
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from django.utils.text import slugify
from typing import Dict, Any, List, Tuple
from django.utils import timezone as djtz
from ..strategies.sensor import SelectpDataStrategy
from openpyxl.worksheet.worksheet import Worksheet

class SensorService:
    """
    class used for orchestration of sensor operations such as:
    - 
    """
    def __init__(self):
        self.repo = SensorTPRepository() # just to list all sensors in admin menu
        self.strategy = SensorStrategy()
        self.reportStrategy = SelectpDataStrategy()
        self.detail_strategy = SensorDetailStrategy()
        self.conn_strategy = ConnectionEvalStrategy()

    def get_all_sensors(self): 
        # list all sensors to the admins view
        return self.repo.get_all()
    
    def create_sensor(self, *, tipo_id: int, data: dict) -> Sensor:
        """
        data viene de form.cleaned_data. Strategy elige form/repo/plantilla.
        """
        cfg = self.strategy.resolve(tipo_id)
        repo = cfg["repo"]
        sensor = repo(tipo_id=tipo_id, data=data)
        return sensor
    
    # update
    def _resolve_cfg_by_sensor(self, sensor_id: int):
        sensor = Sensor.objects.select_related("tipoSensor").get(pk=sensor_id)
        tipo_id = sensor.tipoSensor.pk
        cfg = self.strategy.resolve_update(tipo_id)
        return cfg

    # --- UPDATE: initial ---
    def get_update_initial(self, *, sensor_id: int) -> dict:
        cfg = self._resolve_cfg_by_sensor(sensor_id)
        repo = cfg["repo"]
        return repo.get_update_initial_data(sensor_id=sensor_id)

    # --- UPDATE: submit ---
    def update(self, *, sensor_id: int, data: dict) -> Sensor:
        cfg = self._resolve_cfg_by_sensor(sensor_id)
        repo = cfg["repo"]
        # delega todo al repo
        return repo.update_from_form(sensor_id=sensor_id, data=data)
        
    def delete(self, *, sensor_id: int) -> bool:
        deleted = self.repo.delete_sensor(sensor_id)
        return deleted == 1


    def build_detail(self, sensor_id: int) -> DetailSensor:
        """
        Devuelve un payload {"template_name": str, "context": dict}
        armado por la strategy, a partir del sensor y su tipo.
        """
        sensor = Sensor.objects.select_related("tipoSensor").get(pk=sensor_id)
        tipo_id = sensor.tipoSensor.pk
        return self.detail_strategy.resolve(sensor_id=sensor_id, tipo_id=tipo_id)
    
    
    def build_gas_dashboard(self, *, sensor_id: int, strategy: str = "latest_5_reg", **extra) -> Dict[str, Any]:
        """ Orquesta la construcción del contexto del dashboard de gas. """
        
        # valida existencia básica del sensor, si no está 404
        Sensor.objects.only("id").get(pk=sensor_id)

        selector = SelectpDataStrategy()
        data = selector.run(sensor_id=sensor_id, strategy=strategy, extra=extra or None)

        # Puedes enriquecer el contexto aquí si quieres (títulos, flags, etc.)
        return {
            "sensor_id": sensor_id,
            "strategy": strategy,
            "data": data,   # <- datos del sensor
        }
        
    def eval_conn(self) -> None:
        """
        Itera todos los sensores y evalúa su estado de conexión.
        """
        qs: QuerySet[Sensor] = Sensor.objects.select_related("tipoSensor").all()
        for sensor in qs:
            tipo_id = sensor.tipoSensor.pk
            evaluator = self.conn_strategy.resolve_eval_callable(tipo_id=tipo_id)
            # cada evaluador recibe el objeto sensor
            evaluator(sensor)

    def build_export_workbook_by_gas(self, *, gas_pk: int) -> Tuple[bytes, str]:
        """
        Pide dataset a la strategy y arma el XLSX en memoria.
        Retorna (bytes_xlsx, filename).
        """
        dataset = self.reportStrategy.build_export_dataset(gas_pk=gas_pk)

        sensor_name = dataset.get("sensor_name") or "sensor"
        cylinder_id = dataset.get("cylinder_id")
        cylinder_name = dataset.get("cylinder_name") or ""
        rows: List[Dict[str, Any]] = dataset.get("rows", [])

        wb = Workbook()
        ws: Worksheet = cast(Worksheet, wb.active)
        ws.title = "Resultados"
        
        def _excel_ts(val):
            """Devuelve datetime naive (sin tzinfo) listo para Excel."""
            if isinstance(val, datetime):
                # Si es aware -> convertir a naive en UTC (o en la zona que prefieras)
                if djtz.is_aware(val):
                    return djtz.make_naive(val, djtz.utc)
                return val
            return val

        # Encabezado
        header = [
            "timestamp",
            "presion_gauge_pa",
            "presion_abs_pa",
            "temperature_k",
            "estado_fase",
            "caudal_masa_kg_s",
            "masa_remov_kg",
            "masa_restante_kg",
            "moles_restantes_kg",
            "metodo_calculo",
            "masa_balanza_kg",
            "porc_masa_gas_restant",
            "porc_masa_gas_extracted",
            "valido",
        ]
        ws.append(header)

        # Filas de datos
        for r in rows:
            ws.append([
                _excel_ts(r.get("timestamp")),
                r.get("presion_gauge_pa"),
                r.get("presion_abs_pa"),
                r.get("temperature_k"),
                r.get("estado_fase"),
                r.get("caudal_masa_kg_s"),
                r.get("masa_remov_kg"),
                r.get("masa_restante_kg"),
                r.get("moles_restantes_kg"),
                r.get("metodo_calculo"),
                r.get("masa_balanza_kg"),
                r.get("porc_masa_gas_restant"),
                r.get("porc_masa_gas_extracted"),
                r.get("valido"),
            ])

        # Auto-ancho aproximado
        for col_idx, col_name in enumerate(header, start=1):
            max_len = len(col_name)
            # recorre la columna col_idx, desde la fila 2 hasta la última
            for col_cells in ws.iter_cols(min_col=col_idx, max_col=col_idx, min_row=2, max_row=ws.max_row):
                for c in col_cells:
                    val = c.value
                    if val is not None:
                        max_len = max(max_len, len(str(val)))
            ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 2, 40)

        # Segundo sheet con metadatos
        meta: Worksheet = cast(Worksheet, wb.create_sheet("Resumen"))
        meta.append(["Sensor", sensor_name])
        meta.append(["Cilindro (id)", cylinder_id])
        meta.append(["Cilindro (nombre)", cylinder_name])
        meta.append(["Total registros", len(rows)])
        meta.append(["Generado", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        # Guardar a bytes
        buff = BytesIO()
        wb.save(buff)
        buff.seek(0)

        base = slugify(sensor_name) or "sensor"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base}_resultados_{ts}.xlsx"
        return buff.read(), filename
    
    def build_empty_export(self, *, sensor_id: int) -> tuple[bytes, str]:

        wb = Workbook()
        ws: Worksheet = cast(Worksheet, wb.active)
        
        ws.title = "Resultados"
        # Encabezado “oficial” para no romper parsers
        header = [
            "timestamp", "presion_gauge_pa", "presion_abs_pa", "temperature_k",
            "estado_fase", "caudal_masa_kg_s", "masa_remov_kg", "masa_restante_kg",
            "moles_restantes_kg", "metodo_calculo", "masa_balanza_kg",
            "porc_masa_gas_restant", "porc_masa_gas_extracted", "valido",
        ]
        ws.append(header)

        meta = wb.create_sheet("Resumen")
        meta.append(["Sensor (id)", sensor_id])
        meta.append(["Observación", "No se encontraron datos para exportar"])
        meta.append(["Generado", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sensor_{sensor_id}_resultados_{ts}.xlsx"
        return buf.read(), filename