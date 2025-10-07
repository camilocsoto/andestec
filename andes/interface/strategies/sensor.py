from typing import TypedDict, Type, Optional, List, Dict, Any, cast
from django import forms
from django.db.models import QuerySet
from interface.forms.tp_sensor import SensorTPForm
from ..repositories.sensor_repo import SensorTPRepository, SensorTPDetailRepository, GasDashboardRepository
from ..models import Sensor, GasRestante, TipoSensor, CaracteristicasCilindro, ComposicionGas, ResultsGasRestante

class SensorConfig(TypedDict):
    form_class: Type[forms.Form]
    template_name: str
    repo: SensorTPRepository
    
class DetailSensor(TypedDict):
    template_name: str
    context: dict
    
def _safe(v, placeholder="--") -> Any:
    if v is None:
        return placeholder
    if isinstance(v, str) and not v.strip():
        return placeholder
    return v

class SensorStrategy:
    """
    Devuelve un dict de configuración para cada tipo_id:
    - form_class a usar
    - template_name a renderizar
    - repo concreto para persistencia
    """
    def resolve(self, tipo_id: int) -> SensorConfig:
        # create different sensors
        if tipo_id == 2:
            return {
                "form_class": SensorTPForm,
                "template_name": "sensors/create_tpsensor.html",
                "repo": SensorTPRepository(),
            }
        # Agrega aquí otros mapeos de tipos
        raise ValueError(f"No hay Strategy/Repo para tipo_id={tipo_id}")
    
    def resolve_update(self, tipo_id: int) -> SensorConfig:
        # update different sensors
        if tipo_id == 2:
            return {
                "form_class": SensorTPForm,
                "template_name": "sensors/update_tpsensor.html",
                "repo": SensorTPRepository(),
            }
        # Agrega aquí otros mapeos de tipos
        raise ValueError(f"No hay Strategy/Repo (update) para tipo_id={tipo_id}")
    
    
class SensorDetailStrategy:
    def __init__(self):
        self.repo = SensorTPDetailRepository()

    def resolve(self, *, sensor_id: int, tipo_id: int) -> DetailSensor:
        if tipo_id == 2:
            return self._detail_pres2(sensor_id)
        # Agrega aquí otros sensores.
        return cast(DetailSensor, { # default case
            "template_name": "cruds/sensores/sensor_type2_detail.html",
            "context": {},
        })

    def _detail_pres2(self, sensor_id: int) -> DetailSensor:
        sensor: Sensor = self.repo.get_sensor_base(sensor_id)
        gas: Optional[GasRestante] = self.repo.get_gasrestante_for_sensor(sensor_id)

        # -> cilindros será siempre un QuerySet (iterable). Inicializamos con none()
        cilindros: QuerySet[CaracteristicasCilindro] = CaracteristicasCilindro.objects.none()
        latest_map: Dict[int, ResultsGasRestante] = {}
        if gas:
            cilindros, latest_map = self.repo.get_cylinders_with_latest_result(gas)
            # asegurarnos de que cilindros es un QuerySet (el repo debería devolverlo)
            if cilindros is None:
                cilindros = CaracteristicasCilindro.objects.none()

        # Empresa legible (comprobaciones en variables locales para que Pylance no se queje)
        empresa_nombre: Optional[str] = None
        empresa_obj = getattr(sensor, "empresa", None)
        if empresa_obj is not None:
            usuario_obj = getattr(empresa_obj, "usuario", None)
            if usuario_obj is not None:
                empresa_nombre = usuario_obj.get_full_name() or usuario_obj.email or usuario_obj.username

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
            # composición (puede ser None)
            comp: Optional[ComposicionGas] = getattr(cil, "ComposicionGas", None)

            # obtener la clave anotada de forma segura (Subquery -> puede devolver int/Decimal/None)
            key_any: Any = getattr(cil, "latest_result_id", None)
            last: Optional[ResultsGasRestante]
            if key_any is None:
                last = None
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


class SelectpDataStrategy:
    """
    Selecciona qué dataset armar según la 'estrategia' solicitada.
    """
    def __init__(self):
        self.repo = GasDashboardRepository()

    def run(self, *, sensor_id: int, strategy: str, extra: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """
        Retorna un dict de contexto que la vista usará para el dashboard.
        """
        match strategy:
            case "latest_5_reg":
                return self.repo.latest_5_reg(sensor_id=sensor_id)
            case _:
                # fallback por si llegan estrategias futuras
                return self.repo.latest_5_reg(sensor_id=sensor_id)