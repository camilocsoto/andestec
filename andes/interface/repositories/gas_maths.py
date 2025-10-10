from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, cast
from django.db import transaction
from django.utils import timezone

from interface.models import Sensor, GasRestante, ComposicionGas, CaracteristicasCilindro, ResultsGasRestante


# ---------- Utils y constantes ----------
PSI_TO_PA = 6894.757293168  # Pa/psi
BAR_TO_PA = 1e5
ATM_PA = 101_325.0
PI = 3.141592653589793
R_UNIV = 8.314462618  # J/(mol·K)

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
        
        comp = getattr(cil, 'cil.ComposicionGas', None)
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

    # ---------- Detección de choked + validaciones ----------
    def is_choked(self, *, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Regresa dict con:
        - skip_calc: True si P_gauge < 5 psi o faltan datos clave
        - is_choked: bool
        - p0_abs_pa, p2_pa, T0_K, ratio_real, ratio_crit, gamma
        - sensor_id
        """
        sensor_id = info.get("sensor_id")
        if not sensor_id:
            raise ValueError("info['sensor_id'] es requerido")

        sp = self._load_static(sensor_id=sensor_id)

        # Lecturas del sensor
        P_gauge_psi = safe_float(info.get("pressure"))
        T0_K = safe_float(info.get("temperature"))
        # Validación rápida: presión muy baja → no recalcular
        if P_gauge_psi is None or P_gauge_psi < 5.0:
            return {
                "skip_calc": True,
                "reason": "low_pressure_or_none",
                "sensor_id": sensor_id,
                "p2_pa": sp.p_atm_pa,
                "P_gauge_psi": P_gauge_psi,
                "T0_K": T0_K,
            }

        if T0_K is None or T0_K <= 0.0:
            # Usa un fallback razonable (290 K) si la lectura no viene
            T0_K = 290.0

        p0_abs_pa = P_gauge_psi * PSI_TO_PA + sp.p_atm_pa
        p2_pa = sp.p_atm_pa  # descarga a atmósfera

        # Criterio de estrangulamiento
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
            "cilindro_pk": sp.cilindro.pk,
            "cilindro": sp.cilindro,
            "p_atm_pa": sp.p_atm_pa,
            "masa_lleno_kg": sp.masa_lleno_kg,
            "masa_tara_kg": sp.masa_tara_kg,
            "masa_gas_restante_kg": sp.masa_gas_restante_kg,
            "z_factor": sp.z_factor,
        }

    # ---------- Cálculo CHOKED ----------
    def choked(self, *, info: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula caudal choked, masa removida en 60 s, masa restante,
        % restante, estado_fase, moles, etc.
        """
        area = ctx.get("area_m2")
        cd = ctx["cd"]
        p0 = ctx["p0_abs_pa"]
        T0 = ctx["T0_K"]
        gamma = ctx["gamma"]
        R_spec = ctx["R_spec"]

        if not area:
            raise ValueError("No se tiene área de orificio. Define diametro_orificio_m o area_orificio_m2.")

        # Fórmula de flujo estrangulado (con Cd)
        # mdot = C_d * A * p0 * sqrt( gamma/(R_spec*T0) ) * ((gamma+1)/2)^{- (gamma+1)/(2*(gamma-1))}
        factor = ((gamma + 1.0) / 2.0) ** (-(gamma + 1.0) / (2.0 * (gamma - 1.0)))
        mdot = cd * area * p0 * ( (gamma / (R_spec * T0)) ** 0.5 ) * factor  # kg/s

        # Masa removida en 60 s
        masa_remov_kg = mdot * 60.0

        # Masa inicial (si no hay estado previo, usa lleno - tara)
        m0 = ctx.get("masa_gas_restante_kg")
        if m0 is None:
            if ctx["masa_lleno_kg"] is not None and ctx["masa_tara_kg"] is not None:
                m0 = ctx["masa_lleno_kg"] - ctx["masa_tara_kg"]
            else:
                m0 = None  # sin referencia de masa inicial

        if m0 is None:
            # sin referencia de masa previa; no podemos diferenciar precisa masa restante.
            masa_restante_kg = None
            porc = None
        else:
            masa_restante_kg = max(m0 - masa_remov_kg, 0.0)
            # porcentaje respecto a masa inicial teórica (lleno - tara)
            total_ini = (ctx["masa_lleno_kg"] - ctx["masa_tara_kg"]) if (ctx["masa_lleno_kg"] is not None and ctx["masa_tara_kg"] is not None) else None
            if total_ini and total_ini > 0:
                porc = (masa_restante_kg / total_ini) * 100.0
            else:
                porc = None

        # Moles restantes (si conocemos volumen y estado gas ideal en fase vapor; aquí solo informativo)
        n_rest = None
        estado_fase = "bifasico"  # mientras hay presión alta y masa significativa asumimos bifásico
        if masa_restante_kg is not None and ctx.get("volumen_m3"):
            # Solo informar si ya está solo vapor (difícil saber sin modelo de equilibrio). Lo dejamos bifásico por defecto.
            pass

        return {
            **ctx,
            "mdot_kg_s": mdot,
            "masa_removida_kg": masa_remov_kg,
            "masa_restante_kg": masa_restante_kg,
            "porc_masa_gas_restant": porc,
            "estado_fase": estado_fase,
            "metodo": "choked",
        }

    # ---------- Cálculo NO CHOKED ----------
    def no_choked(self, *, info: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """
        Usa fórmula subcrítica (no estrangulada). Si el tanque ya está solo vapor
        y tienes volumen, puedes además usar ideal gas para estimar moles/másica.
        """
        area = ctx.get("area_m2")
        cd = ctx["cd"]
        p0 = ctx["p0_abs_pa"]
        p2 = ctx["p2_pa"]
        T0 = ctx["T0_K"]
        gamma = ctx["gamma"]
        R_spec = ctx["R_spec"]

        if not area:
            raise ValueError("No se tiene área de orificio. Define diametro_orificio_m o area_orificio_m2.")

        # mdot = C_d * A * p0 * sqrt( (2*gamma)/(R_spec*T0*(gamma-1)) * [ (p2/p0)^{2/gamma} - (p2/p0)^{(gamma+1)/gamma} ] )
        pr = p2 / p0
        inside = (pr ** (2.0 / gamma)) - (pr ** ((gamma + 1.0) / gamma))
        if inside <= 0.0:
            mdot = 0.0
        else:
            mdot = cd * area * p0 * (( (2.0 * gamma) / (R_spec * T0 * (gamma - 1.0)) * inside ) ** 0.5)

        masa_remov_kg = mdot * 60.0

        # Masa inicial y restante (igual que arriba)
        m0 = ctx.get("masa_gas_restante_kg")
        if m0 is None:
            if ctx["masa_lleno_kg"] is not None and ctx["masa_tara_kg"] is not None:
                m0 = ctx["masa_lleno_kg"] - ctx["masa_tara_kg"]
            else:
                m0 = None

        if m0 is None:
            masa_restante_kg = None
            porc = None
        else:
            masa_restante_kg = max(m0 - masa_remov_kg, 0.0)
            total_ini = (ctx["masa_lleno_kg"] - ctx["masa_tara_kg"]) if (ctx["masa_lleno_kg"] is not None and ctx["masa_tara_kg"] is not None) else None
            porc = (masa_restante_kg / total_ini) * 100.0 if total_ini and total_ini > 0 else None

        # Si suponemos solo vapor y tenemos volumen → gas ideal para moles
        n_rest = None
        estado_fase = "vapor"  # al caer presión y salir de choke, es razonable etiquetar vapor si ya está bajo
        if masa_restante_kg is not None and ctx.get("volumen_m3") and masa_restante_kg > 0:
            # OJO: sin Z y sin equilibrio esto es aproximación; lo dejamos comentado
            # n = P*V / (R*T) (en moles); masa = n*M
            pass

        return {
            **ctx,
            "mdot_kg_s": mdot,
            "masa_removida_kg": masa_remov_kg,
            "masa_restante_kg": masa_restante_kg,
            "porc_masa_gas_restant": porc,
            "estado_fase": estado_fase,
            "metodo": "no_choked",
        }

    # ---------- Guardado en ResultsGasRestante ----------
    @transaction.atomic
    def save_results(self, *, info: Dict[str, Any], calc: Dict[str, Any], metodo: str):
        """
        Persiste una fila en ResultsGasRestante.
        - Actualiza (si quieres) la masa restante del cilindro en CaracteristicasCilindro.masa_gas_restant_kg
          para usarla como “estado” en el siguiente minuto.
        """
        sensor_id = calc["sensor_id"]
        cil: CaracteristicasCilindro = calc["cilindro"]

        # Lecturas base
        P_gauge_psi = safe_float(info.get("pressure"))
        T0_K = safe_float(info.get("temperature"))
        if T0_K is None or T0_K <= 0: T0_K = 290.0

        presion_gauge_pa = P_gauge_psi * PSI_TO_PA if P_gauge_psi is not None else None
        presion_abs_pa = calc.get("p0_abs_pa")

        masa_restante_kg = calc.get("masa_restante_kg")
        masa_remov_kg = calc.get("masa_removida_kg")
        mdot = calc.get("mdot_kg_s")
        estado_fase = calc.get("estado_fase", "descon.")
        porc_rest = calc.get("porc_masa_gas_restant")

        # Moles restantes si tienes masa y M
        M_kg_mol = calc.get("M_kg_mol", 0.04901)
        moles_restantes = (masa_restante_kg / M_kg_mol) if (masa_restante_kg is not None and M_kg_mol) else None

        # Construir fila
        row = ResultsGasRestante.objects.create(
            timestamp=timezone.now(),
            presion_gauge_pa=presion_gauge_pa,
            presion_abs_pa=presion_abs_pa,
            temperature_k=T0_K,
            estado_fase=estado_fase,
            caudal_masa_kg_s=mdot,
            masa_remov_kg=masa_remov_kg,
            masa_restante_kg=masa_restante_kg,
            moles_restantes_kg=moles_restantes,  # tu campo dice "kg" pero son moles; sugerencia: renómbralo
            metodo_calculo=metodo,
            masa_balanza_kg=None,  # si algún día pesas, llénalo
            porc_masa_gas_restant=porc_rest,
            caracteristicas_cilindro=cil,  # <<< Usa el nombre de campo REAL sin tildes
            valido=1,
        )

        # Opcional: persistir masa restante en el cilindro como “estado”
        try:
            if masa_restante_kg is not None:
                cil.masa_gas_restant_kg = masa_restante_kg
                cil.save(update_fields=["masa_gas_restant_kg"])
        except Exception:
            # no bloquees la transacción por este update secundario
            pass

        return row
