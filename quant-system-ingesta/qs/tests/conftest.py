# V2 lote 3: sale la redirección del consumidor retirado; se conserva la vigilancia
# de las raíces históricas .git/qs-* en todos los tests.
import hashlib as _hashlib
import os as _os
import stat as _stat
import subprocess as _sp

import pytest as _pytest




# ═══ Y SE VIGILA, no solo se redirige (revision adversarial de M-13.7) ═══
#
# La redireccion de arriba cubre UNA raiz. Lo que de verdad se quiere garantizar es que ningun test
# escriba bajo `.git/qs-*` del repositorio real, sea por la raiz que sea: esta huella lo comprueba
# despues de CADA test, sola. Fuera de un repositorio (la copia del arnes de mutacion) no hay nada
# que vigilar y no hace nada.
_QS = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))


def _raiz_git_comun():
    try:
        r = _sp.run(["git", "rev-parse", "--git-common-dir"], cwd=_QS, capture_output=True,
                    text=True, encoding="utf-8", errors="replace")
    except Exception:
        return None
    if r.returncode != 0 or not r.stdout.strip():
        return None
    return _os.path.abspath(_os.path.join(_QS, r.stdout.strip()))


_GIT_COMUN = _raiz_git_comun()


def _huella_qs_en_git():
    if not _GIT_COMUN:
        return None
    h = {}
    for sub in ("qs-consumo-candidato", "qs-gate-b"):
        p = _os.path.join(_GIT_COMUN, sub)
        if not _os.path.lexists(p):
            h[sub] = None
            continue
        entradas = {}
        for raiz, dirs, ficheros in _os.walk(p, followlinks=False):
            dirs.sort()
            ficheros.sort()
            rel_raiz = _os.path.relpath(raiz, p).replace(_os.sep, "/")
            for nombre in dirs + ficheros:
                q = _os.path.join(raiz, nombre)
                rel = nombre if rel_raiz == "." else f"{rel_raiz}/{nombre}"
                try:
                    st = _os.lstat(q)
                    if _stat.S_ISLNK(st.st_mode):
                        entradas[rel] = ("SYMLINK", _os.readlink(q))
                    elif _stat.S_ISDIR(st.st_mode):
                        entradas[rel] = ("DIR",)
                    elif _stat.S_ISREG(st.st_mode):
                        with open(q, "rb") as fh:
                            entradas[rel] = ("FILE", _hashlib.sha256(fh.read()).hexdigest())
                    else:
                        entradas[rel] = ("OTRO", int(st.st_mode))
                except OSError as exc:
                    entradas[rel] = ("ILEGIBLE", type(exc).__name__)
        h[sub] = entradas
    return h


@_pytest.fixture(autouse=True)
def _ningun_test_escribe_en_el_git_real():
    antes = _huella_qs_en_git()
    yield
    despues = _huella_qs_en_git()
    assert antes == despues, (f"un test ha escrito en el .git REAL ({_GIT_COMUN}): antes={antes} "
                              f"despues={despues}")
