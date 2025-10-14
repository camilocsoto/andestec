from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, cast
from django.db import transaction
from django.utils import timezone

from interface.models import Sensor, GasRestante, ComposicionGas, CaracteristicasCilindro, ResultsGasRestante


# ---------- constants units ----------
PSI_TO_PA = 6894.757293168  # Pa/psi
BAR_TO_PA = 1e5
ATM_PA = 101_325.0
PI = 3.141592653589793
R_UNIV = 8.314462618  # J/(mol·K)

# ---------- helpers units ----------
def pa_to_psi(pa: float) -> float:
    return pa / PSI_TO_PA

def psi_to_pa(psi: float) -> float:
    return psi * PSI_TO_PA

def safe_float(x: Any, default: Optional[float] = None) -> Optional[float]:
    try:
        if x is None: return default
        return float(x)
    except Exception:
        return default

def area_from_diam(d_m: Optional[float]) -> Optional[float]:
    if d_m is None:
        return None
    r = d_m * 0.5
    return PI * r * r

def norm_temperature_to_K(t: Optional[float]) -> float:
    """
    Si llega None o <=0 -> 290 K.
    Si llega < 200 -> asumo °C y convierto a K.
    Si llega >= 200 -> ya está en K.
    """
    if t is None or t <= 0:
        return 290.0
    if t < 200.0:
        return t + 273.15
    return t

@dataclass
class StaticParams:
    # De CaracteristicasCilindro
    volumen_m3: Optional[float]
    masa_tara_kg: Optional[float]
    masa_lleno_kg: Optional[float]
    masa_gas_restante_kg: Optional[float]  # campo “estado” si lo usas como memoria
    cd: Optional[float]
    diam_m: Optional[float]
    area_m2: Optional[float]
    notas: Optional[str]

    # De ComposicionGas
    M_kg_mol: float           # masa molar mezcla
    gamma: float              # cp/cv estimado (usaremos y_entropia si viene)
    z_factor: Optional[float]
    densidad_ref: Optional[float]

    # Ambient/reference
    p_atm_pa: float           # si no hay, usar 101325 por defecto

    # Foreign keys prácticos
    cilindro: CaracteristicasCilindro
    comp: Optional[ComposicionGas]
    gas_restante_row: Optional[GasRestante]

class GasMaths:
    """Cálculos físicos y persistencia para GasRestante/ResultsGasRestante."""

    # ---------- Carga de parámetros estáticos ----------
    def _load_static(self, sensor_id: int) -> StaticParams:
        # # traer GasRestante (1:1 con Sensor)  y trae el último dato
        try:
            gr = GasRestante.objects.select_related("Sensor_idSensor").get(Sensor_idSensor_id=sensor_id)
        except GasRestante.DoesNotExist:
            raise ValueError(f"No existe GasRestante para sensor_id={sensor_id}")

        # Traer el cilindro vinculado al GasRestante (puede haber varios; elige el más reciente)
        cil_qs = CaracteristicasCilindro.objects.select_related("ComposicionGas").filter(GasRestante=gr).order_by("-pk")
        if not cil_qs.exists():
            raise ValueError(f"No existe CaracteristicasCilindro asociado al GasRestante del sensor_id={sensor_id}")
        cil = cil_qs.first()
        cil = cast(CaracteristicasCilindro, cil)
        
        comp = getattr(cil, 'ComposicionGas', None)
        comp = cast(Optional[ComposicionGas], comp) 

        # Masa molar de la mezcla
        M_kg_mol = comp.masa_molar if comp and comp.masa_molar else 0.04901  # fallback 49.01 g/mol
        # y_entropia lo usaremos como gamma si lo llenaste ahí; de lo contrario 1.13
        gamma = comp.y_entropia if comp and comp.y_entropia else 1.13
        z_factor = comp.z_factor if comp else None
        dens_ref = comp.densidad if comp else None

        p_atm = getattr(cil, "presion_atmosferica_ref_pa", None)
        if p_atm is None:
            # si no posees ese campo en tu modelo, usa atm estándar
            p_atm = ATM_PA

        # área: si no se guarda, se calcula del diámetro
        area = cil.diametro_orificio_m
        area = area_from_diam(area) if area else getattr(cil, "area_orificio_m2", None)

        return StaticParams(
            volumen_m3=cil.volumen_interno_m3,
            masa_tara_kg=cil.masa_cil_vacio_kg,
            masa_lleno_kg=cil.masa_cil_lleno_kg,
            masa_gas_restante_kg=cil.masa_gas_restant_kg,  # si lo usas como “estado”
            cd=cil.coef_descarga_cd,
            diam_m=cil.diametro_orificio_m,
            area_m2=area,
            notas=cil.notas,

            M_kg_mol=M_kg_mol,
            gamma=gamma,
            z_factor=z_factor,
            densidad_ref=dens_ref,

            p_atm_pa=p_atm,

            cilindro=cil,
            comp=comp,
            gas_restante_row=gr,
        )
        
    # ---------- helpers de últimos resultados ----------
    def _get_cylinder_for_sensor(self, sensor_id: int) -> CaracteristicasCilindro:
        sp = self._load_static(sensor_id=sensor_id)  # ya valida y retorna StaticParams
        return sp.cilindro

    def _last_result(self, cil: CaracteristicasCilindro) -> Optional[ResultsGasRestante]:
        return (ResultsGasRestante.objects.filter(caracteristicas_cilindro=cil).order_by("-timestamp").first())

    

    # ---------- Detección de choked + validaciones ----------
    def is_choked(self, *, info: Dict[str, Any]) -> Dict[str, Any]:
        sensor_id = info.get("sensor_id")
        if not sensor_id:
            raise ValueError("info['sensor_id'] es requerido")

        sp = self._load_static(sensor_id=sensor_id)

        P_gauge_psi = safe_float(info.get("pressure"))
        T0_K = safe_float(info.get("temperature"))

        # Normaliza temperatura si falta
        if T0_K is None or T0_K <= 0.0:
            T0_K = 290.0

        # Si presión < 5 psi => rama "low pressure"
        if P_gauge_psi is None or P_gauge_psi < 5.0:
            return {
                "skip_calc": True,
                "reason": "low_pressure_or_none",
                "sensor_id": sensor_id,
                "p2_pa": sp.p_atm_pa,
                "P_gauge_psi": P_gauge_psi,               # puede ser 0, <5, o None
                "p0_abs_pa": (P_gauge_psi or 0.0) * PSI_TO_PA + sp.p_atm_pa,
                "T0_K": T0_K,
                "cilindro": sp.cilindro,
                "M_kg_mol": sp.M_kg_mol,
            }

        # Caso normal >= 5 psi
        p0_abs_pa = P_gauge_psi * PSI_TO_PA + sp.p_atm_pa
        p2_pa = sp.p_atm_pa

        gamma = sp.gamma
        ratio_crit = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))
        ratio_real = p2_pa / p0_abs_pa
        is_choked = ratio_real < ratio_crit

        return {
            "skip_calc": False,
            "is_choked": is_choked,
            "sensor_id": sensor_id,
            "p0_abs_pa": p0_abs_pa,
            "p2_pa": p2_pa,
            "T0_K": T0_K,
            "ratio_real": ratio_real,
            "ratio_crit": ratio_crit,
            "gamma": gamma,
            "M_kg_mol": sp.M_kg_mol,
            "R_spec": R_UNIV / sp.M_kg_mol,
            "cd": sp.cd if sp.cd is not None else 0.62,
            "area_m2": sp.area_m2 if sp.area_m2 is not None else (area_from_diam(sp.diam_m) if sp.diam_m else None),
            "volumen_m3": sp.volumen_m3,
            "cilindro": sp.cilindro,
            "p_atm_pa": sp.p_atm_pa,
            "masa_lleno_kg": sp.masa_lleno_kg,
            "masa_tara_kg": sp.masa_tara_kg,
            "masa_gas_restante_kg": sp.masa_gas_restante_kg,
            "z_factor": sp.z_factor,
        }

    # ---------- guardado rama low-pressure ----------
    @transaction.atomic
    def save_low_pressure(self, *, info: Dict[str, Any], ctx: Dict[str, Any]):
        """
        Guarda un registro minimal cuando pressure < 5 psi, con reglas:
        - No guarda si previo gauge==0 psi y actual gauge==0 psi.
        - Guarda con:
          estado_fase=None, masa_remov_kg=0, masa_restante_kg=(prev o cil),
          moles_restantes=(prev o masa/M), y NO actualiza el cilindro.
        """
        cil: CaracteristicasCilindro = ctx["cilindro"]
        last = self._last_result(cil)

        curr_gauge_psi = safe_float(info.get("pressure"), 0.0) or 0.0
        curr_gauge_pa = psi_to_pa(curr_gauge_psi)
        curr_abs_pa = ctx.get("p0_abs_pa")  # ya incluye atm

        # Regla de supresión: previo==0 psi y actual==0 psi
        if last and last.presion_gauge_pa is not None:
            prev_gauge_psi = pa_to_psi(last.presion_gauge_pa)
            if prev_gauge_psi <= 0.01 and curr_gauge_psi <= 0.01:
                return None  # NO guardar

        # Determinar masa_restante y moles_restantes
        masa_restante_kg = None
        moles_restantes = None
        if last and last.masa_restante_kg is not None:
            masa_restante_kg = last.masa_restante_kg
            # preferimos conservar moles previos si existen
            if last.moles_restantes_kg is not None:
                moles_restantes = last.moles_restantes_kg
        if masa_restante_kg is None:
            masa_restante_kg = getattr(cil, "masa_gas_restant_kg", None)
            if masa_restante_kg is not None and moles_restantes is None:
                M_kg_mol = ctx.get("M_kg_mol", 0.04901)
                if M_kg_mol:
                    moles_restantes = masa_restante_kg / M_kg_mol

        # Temperatura
        T0_K_raw = safe_float(info.get("temperature"))
        T0_K = norm_temperature_to_K(T0_K_raw)

        # Crear fila
        row = ResultsGasRestante.objects.create(
            timestamp=timezone.now(),
            presion_gauge_pa=curr_gauge_pa,
            presion_abs_pa=curr_abs_pa,
            temperature_k=T0_K,
            estado_fase=None,            # solicitado
            caudal_masa_kg_s=None,       # no se calcula en esta rama
            masa_remov_kg=0.0,           # solicitado
            masa_restante_kg=masa_restante_kg,
            moles_restantes_kg=moles_restantes,
            metodo_calculo="skip_low_pressure",
            masa_balanza_kg=None,
            porc_masa_gas_restant=None if masa_restante_kg is None else self._porc_from_cil(cil, masa_restante_kg),
            caracteristicas_cilindro=cil,
            valido=1,
        )
        # Importante: **NO** actualizar cil.masa_gas_restant_kg en esta rama
        return row

    def _porc_from_cil(self, cil: CaracteristicasCilindro, masa_restante_kg: Optional[float]) -> Optional[float]:
        if masa_restante_kg is None:
            return None
        if cil.masa_cil_lleno_kg is None or cil.masa_cil_vacio_kg is None:
            return None
        total_ini = cil.masa_cil_lleno_kg - cil.masa_cil_vacio_kg
        if total_ini and total_ini > 0:
            return (masa_restante_kg / total_ini) * 100.0
        return None
    
        # ---------- Cálculo CHOKED ----------
    def choked(self, *, info: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        mdot choked (isentrópico + Cd):
        mdot = Cd * A * p0 * sqrt( gamma/(Rspec*T0) ) * ((gamma+1)/2)^(-(gamma+1)/(2*(gamma-1)))
        """
        area = ctx.get("area_m2")
        cd = ctx["cd"]
        p0 = ctx["p0_abs_pa"]
        T0 = norm_temperature_to_K(ctx.get("T0_K"))
        gamma = ctx["gamma"]
        R_spec = ctx["R_spec"]

        if not area:
            raise ValueError("No se tiene área de orificio. Define diametro_orificio_m o area_orificio_m2.")

        factor = ((gamma + 1.0) / 2.0) ** (-(gamma + 1.0) / (2.0 * (gamma - 1.0)))
        mdot = cd * area * p0 * ((gamma / (R_spec * T0)) ** 0.5) * factor  # kg/s

        masa_remov_kg = mdot * 60.0

        # masa inicial m0
        m0 = ctx.get("masa_gas_restante_kg")
        if m0 is None:
            if ctx["masa_lleno_kg"] is not None and ctx["masa_tara_kg"] is not None:
                m0 = ctx["masa_lleno_kg"] - ctx["masa_tara_kg"]
        masa_restante_kg = max((m0 or 0.0) - masa_remov_kg, 0.0) if m0 is not None else None

        # porcentaje
        total_ini = None
        if ctx.get("masa_lleno_kg") is not None and ctx.get("masa_tara_kg") is not None:
            total_ini = ctx["masa_lleno_kg"] - ctx["masa_tara_kg"]
        porc = (masa_restante_kg / total_ini * 100.0) if (masa_restante_kg is not None and total_ini and total_ini > 0) else None

        return {
            **ctx,
            "T0_K": T0,
            "mdot_kg_s": mdot,
            "masa_removida_kg": masa_remov_kg,
            "masa_restante_kg": masa_restante_kg,
            "porc_masa_gas_restant": porc,
            "estado_fase": "choked",
            "metodo": "choked",
        }

    # ---------- Cálculo NO CHOKED ----------
    def no_choked(self, *, info: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        mdot subcrítico (no estrangulado):
        mdot = Cd * A * p0 * sqrt( (2*gamma)/(Rspec*T0*(gamma-1))
               * [ (p2/p0)^(2/gamma) - (p2/p0)^((gamma+1)/gamma) ] )
        """
        area = ctx.get("area_m2")
        cd = ctx["cd"]
        p0 = ctx["p0_abs_pa"]
        p2 = ctx["p2_pa"]
        T0 = norm_temperature_to_K(ctx.get("T0_K"))
        gamma = ctx["gamma"]
        R_spec = ctx["R_spec"]

        if not area:
            raise ValueError("No se tiene área de orificio. Define diametro_orificio_m o area_orificio_m2.")

        pr = p2 / p0
        inside = (pr ** (2.0 / gamma)) - (pr ** ((gamma + 1.0) / gamma))
        mdot = 0.0
        if inside > 0.0:
            mdot = cd * area * p0 * (((2.0 * gamma) / (R_spec * T0 * (gamma - 1.0)) * inside) ** 0.5)

        masa_remov_kg = mdot * 60.0

        m0 = ctx.get("masa_gas_restante_kg")
        if m0 is None:
            if ctx["masa_lleno_kg"] is not None and ctx["masa_tara_kg"] is not None:
                m0 = ctx["masa_lleno_kg"] - ctx["masa_tara_kg"]
        masa_restante_kg = max((m0 or 0.0) - masa_remov_kg, 0.0) if m0 is not None else None

        total_ini = None
        if ctx.get("masa_lleno_kg") is not None and ctx.get("masa_tara_kg") is not None:
            total_ini = ctx["masa_lleno_kg"] - ctx["masa_tara_kg"]
        porc = (masa_restante_kg / total_ini * 100.0) if (masa_restante_kg is not None and total_ini and total_ini > 0) else None

        return {
            **ctx,
            "T0_K": T0,
            "mdot_kg_s": mdot,
            "masa_removida_kg": masa_remov_kg,
            "masa_restante_kg": masa_restante_kg,
            "porc_masa_gas_restant": porc,
            "estado_fase": "no_choked",
            "metodo": "no_choked",
        }

    
    
    # ---------- Guardado en ResultsGasRestante ----------
    
    @transaction.atomic
    def save_results(self, *, info: Dict[str, Any], calc: Dict[str, Any], metodo: str):
        cil: CaracteristicasCilindro = calc["cilindro"]
        P_gauge_psi = safe_float(info.get("pressure"))
        T0_K = safe_float(info.get("temperature")) or 290.0
        presion_gauge_pa = psi_to_pa(P_gauge_psi) if P_gauge_psi is not None else None
        presion_abs_pa = calc.get("p0_abs_pa")

        masa_restante_kg = calc.get("masa_restante_kg")
        masa_remov_kg = calc.get("masa_removida_kg")
        mdot = calc.get("mdot_kg_s")
        estado_fase = calc.get("estado_fase", None) 
        porc_rest = calc.get("porc_masa_gas_restant")

        M_kg_mol = calc.get("M_kg_mol", 0.04901)
        moles_restantes = (masa_restante_kg / M_kg_mol) if (masa_restante_kg is not None and M_kg_mol) else None

        row = ResultsGasRestante.objects.create(
            timestamp=timezone.now(),
            presion_gauge_pa=presion_gauge_pa,
            presion_abs_pa=presion_abs_pa,
            temperature_k=T0_K,
            estado_fase=estado_fase,
            caudal_masa_kg_s=mdot,
            masa_remov_kg=masa_remov_kg,
            masa_restante_kg=masa_restante_kg,
            moles_restantes_kg=moles_restantes,
            metodo_calculo=metodo,
            masa_balanza_kg=None,
            porc_masa_gas_restant=porc_rest,
            caracteristicas_cilindro=cil,
            valido=1,
        )

        # Solo en cálculos normales actualizamos el estado en Cilindro
        try:
            if masa_restante_kg is not None and metodo in ("choked", "no_choked"):
                cil.masa_gas_restant_kg = masa_restante_kg
                cil.save(update_fields=["masa_gas_restant_kg"])
        except Exception:
            pass

        return row