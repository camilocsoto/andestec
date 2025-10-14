from ..models import Sensor, GasRestante, TipoSensor, CaracteristicasCilindro, ComposicionGas, ResultsGasRestante, ServerCredentials
from accounts.models import Empresa
from typing import Tuple, Dict, Any, List, Optional
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import OuterRef, Subquery, QuerySet
from django.db import transaction
from django.utils import timezone
import json

def _safe(v, placeholder="--") -> Any:
    if v is None:
        return placeholder
    if isinstance(v, str) and not v.strip():
        return placeholder
    return v

class SensorTPRepository:
    """
    Repo responsable de crear el sensor y su GasRestante para tipo_id=2.
    Aquí va TODA la persistencia y normalización de datos desde el form.
    """
    def get_all(self):
        """return all sensors (for admin menu)"""
        return Sensor.objects.all()
    
    def get_sensor_with_related(self, pk: int) -> Sensor:
        """return the specific sensors (for empresa and operador menu)"""
        return Sensor.objects.select_related("empresa", "tipoSensor").get(pk=pk)

    def _to_estado_bool(self, estado_bytes: Optional[bytes]) -> Optional[bool]:
        """function part of the form update, to normalize the data"""
        if estado_bytes is None:
            return None
        return estado_bytes == b"\x01"

    def _to_estado_bytes(self, estado_bool: Optional[bool]) -> Optional[bytes]:
        """function part of the form create, to normalize the data"""
        if estado_bool is None:
            return None
        return b"\x01" if estado_bool else b"\x00"

    @transaction.atomic
    def create_from_form(self, *, tipo_id: int, data: dict[str, Any]) -> Sensor:
        """Recibe form.cleaned_data, normaliza y delega a la api primitiva."""
        nombre = data.get("nombre")
        estado_bytes = self._to_estado_bytes(data.get("estado"))
        empresa: Optional[Empresa] = data.get("empresa")
        toleranciaMins:Optional[int] = data.get("toleranciaMins")
        localizacion: Optional[str] = data.get("localizacion")
        bateria: Optional[str] = data.get("bateria")
        server_deviceNo: Optional[str] = data.get("server_deviceNo")
        server_credentials: Optional[ServerCredentials] = data.get("server_credentials")

        return self.create_gas_tp_sensor(
            nombre=nombre,
            estado_bytes=estado_bytes,
            empresa=empresa,
            toleranciaMins= toleranciaMins,
            tipo_id=tipo_id,
            localizacion=localizacion,
            bateria=bateria,
            server_deviceNo=server_deviceNo,
            server_credentials=server_credentials,
        )
        
    @transaction.atomic
    def create_gas_tp_sensor(self,*,nombre: str | None,estado_bytes: bytes | None,empresa: Empresa | None,tipo_id: int, toleranciaMins:int | None, localizacion: str | None,bateria: str | None,server_deviceNo: str | None,server_credentials: ServerCredentials | None,) -> Sensor:
        """Primitivo de bajo nivel: recibe datos ya normalizados."""
        tipo = TipoSensor.objects.get(pk=tipo_id)
        sensor = Sensor.objects.create(
            nombre=nombre,
            estado=estado_bytes,
            empresa=empresa,
            tipoSensor=tipo,
        )
        GasRestante.objects.create(
            Sensor_idSensor=sensor,
            toleranciaMins=toleranciaMins,
            localizacion=localizacion,
            bateria=bateria,
            server_deviceNo=server_deviceNo,
            server_credentials=server_credentials,
        )
        return sensor

    # ---------- READ (initial) ----------
    def get_update_initial_data(self, *, sensor_id: int) -> Dict[str, Any]:
        """
        Devuelve el initial para el formulario de update.
        """
        sensor = (Sensor.objects.select_related("empresa__usuario", "tipoSensor").get(pk=sensor_id))
        try:
            gas = GasRestante.objects.get(Sensor_idSensor_id=sensor_id)
        except GasRestante.DoesNotExist:
            gas = None

        return {
            "nombre": sensor.nombre,
            "estado": self._to_estado_bool(sensor.estado), # bytes -> bool/None
            "empresa": sensor.empresa,
            "localizacion": getattr(gas, "localizacion", "") if gas else "",
            "bateria": getattr(gas, "bateria", "") if gas else "",
            "toleranciaMins": getattr(gas, "toleranciaMins", None) if gas else None,
            "server_deviceNo": getattr(gas, "server_deviceNo", "") if gas else "",
            "server_credentials": getattr(gas, "server_credentials", None) if gas else None,
            # si el form tiene tipoSensor, lo ignoraremos en update
        }

    # ---------- WRITE (update) ----------
    @transaction.atomic
    def update_from_form(self, *, sensor_id: int, data: Dict[str, Any]) -> Sensor:
        """
        Recibe form.cleaned_data (data) y realiza TODA la persistencia:
        - normaliza estado (bool -> bytes)
        - actualiza Sensor
        - actualiza GasRestante
        """
        # Ignorar tipoSensor si viene en el form
        if "tipoSensor" in data:
            data = {k: v for k, v in data.items() if k != "tipoSensor"}

        sensor = (Sensor.objects.select_for_update().select_related("tipoSensor").get(pk=sensor_id))

        # Normalizaciones desde el form
        nombre = data.get("nombre")
        estado_bytes = self._to_estado_bytes(data.get("estado"))
        empresa: Optional[Empresa] = data.get("empresa")
        toleranciaMins:Optional[int] = data.get("toleranciaMins")
        localizacion: Optional[str] = data.get("localizacion")
        bateria: Optional[str] = data.get("bateria")
        server_deviceNo: Optional[str] = data.get("server_deviceNo")
        server_credentials: Optional[ServerCredentials] = data.get("server_credentials")

        # Persistencia Sensor
        sensor.nombre = nombre
        sensor.estado = estado_bytes
        sensor.empresa = empresa
        sensor.save(update_fields=["nombre", "estado", "empresa"])

        # Persistencia GasRestante (1:1 con Sensor)
        gas = GasRestante.objects.select_for_update().get(Sensor_idSensor_id=sensor_id)
        gas.toleranciaMins = toleranciaMins
        gas.localizacion = localizacion
        gas.bateria = bateria
        gas.server_deviceNo = server_deviceNo
        if server_credentials is not None:
            gas.server_credentials = server_credentials
        
        gas.save(update_fields=["toleranciaMins", "localizacion", "bateria", "server_deviceNo", "server_credentials"])
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
        return (Sensor.objects.select_related("empresa__usuario", "tipoSensor").get(pk=sensor_id))

    def get_gasrestante_for_sensor(self, sensor_id: int) -> GasRestante | None:
        try:
            return (GasRestante.objects.select_related("server_credentials", "Sensor_idSensor").get(Sensor_idSensor_id=sensor_id))
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
            ResultsGasRestante.objects.filter(caracteristicas_cilindro=OuterRef('pk')).order_by('-timestamp').values('id')[:1]
        )

        cilindros_qs = (CaracteristicasCilindro.objects.select_related('ComposicionGas', 'GasRestante').filter(GasRestante=gas).annotate(latest_result_id=Subquery(latest_result_subq))
        )

        # Extraer los ids anotados sin acceder a atributos dinámicos en instancias
        ids_qs = cilindros_qs.values_list('latest_result_id', flat=True)
        # materializar y filtrar None/0/'' (lo que sea no válido)
        ids = [int(i) for i in ids_qs if i]

        latest_results = ResultsGasRestante.objects.in_bulk(ids) if ids else {}

        return cilindros_qs, latest_results
    
    def build_detail_pres2(self, sensor_id: int) -> Dict[str, Any]:
        """
        Devuelve {"template_name": str, "context": dict} para el detail del tipo 2.
        """
        sensor: Sensor = self.get_sensor_base(sensor_id)
        gas: Optional[GasRestante] = self.get_gasrestante_for_sensor(sensor_id)

        cilindros: QuerySet[CaracteristicasCilindro] = CaracteristicasCilindro.objects.none()
        latest_map: Dict[int, ResultsGasRestante] = {}
        if gas:
            cilindros, latest_map = self.get_cylinders_with_latest_result(gas)

        # Empresa legible
        empresa_nombre: Optional[str] = None
        empresa_obj = getattr(sensor, "empresa", None)
        if empresa_obj is not None:
            usuario_obj = getattr(empresa_obj, "usuario", None)
            if usuario_obj is not None:
                empresa_nombre = (
                    usuario_obj.get_full_name()
                    or usuario_obj.email
                    or usuario_obj.username
                )

        # Estado binario → etiqueta
        estado_legible: Optional[str] = None
        if getattr(sensor, "estado", None) is not None:
            estado_legible = "Activo" if sensor.estado == b"\x01" else "Inactivo"

        # GasRestante (sin localizacion)
        gas_ctx = None
        if gas:
            gas_ctx = {
                "bateria": _safe(getattr(gas, "bateria", None)),
                "server_deviceNo": _safe(getattr(gas, "server_deviceNo", None)),
                "server_credentials": _safe(str(gas.server_credentials) if getattr(gas, "server_credentials", None) else None),
            }

        # Cilindros + último resultado por cilindro
        cil_ctx: List[dict] = []
        for cil in cilindros:
            comp: Optional[ComposicionGas] = getattr(cil, "ComposicionGas", None)

            key_any: Any = getattr(cil, "latest_result_id", None)
            if key_any is None:
                last: Optional[ResultsGasRestante] = None
            else:
                try:
                    key_int = int(key_any)
                except Exception:
                    key_int = None
                last = latest_map.get(key_int) if key_int is not None else None

            cil_ctx.append({
                "id": getattr(cil, "pk", None),
                "nombre": _safe(getattr(cil, "nombre", None)),
                "volumen_interno_m3": _safe(getattr(cil, "volumen_interno_m3", None)),
                "masa_cil_vacio_kg": _safe(getattr(cil, "masa_cil_vacio_kg", None)),
                "masa_cil_lleno_kg": _safe(getattr(cil, "masa_cil_lleno_kg", None)),
                "masa_gas_restant_kg": _safe(getattr(cil, "masa_gas_restant_kg", None)),
                "coef_descarga_cd": _safe(getattr(cil, "coef_descarga_cd", None)),
                "diametro_orificio_m": _safe(getattr(cil, "diametro_orificio_m", None)),
                "notas": _safe(getattr(cil, "notas", None)),
                "composicion_gas": None if not comp else {
                    "nombre": _safe(getattr(comp, "nombre", None)),
                    "descripcion": _safe(getattr(comp, "descripcion", None)),
                    "masa_molar": _safe(getattr(comp, "masa_molar", None)),
                    "y_entropia": _safe(getattr(comp, "y_entropia", None)),
                    "z_factor": _safe(getattr(comp, "z_factor", None)),
                    "densidad": _safe(getattr(comp, "densidad", None)),
                },
                "ultimo_resultado": None if not last else {
                    "timestamp": _safe(getattr(last, "timestamp", None)),
                    "presion_gauge_pa": _safe(getattr(last, "presion_gauge_pa", None)),
                    "presion_abs_pa": _safe(getattr(last, "presion_abs_pa", None)),
                    "temperature_k": _safe(getattr(last, "temperature_k", None)),
                    "estado_fase": _safe(getattr(last, "estado_fase", None)),
                    "caudal_masa_kg_s": _safe(getattr(last, "caudal_masa_kg_s", None)),
                    "masa_remov_kg": _safe(getattr(last, "masa_remov_kg", None)),
                    "masa_restante_kg": _safe(getattr(last, "masa_restante_kg", None)),
                    "moles_restantes_kg": _safe(getattr(last, "moles_restantes_kg", None)),
                    "metodo_calculo": _safe(getattr(last, "metodo_calculo", None)),
                    "masa_balanza_kg": _safe(getattr(last, "masa_balanza_kg", None)),
                    "valido": _safe(getattr(last, "valido", None)),
                }
            })

        context = {
            "sensor": sensor,
            "tipo_sensor": getattr(sensor, "tipoSensor", None),
            "empresa_nombre": _safe(empresa_nombre),
            "estado_legible": _safe(estado_legible),
            "gas": gas_ctx,
            "cilindros": cil_ctx,
        }
        return {
            "template_name": "sensors/tpresdetail.html",
            "context": context,
        }
    
class SensorTPEvalConnRepository:
    def _bool_to_bytes(self, flag: Optional[bool]) -> Optional[bytes]:
        if flag is None:
            return None
        return b"\x01" if flag else b"\x00"

    def _get_gas_by_sensor(self, sensor_id: int) -> Optional[GasRestante]:
        try:
            return (GasRestante.objects.select_related("Sensor_idSensor", "server_credentials").get(Sensor_idSensor_id=sensor_id))
        except GasRestante.DoesNotExist:
            return None

    def _get_primary_cylinder(self, gas: GasRestante) -> Optional[CaracteristicasCilindro]:
        return (CaracteristicasCilindro.objects.select_related("GasRestante").filter(GasRestante=gas).order_by("pk").first())

    @transaction.atomic
    def eval_conn_tp_gauge(self, sensor: Sensor) -> None:
        """
        Evalúa si el sensor 'está vivo' según el tiempo desde el último dato
        vs GasRestante.toleranciaMins. Actualiza Sensor.estado (BinaryField).
        """
        # Bloqueo para escritura segura del estado del sensor
        sensor = (Sensor.objects.select_for_update().select_related("tipoSensor").get(pk=sensor.pk))

        gas = self._get_gas_by_sensor(sensor.pk)
        if gas is None:
            # No hay relación GasRestante → no podemos evaluar
            return

        tol = gas.toleranciaMins
        if tol is None:
            # sin tolerancia configurada → no evaluamos
            return

        cyl = self._get_primary_cylinder(gas)
        if cyl is None:
            # sin cilindro → no hay resultados
            return

        last = (ResultsGasRestante.objects.filter(caracteristicas_cilindro=cyl, timestamp__isnull=False).order_by("-timestamp").first())
        if last is None:
            # nunca hubo resultados → no evaluamos
            return

        now = timezone.now()
        # defensivo: si el timestamp viene a futuro, delta=0
        if last.timestamp is None or last.timestamp > now:
            delta_mins = 0.0
        else:
            delta = now - last.timestamp
            delta_mins = delta.total_seconds() / 60.0

        # Estado: dentro de tolerancia -> True, fuera -> False
        is_up = delta_mins <= float(tol)
        sensor.estado = self._bool_to_bytes(is_up)
        sensor.save(update_fields=["estado"])
    
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
            results_qs = (ResultsGasRestante.objects.select_related("caracteristicas_cilindro").filter(caracteristicas_cilindro=cyl).order_by("-timestamp")[:5])
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
                "porc_masa_gas_restant": r.porc_masa_gas_restant,
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
        