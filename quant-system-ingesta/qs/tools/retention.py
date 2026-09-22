"""tools/retention.py — Retención de Parquet en disco (ESPEC §9, v1.4/v2.2).

Borra días completos YA AUDITADOS (audit.json) **y YA RESPALDADOS con
verificación** (.backed_up — candado v2.2) cuando superan max_days o bajo
presión de disco (antiguos primero). Nunca toca días sin auditar, sin respaldar
ni la ventana protegida min_keep_days. Dry-run por defecto; --apply ejecuta.

Uso:  python tools/retention.py [--apply]
"""
from __future__ import annotations
import argparse
import glob
import os
import shutil
import sys
import time


def _dir_size(path: str) -> int:
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            total += os.path.getsize(os.path.join(root, f))
    return total


def plan_retention(data_dir: str, max_days: int = 75, min_free_gb: float = 5,
                   min_keep_days: int = 7, now: float | None = None,
                   disk_free_bytes: int | None = None) -> list[str]:
    """Day-dirs a borrar, más antiguos primero. Solo días con audit.json y
    anteriores a la ventana protegida; `disk_free_bytes` inyectable en tests."""
    from tools.backup import _marker_obsoleto   # lazy: evita líos de path como script
    now = now if now is not None else time.time()
    cutoff = time.strftime("%Y-%m-%d", time.gmtime(now - max_days * 86400))
    protegido = time.strftime("%Y-%m-%d", time.gmtime(now - min_keep_days * 86400))
    candidatos: list[tuple[str, str]] = []
    for p in sorted(glob.glob(os.path.join(data_dir, "*", "*"))):
        if not os.path.isdir(p):
            continue
        day = os.path.basename(p)
        if day >= protegido or not os.path.exists(os.path.join(p, "audit.json")):
            continue
        # candado (§9 v2.2): sin respaldo VERIFICADO y VIGENTE jamás se borra. Un
        # marcador obsoleto (el día cambió tras respaldarse → remoto desfasado)
        # cuenta como NO respaldado (mismo criterio que backup.dias_pendientes).
        if not os.path.exists(os.path.join(p, ".backed_up")) or _marker_obsoleto(p):
            continue
        candidatos.append((day, p))
    candidatos.sort()                            # antiguos primero
    plan = [p for day, p in candidatos if day < cutoff]
    if disk_free_bytes is None:
        disk_free_bytes = shutil.disk_usage(data_dir).free
    objetivo = min_free_gb * 2 ** 30
    liberado = sum(_dir_size(p) for p in plan)
    if disk_free_bytes + liberado < objetivo:    # presión de disco
        elegidos = set(plan)
        for day, p in candidatos:
            if p in elegidos:
                continue
            plan.append(p)
            liberado += _dir_size(p)
            if disk_free_bytes + liberado >= objetivo:
                break
    return plan


def main() -> None:
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # → qs/
    sys.path.insert(0, os.getcwd())
    import yaml
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply", action="store_true",
                    help="ejecuta el borrado (sin esto: dry-run)")
    a = ap.parse_args()
    with open("config/instruments.yaml") as f:
        cfg = yaml.safe_load(f)
    r = cfg.get("retention") or {}
    min_free = r.get("min_free_gb", 5)
    plan = plan_retention(cfg["data_dir"], r.get("max_days", 75),
                          min_free, r.get("min_keep_days", 7))
    # alerta de presión (hallazgo code-reviewer): si el disco va justo y el plan
    # no alcanza a liberar lo necesario (típico: candado sin respaldos), avisar —
    # el primer síntoma NO puede ser el ENOSPC del writer
    free_gb = shutil.disk_usage(cfg["data_dir"]).free / 2 ** 30
    liberable_gb = sum(_dir_size(p) for p in plan) / 2 ** 30
    if free_gb < min_free and free_gb + liberable_gb < min_free:
        from tools.backup import alerta
        alerta(f"⚠️ quant-ingesta: disco bajo ({free_gb:.1f} GB libres) y la "
               f"retención solo puede liberar {liberable_gb:.1f} GB — "
               f"¿faltan respaldos (candado) o hay que ampliar disco?")
    if not plan:
        print("retención: nada que borrar")
        return
    total = 0
    for p in plan:
        sz = _dir_size(p)
        total += sz
        print(f"{'BORRADO ' if a.apply else 'borraría'} {p}  ({sz / 2**20:.1f} MB)")
        if a.apply:
            shutil.rmtree(p)
    print(f"{'liberados' if a.apply else 'liberaría'} {total / 2**30:.2f} GB "
          f"en {len(plan)} día(s)")


if __name__ == "__main__":
    main()
