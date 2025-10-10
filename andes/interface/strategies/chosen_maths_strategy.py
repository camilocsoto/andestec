# strategies/chosen_maths_strategy.py
from typing import Any, Dict
from ..repositories.gas_maths import GasMaths

class ChosenMathsStrategy:
    """Selecciona el método matemático de cálculo para gas."""
    def gas_maths_strategy(self, *, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        info = dict unificado del sensor:
        {
          'deviceNo': str,
          'pressure': float|str|None, # psi (gauge)
          'temperature': float|str|None, # K
          'battery': float|str|None,
          'signal': float|str|None,
          'iccid': str|None,
          'heartbeatDate': 'YYYY-MM-DD HH:MM:SS' | None,
          'lat': float|None,
          'lng': float|None,
          'sensor_id': int,   # AÑADIDO ANTES EN TU STRATEGY
        }
        """
        gm = GasMaths()

        # 1) Decidir si hay flujo estrangulado
        choke_ctx = gm.is_choked(info=info)  # dict con flags y magnitudes
        if choke_ctx.get("skip_calc", False):
            # Solo guarda un "ping" mínimo (sin recalcular nada pesado)
            saved = gm.save_results(info=info, calc=choke_ctx, metodo="skip_low_pressure")
            return {"status": "ok", "mode": "skip_low_pressure", "saved_id": saved.pk, "context": choke_ctx}

        if choke_ctx.get("is_choked", False):
            calc = gm.choked(info=info, ctx=choke_ctx)
            saved = gm.save_results(info=info, calc=calc, metodo="choked")
            return {"status": "ok", "mode": "choked", "saved_id": saved.pk, "context": calc}

        # Si no está estrangulado (subcrítico)
        calc = gm.no_choked(info=info, ctx=choke_ctx)
        saved = gm.save_results(info=info, calc=calc, metodo="no_choked")
        return {"status": "ok", "mode": "no_choked", "saved_id": saved.pk, "context": calc}
