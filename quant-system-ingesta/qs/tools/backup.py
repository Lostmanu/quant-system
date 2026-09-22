"""tools/backup.py — Respaldo diario de días CERRADOS y AUDITADOS (ESPEC §9 v2.2).

Sube por rsync/SSH cada `data/{symbol}/{day}/` con `audit.json` y distinto del
día UTC en curso al destino `backup.remote` de config/instruments.yaml (formato
rsync, p. ej. `<USER>@<HOST>:<REMOTE_PATH>`; vacío = no-op).
La transferencia se VERIFICA (segunda pasada rsync --checksum sin cambios
pendientes) y solo entonces se escribe el marcador `.backed_up`, que es el
candado que la retención exige antes de borrar. Fallos → alerta Telegram.

Uso:  python tools/backup.py   (pensado para backup.timer, 00:30 UTC)
"""
from __future__ import annotations
import glob
import json
import os
import subprocess
import sys
import time
import urllib.request

MARKER = ".backed_up"


def hoy_utc() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def remote_es_remoto(remote: str) -> bool:
    """True si `remote` apunta a un host (rsync lo ve como remoto: tiene ':').
    Sin ':' rsync lo trataría como RUTA LOCAL → "respaldaría" al propio disco del
    VPS fingiendo éxito (la verificación local-contra-local pasa trivialmente).
    Guarda contra ese fallo silencioso: el destino DEBE ser user@host:path."""
    return ":" in remote


def _marker_obsoleto(day_dir: str) -> bool:
    """True si el día ganó/cambió contenido DESPUÉS del marcador (part tardío
    tras incidencia, compactación o re-auditoría posterior): el remoto está
    desfasado y hay que re-sincronizar. Ante cualquier error de E/S devuelve
    True (fail-safe: un día dudoso NUNCA cuenta como respaldado → no se borra).
    Lo usan tanto el respaldo (re-sincronizar) como la retención (candado)."""
    try:
        mt = os.path.getmtime(os.path.join(day_dir, MARKER))
        for root, _, files in os.walk(day_dir):
            for f in files:
                if f != MARKER and os.path.getmtime(os.path.join(root, f)) > mt:
                    return True
        return False
    except OSError:
        return True


def dias_pendientes(data_dir: str, hoy: str | None = None) -> list[str]:
    """Días cerrados + auditados + (sin marcador O con marcador obsoleto),
    ordenados (antiguos 1º)."""
    hoy = hoy or hoy_utc()
    out = []
    for p in sorted(glob.glob(os.path.join(data_dir, "*", "*"))):
        if not os.path.isdir(p) or os.path.basename(p) >= hoy:
            continue                      # jamás el día en curso (ni futuros)
        if not os.path.exists(os.path.join(p, "audit.json")):
            continue                      # sin auditar: aún no se respalda
        if os.path.exists(os.path.join(p, MARKER)) and not _marker_obsoleto(p):
            continue                      # respaldado, verificado y sin cambios
        out.append(p)
    return out


def dias_huerfanos(data_dir: str, gracia_dias: int = 2,
                   now: float | None = None) -> list[str]:
    """Días cerrados hace > gracia_dias SIN audit.json: nadie los auditará ya
    (audit-day solo mira 'ayer') → ni respaldo ni retención los verán. Alertar."""
    now = now if now is not None else time.time()
    limite = time.strftime("%Y-%m-%d", time.gmtime(now - gracia_dias * 86400))
    return [p for p in sorted(glob.glob(os.path.join(data_dir, "*", "*")))
            if os.path.isdir(p) and os.path.basename(p) < limite
            and not os.path.exists(os.path.join(p, "audit.json"))]


def _rsync(args: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def respaldar_dia(day_dir: str, remote: str, ssh_port: int,
                  runner=_rsync) -> bool:
    """Transfiere y VERIFICA un día; escribe el marcador solo si la verificación
    (rsync --checksum en seco, cero cambios pendientes) sale limpia."""
    rel = os.path.join(os.path.basename(os.path.dirname(day_dir)),
                       os.path.basename(day_dir))          # SYMBOL/YYYY-MM-DD
    dst = f"{remote}/{rel.replace(os.sep, '/')}/"
    ssh = f"ssh -p {ssh_port} -o StrictHostKeyChecking=accept-new"
    src = day_dir.rstrip("/\\") + "/"

    try:
        # --delete: el remoto es ESPEJO del día local (sin él, un layout que
        # cambió entre intentos — parts→compactado — dejaría duplicados en un restore)
        r = runner(["rsync", "-a", "--delete", "--mkpath", "-e", ssh, src, dst])
        if r.returncode != 0:
            print(f"FALLO transferencia {rel}: {r.stderr.strip()[:200]}", flush=True)
            return False
        # verificación: checksum + deleciones pendientes, salida debe ser vacía
        v = runner(["rsync", "-aic", "--delete", "--dry-run", "-e", ssh, src, dst])
        if v.returncode != 0 or v.stdout.strip():
            print(f"FALLO verificación {rel}: rc={v.returncode} "
                  f"pendiente={v.stdout.strip()[:200]!r}", flush=True)
            return False
    except subprocess.TimeoutExpired:
        print(f"FALLO timeout {rel} (>900s): se reintenta en el próximo run "
              f"(rsync reanuda)", flush=True)
        return False
    except Exception as e:
        print(f"FALLO {rel}: {type(e).__name__}: {e}", flush=True)
        return False
    with open(os.path.join(day_dir, MARKER), "w") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")
    print(f"OK {rel}", flush=True)
    return True


def alerta(texto: str) -> None:
    """Telegram si hay credenciales en el entorno (EnvironmentFile del service)."""
    tok = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not (tok and chat):
        return
    try:
        body = json.dumps({"chat_id": chat, "text": texto}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{tok}/sendMessage", data=body,
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        print(f"(alerta no enviada: {e})", flush=True)


def main() -> int:
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # → qs/
    sys.path.insert(0, os.getcwd())
    import yaml
    with open("config/instruments.yaml") as f:
        cfg = yaml.safe_load(f)
    b = cfg.get("backup") or {}
    remote, port = (b.get("remote") or "").strip(), int(b.get("ssh_port", 23))
    huerfanos = dias_huerfanos(cfg["data_dir"])
    if huerfanos:                       # cerrados >48h sin auditar: nadie los verá
        rels = [os.path.basename(os.path.dirname(p)) + "/" + os.path.basename(p)
                for p in huerfanos]
        print(f"AVISO: {len(huerfanos)} día(s) cerrados sin auditar >48h: {rels[:6]}")
        alerta(f"⚠️ quant-ingesta: {len(huerfanos)} día(s) cerrados SIN AUDITAR "
               f">48h (ni se respaldan ni se retienen): {rels[:4]}")
    if not remote:
        print("backup: sin destino configurado (backup.remote vacío) — no-op")
        return 0
    if not remote_es_remoto(remote):
        # footgun real (2026-06-13): remote sin ':' → rsync copia al disco LOCAL
        # fingiendo éxito y escribe marcadores falsos → el candado borraría datos
        print(f"backup: ABORTADO — backup.remote='{remote}' no tiene ':' "
              f"(sería ruta local, no el box). Debe ser user@host:path")
        alerta(f"⚠️ quant-ingesta: backup.remote mal configurado ('{remote}': "
               f"falta ':host:path') — respaldo ABORTADO, NO se borra nada")
        return 1
    pendientes = dias_pendientes(cfg["data_dir"])
    if not pendientes:
        print("backup: nada pendiente")
        return 0
    fallos = []
    for d in pendientes:
        if not respaldar_dia(d, remote, port):
            fallos.append(d)
    print(f"backup: {len(pendientes) - len(fallos)}/{len(pendientes)} días OK")
    if fallos:
        alerta(f"⚠️ quant-ingesta: respaldo FALLÓ en {len(fallos)} día(s): "
               f"{[os.path.basename(os.path.dirname(f)) + '/' + os.path.basename(f) for f in fallos][:4]}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
