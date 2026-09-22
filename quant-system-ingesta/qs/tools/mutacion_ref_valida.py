"""ARNES DE MUTACION del guardia de REFERENCIA INVALIDA (`analysis/ref_valida.py`) — CI.

MOTIVACION (mesa, 2026-08-27): «anade mutacion especifica de la nueva guardia». Los tests focales
(48 + 12) acreditan que el guardia hace lo que dice cuando se le llama; **no** acreditan que sea EL
guardia quien mantiene verdes esos tests. Un test puede estar pasando por otra razon — y en este
proyecto ya paso DOS VECES en la serie M-12: produccion gana una defensa mas temprana que emite un
mensaje que tambien casa, el test sigue verde, y la guardia que se creia acreditada llevaba tiempo
muerta.

Este arnes DESACTIVA cada comprobacion, una a una, sobre una COPIA del arbol (jamas sobre el arbol
real) y exige que los tests declarados FALLEN. Una comprobacion cuya mutacion no mata a su test es
decorativa.

REUTILIZA la maquinaria de `tools/arnes_comun.py` (trasladada del gate en V2) — copia limpia por mutacion, linea base
verde-y-valida con sus cuatro condiciones, mordida SEMANTICA (no cualquier rc!=0), huella de las
rutas vigiladas y temporal fuera del repo. **No se reimplementa nada**: un segundo arnes que se
parece pero no es igual seria una fuente de error nueva, que es justo el patron que este proyecto
cataloga.

    python tools/mutacion_ref_valida.py
"""
from __future__ import annotations

import argparse
import io
import os
import shutil
import sys
import tempfile

_AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _AQUI)
sys.path.insert(0, os.path.dirname(_AQUI))

import arnes_comun as M                                            # noqa: E402

REL_PROD = os.path.join("analysis", "ref_valida.py")      # objetivo POR DEFECTO
REL_CARRIL = os.path.join("analysis", "carril.py")
REL_ARTE = os.path.join("analysis", "artefacto.py")
REL_DOC = os.path.join("tools", "guardia_documental.py")
REL_COMP = os.path.join("tools", "guardia_completitud.py")
REL_REG = os.path.join("tools", "registro_sonda.py")
REL_BOOK = os.path.join("ingestion", "book.py")
class _AbortarCorrida(Exception):
    """Salida de control: su codigo sólo se decide después de juzgar huella y limpieza."""

    def __init__(self, codigo):
        super().__init__(codigo)
        self.codigo = codigo


REL_PREVUELO = os.path.join("tools", "prevuelo.py")
FICHEROS_TEST = ('tests/test_agilidad.py', 'tests/test_artefacto.py', 'tests/test_compuertas_ref_invalida.py', 'tests/test_core.py', 'tests/test_guardia_completitud.py', 'tests/test_guardia_documental.py', 'tests/test_propiedades_ref_valida.py', 'tests/test_ref_valida.py', 'tests/test_registro_sonda.py')

# Una fila puede llevar un 4o campo con SU fichero objetivo. Sin el, muta `REL_PROD`.
def _objetivo(fila):
    return fila[3] if len(fila) > 3 else REL_PROD

# (nombre, [(ancla_unica, sustituto)], {test: fragmento EXIGIDO en la salida del fallo})
MUTACIONES = [
    ("R1 quitar el rechazo de NO FINITA (NaN / +-inf pasan a ser markouts)",
     [('    if not np.isfinite(r):\n        return "no_finita"',
       '    if False:\n        return "no_finita"')],
     {'test_clasificar_asigna_la_clase_correcta': 'assert'}),

    ("R1 quitar el GRUPO que atrapa el CERO (rechazo <=0 + banda): vuelve el defecto original",
     [('    if r <= 0.0:\n        return "no_positiva"',
       '    if False:\n        return "no_positiva"'),
      ('    return "ok" if abs(markout_bps(r, p)) < LIMITE_ABSURDO_BPS else "degenerada"',
       '    return "ok"')],
     {'test_clasificar_asigna_la_clase_correcta': 'assert'}),

    ("R1 quitar la clase DEGENERADA (el positivo diminuto vuelve a pasar: el agujero del 1er arreglo)",
     [('    return "ok" if abs(markout_bps(r, p)) < LIMITE_ABSURDO_BPS else "degenerada"',
       '    return "ok"')],
     {'test_los_bordes_de_la_banda_son_los_declarados': 'assert'}),

    ("R1 invertir el ORDEN: la banda antes que la finitud (un NaN saldria 'degenerada')",
     [('    r = float(ref)\n    if not np.isfinite(r):',
       '    r = float(ref)\n    if False:')],
     {"test_clasificar_asigna_la_clase_correcta": "assert"}),

    ("R1 volver a comparar RATIOS en vez del markout (reintroduce la asimetria de E-51)",
     [('    return "ok" if abs(markout_bps(r, p)) < LIMITE_ABSURDO_BPS else "degenerada"',
       '    return "ok" if 0.1 <= r / p <= 10.0 else "degenerada"   # MUTANTE: el defecto E-51')],
     {"test_los_bordes_de_la_banda_son_los_declarados": "assert",
      "test_la_banda_es_SIMETRICA_en_consecuencia": "assert",
      "test_PROPIEDAD_ninguna_referencia_aceptada_produce_un_markout_absurdo": "CONTRAEJEMPLO"}),

    ("R4 contar SOLO una clase de rechazo en vez de las tres",
     [('    return int(cnt["ref_no_finita"][k] + cnt["ref_no_positiva"][k] + cnt["ref_degenerada"][k])',
       '    return int(cnt["ref_no_positiva"][k])')],
     {"test_R4_cuenta_LAS_TRES_clases_no_solo_una": "assert"}),

    ("R4 aflojar el umbral de anomalia (nunca gritaria)",
     [("UMBRAL_R4 = 0.05", "UMBRAL_R4 = 1.0")],
     {"test_R4_avisa_por_debajo_del_umbral_y_GRITA_por_encima": "assert",
      "test_R4_la_frontera_del_umbral_es_ESTRICTA_al_5_por_ciento": "assert"}),

    ("compuerta de CONSUMO: dejar pasar artefactos contaminados",
     [('    if c["total"] and not permitir:', "    if False:")],
     {"test_exigir_limpio_RECHAZA_un_artefacto_contaminado": "DID NOT RAISE"}),

    ("EMPALME: dejar de exigir que el snapshot caiga DENTRO del evento (U <= L <= u)",
     [("            if not (U <= L <= u):", "            if False:")],
     {"test_la_banda_L_MAS_UNO_YA_NO_entra": "DID NOT RAISE",
      "test_un_snapshot_VIEJO_sigue_siendo_hueco": "DID NOT RAISE"},
     REL_BOOK),

    ("CARRIL: volver a resolver el canonico RELATIVO contra el CWD (compuerta ambiental)",
     [("    n = lambda x: os.path.normcase(os.path.realpath(_absoluta(x)))",
       "    n = lambda x: os.path.normcase(os.path.realpath(x))")],
     {"test_P0_2_la_compuerta_NO_depende_del_directorio_desde_el_que_se_lance": "DID NOT RAISE"},
     REL_CARRIL),

    ("CARRIL: dejar producir en el directorio CANONICO con el carril equivocado",
     [("    if conforme(sym, capa, usado) or not _es_canonico(destino, canonico):",
       "    if True:")],
     {"test_el_carril_no_conforme_IMPIDE_producir_para_un_simbolo_certificado": "DID NOT RAISE",
      "test_el_escape_del_carril_NO_se_activa_con_cualquier_valor": "DID NOT RAISE"},
     REL_CARRIL),

    ("ARTEFACTO: devolver la premisa al acusado (la capa sale del manifiesto, no del consumidor)",
     [('    if m.get("capa") != capa_esperada:', "    if False:"),
      ("    if not CA.conforme(sym, capa_esperada, m.get(\"carril_usado\", \"\")):",
       "    if not CA.conforme(sym, m.get(\"capa\", \"\"), m.get(\"carril_usado\", \"\")):")],
     {"test_P0_1_un_artefacto_de_CAPA2_no_se_acredita_como_CONFIRMACION": "Regex pattern did not match"},
     REL_ARTE),

    ("ARTEFACTO: dejar de exigir el simbolo esperado",
     [("    if simbolo_esperado is not None and m.get(\"simbolo\") != simbolo_esperado:",
       "    if False:")],
     {"test_P0_1_el_simbolo_esperado_tambien_se_puede_fijar": "DID NOT RAISE"},
     REL_ARTE),

    ("ARTEFACTO: no validar el contenido al PUBLICAR (un vector desalineado llega a disco)",
     [("    malos = _validar_contenido(arrays, capa, lambda k: arrays[k])", "    malos = []")],
     {"test_P0_1_UN_VECTOR_DESALINEADO_no_pasa": "DID NOT RAISE",
      "test_P0_1_un_mo_que_no_es_de_coma_flotante_no_pasa": "DID NOT RAISE"},
     REL_ARTE),

    ("ARTEFACTO: no validar el contenido al CARGAR (un npz escrito por fuera entra igual)",
     [("    fallos = fallos + _validar_contenido(z.files, capa_esperada, lambda k: z[k])",
       "    fallos = fallos + []")],
     {"test_P0_1_el_contenido_se_valida_TAMBIEN_al_CARGAR": "assert"},
     REL_ARTE),

    ("ARTEFACTO: no comprobar el SHA de los bytes (una marca vieja acredita una sustitucion)",
     [('    if m.get("sha256") != sha:', "    if False:")],
     {"test_una_sustitucion_del_MISMO_TAMANO_solo_la_atrapa_el_SHA": "DID NOT RAISE"},
     REL_ARTE),

    ("ARTEFACTO: dejar que `extra` pise los campos normativos (el agujero exacto de la v1)",
     [('        man["extra"] = extra                      # bajo SU clave: no puede pisar lo normativo',
       "        man.update(extra)")],
     {"test_ATAQUE_2_extra_NO_puede_sobrescribir_la_conformidad": "assert"},
     REL_ARTE),

    ("ARTEFACTO: no publicar el manifiesto (vuelve el npz-sin-marca tras un crash)",
     [("    os.replace(tmp_man, ruta_man)", "    pass  # MUTANTE: el manifiesto no se publica")],
     {"test_EL_ORDEN_SE_COMPRUEBA_EJECUTANDO_no_leyendo_fuentes": "DID NOT RAISE",   # el crash
      # simulado ya no puede ocurrir: la llamada que lo provoca es la que se quita. El bocado
      # SUSTANTIVO es el de abajo — el npz canonico aparece SIN manifiesto.
     
      "test_el_npz_canonico_aparece_SOLO_con_su_manifiesto": "assert"},
     REL_ARTE),

    ("GUARDIA-DOC: volver a descartar la relacion MALA en vez de exigir la BUENA (fallo abierto)",
     [("                    if _es_ancestro(c_doc, c_art):",
       "                    if _es_ancestro(c_doc, c_art) or not _es_ancestro(c_art, c_doc):")],
     {"test_EL_FALLO_ABIERTO_dos_commits_HERMANOS_no_establecen_precedencia": "assert"},
     REL_DOC),

    ("GUARDIA-DOC: volver al commit INTRODUCTOR del documento en vez de al del texto vigente",
     [('        c_doc, _blob = commit_del_texto_vigente(f"docs/{nombre}")',
       '        c_doc, _blob = _commit_introductor(f"docs/{nombre}"), ""')],
     {"test_un_artefacto_ENTRE_la_v1_y_las_reglas_vigentes_NO_pasa": "assert"},
     REL_DOC),

    ("GUARDIA-DOC: dejar de reconocer las reglas S y T (ocho reglas de la sonda, invisibles)",
     [(r'_ID_REGLA = re.compile(r"\*\*([RMCST]\d+(?:-[a-z]+)?)\b")',
       r'_ID_REGLA = re.compile(r"\*\*([RMC]\d+(?:-[a-z]+)?)\b")')],
     {"test_las_reglas_S_y_T_TAMBIEN_se_reconocen": "assert"},
     REL_DOC),

    ("GUARDIA-DOC: dejar de bloquear por cobertura incompleta (se gastaria bajo un prereg a medias)",
     [("    for ident in sorted(set(_ID_REGLA.findall(texto))):",
       "    for ident in sorted(declaradas):")],
     {"test_exigir_cobertura_BLOQUEA_mientras_una_regla_no_tenga_codigo": "assert"},
     REL_DOC),

    ("GUARDIA-DOC P0-7: volver a sellar la PRIMERA aparicion del blob (se puede reactivar una v1)",
     [("    for c in historia:                                 # de la MÁS NUEVA a la más vieja",
       "    for c in reversed(historia):")],
     {"test_P0_7_REACTIVAR_la_v1_despues_de_ver_el_resultado_ya_no_da_verde": "assert"},
     REL_DOC),

    ("GUARDIA-DOC P0-7: dejar de rechazar lo que llega por RENOMBRE",
     [("            if renombres:", "            if False:")],
     {"test_P0_7_un_artefacto_que_llega_por_RENOMBRE_no_se_certifica": "assert"},
     REL_DOC),

    ("GUARDIA-DOC P0-6: volver a aceptar que un commit se preceda a SI MISMO",
     [("    if not a or not b or a == b:", "    if not a or not b or (a == b and False):")],
     {"test_P0_6_el_prereg_y_el_artefacto_EN_EL_MISMO_COMMIT_no_establecen_precedencia": "assert",
      "test_P0_6_la_ancestria_es_ESTRICTA": "assert"},
     REL_DOC),

    ("GUARDIA-DOC P0-5: que `ruta_limpia` deje de comparar el arbol con HEAD",
     [("    return bool(_blob_en_head(rel)) and _blob_del_arbol(rel) == _blob_en_head(rel)",
       "    return bool(_blob_en_head(rel))")],
     {"test_P0_5_la_ruta_limpia_es_lo_que_distingue_congelado_de_editable": "assert"},
     REL_DOC),

    ("GUARDIA-DOC P0-7: volver a inspeccionar UNA sola introduccion del comodin",
     [(r'    return [c.strip() for c in salida.split("\n") if c.strip()]',
       r'    return [c.strip() for c in salida.split("\n") if c.strip()][-1:]')],
     {"test_P0_7_un_COMODIN_con_fechas_sesgadas_ya_no_deja_pasar_al_hermano_anterior": "assert",
      "test_P0_7_se_comprueban_TODAS_las_introducciones_no_una": "assert"},
     REL_DOC),

    ("GUARDIA-DOC P0-7: quitar el orden TOPOLOGICO (git log ordena por FECHA, no por ancestria)",
     [('                  "--reverse", "--", pathspec)', '                  "--", pathspec)')],
     {"test_P0_7_las_introducciones_salen_en_orden_TOPOLOGICO_no_por_fecha": "assert"},
     REL_DOC),

    ("GUARDIA-DOC P0-4: volver a recorrer los CUERPOS de funcion (una anidada acreditaria)",
     [("    for n in arbol.body:", "    for n in ast.walk(arbol):")],
     {"test_P0_4_ninguna_forma_DECORATIVA_acredita_una_regla": "assert"},
     REL_DOC),

    ("GUARDIA-DOC P0-4: aceptar cosas NO invocables (una clase acreditaria una regla)",
     [("        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == simbolo:",
       "        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == simbolo:")],
     {"test_P0_4_ninguna_forma_DECORATIVA_acredita_una_regla": "assert"},
     REL_DOC),

    ("CENSO: volver a mirar solo `analysis/` (6 llamadas reales de `tools/` invisibles)",
     [('PAQUETES = ("analysis", "tools")', 'PAQUETES = ("analysis",)')],
     {'test_una_carga_bajo_tools_ya_no_es_invisible': 'assert'},
     REL_COMP),

    ("CENSO: dejar de vigilar a los ESCRITORES (el agujero del eco vuelve a ser invisible)",
     [('NUMPY_VIGILADAS = ("load", "savez", "savez_compressed", "save")',
       'NUMPY_VIGILADAS = ("load",)')],
     {"test_un_np_savez_fuera_del_publicador_se_ve": "assert"},
     REL_COMP),

    ("CENSO: dejar de resolver alias (`from numpy import load` se escapa)",
     [('        elif isinstance(n, ast.ImportFrom) and n.module == "numpy":', "        elif False:")],
     {"test_una_llamada_REAL_se_ve_escrita_como_se_escriba": "assert"},
     REL_COMP),

    ("CENSO: glob NO recursivo (un subpaquete entero deja de mirarse)",
     [('glob.glob(os.path.join(QS, paq, "**", "*.py"), recursive=True)',
       'glob.glob(os.path.join(QS, paq, "**", "*.py"), recursive=False)')],
     {"test_el_glob_ve_LOS_DOS_NIVELES": "assert"},
     REL_COMP),

    ("CENSO: ignorar el numero de llamadas de una exencion (la exencion se hereda en silencio)",
     [("        if n != esperadas:", "        if False:")],
     {"test_una_SEGUNDA_llamada_en_una_funcion_eximida_rompe_el_build": "assert"},
     REL_COMP),

    ("CENSO: dejar de denunciar la exencion FANTASMA (la v1 tenia una)",
     [("    for clave in sorted(set(EXENTAS) - set(vistas)):", "    for clave in ():")],
     {"test_una_exencion_FANTASMA_se_denuncia": "assert"},
     REL_COMP),

    ("CENSO-SELLADAS: ignorar el recuento aunque el hash sea valido",
     [("        if n_selladas != esperadas:", "        if False:")],
     {"test_sellada_rechaza_segunda_llamada_con_hash_valido": "[SELLADA-second_call]"},
     REL_COMP),

    ("CENSO-SELLADAS: omitir el hash del cuerpo y de sus saltos de linea",
     [('        if hashlib.sha256(fuentes[rel].encode("utf-8")).hexdigest() != sha:',
       '        if False:')],
     {"test_sellada_rechaza_edicion_del_cuerpo": "[SELLADA-body]",
      "test_sellada_rechaza_cambio_de_saltos_de_linea": "[SELLADA-newlines]"},
     REL_COMP),

    ("CENSO-SELLADAS: callar una exencion fantasma sin provocar una excepcion ajena",
     [('            problemas.append(f"{clave}: EXENCIÓN SELLADA FANTASMA — no hay ninguna llamada así.")',
       '            pass  # Se conserva el continue: ninguna fuente ausente se indexa.')],
     {"test_sellada_denuncia_excepcion_fantasma": "[SELLADA-missing]"},
     REL_COMP),

    ("CENSO: aceptar la compuerta dentro de una RAMA (un `except` que se la traga)",
     [("                    if isinstance(stmt, (ast.If, ast.Try)):", "                    if False:")],
     {"test_la_compuerta_que_NO_domina": "assert"},
     REL_COMP),

    ("CENSO: dejar de exigir que la compuerta vaya ANTES (despues ya se ha gastado)",
     [("                if (isinstance(h, ast.Call) and h.lineno < linea_marcada",
       "                if (isinstance(h, ast.Call) and True")],
     {"test_la_compuerta_que_NO_domina": "assert"},
     REL_COMP),

    ("CARRIL: que el escape vuelva a abrir el directorio CANONICO",
     [("    if conforme(sym, capa, usado) or not _es_canonico(destino, canonico):",
       '    if conforme(sym, capa, usado) or not _es_canonico(destino, canonico) or os.environ.get(VAR_ESCAPE) == "1":')],
     {"test_el_escape_NO_deja_escribir_en_el_directorio_CANONICO": "DID NOT RAISE"},
     REL_CARRIL),

    ("REGISTRO: aceptar un simbolo NO invocable (una constante pasaria por implementacion)",
     [("    if not callable(fn):", "    if False:")],
     {"test_una_CONSTANTE_no_es_una_implementacion_ejecutable": "DID NOT RAISE"},
     REL_REG),

    ("REGISTRO: resolver solo la PRIMERA y parar (media campana gastada al descubrir la quinta)",
     [("            fallos.append(str(e))", "            raise")],
     {"test_exigir_listo_reporta_TODAS_las_que_fallan_no_la_primera": "assert"},
     REL_REG),

    ("REGISTRO: dejar de comprobar el sentido CODIGO-SIN-NORMA",
     [("    for ident in sorted(set(REGLAS) - set(declaradas)):", "    for ident in ():")],
     {"test_codigo_SIN_norma_tambien": "assert"},
     REL_REG),

    ("deteccion: volver a la firma ANCHA (|mo|>=1e4), que no acredita ref==0",
     [("    exacta = fin & (mo == objetivo)", "    exacta = fin & (np.abs(mo) >= 1e4 - tol)")],
     {"test_exigir_limpio_distingue_EXACTA_de_CASI_CERO": "assert"}),

    ("PREVUELO: dejar de exigir que el ancla de cada fila sea UNICA (vuelven las anclas muertas)",
     [('            n = texto.count(viejo)\n            if n != 1:', '            n = 1\n            if False:')],
     {"test_un_ancla_MUERTA_es_un_problema": "assert",
      "test_un_ancla_DUPLICADA_es_un_problema": "assert"},
     REL_PREVUELO),

    ("PREVUELO: volver a exigir el nombre EXACTO en vez de subcadena (mentiría sobre 27 filas del libro)",
     [('    return [n for n in nombres if d == n or d in n]', '    return [n for n in nombres if d == n]')],
     {'test_la_semantica_de_los_tests_es_SUBCADENA_como_en_pytest_k': 'assert'},
     REL_PREVUELO),

    ("PREVUELO: reventar con la excepcion cruda si un arnes no importa (los otros dos quedan sin revisar)",
     [('    try:\n        mod = _cargar(cfg["modulo"])\n    except Exception as e:                                     # noqa: BLE001\n        return [f"[{clave}] el arnes NO IMPORTA: {type(e).__name__}: {e}"]',
       '    mod = _cargar(cfg["modulo"])')],
     {"test_un_arnes_que_NO_IMPORTA_se_declara_en_vez_de_reventar": "PROPAGO"},
     REL_PREVUELO),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--solo", metavar="SUBCADENA", default=None,
                    help="corre SOLO las filas cuyo nombre contenga esta subcadena (iterar en "
                         "minutos). El recuento resultante NO es el del arnes integro y se dice.")
    args = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    # ═══ EL PRE-VUELO CORRE SIEMPRE SOBRE LA TABLA ENTERA, ANTES DEL FILTRO ═══
    #
    # Es la leccion del arnes hermano, y aqui costo 11 minutos + 52 copias del arbol descubrir a
    # mano lo que esto dice en 0,4 s. Va ANTES del filtro a proposito: si `--solo` pudiera ocultar
    # una fila con el ancla muerta o un test inexistente, el filtro se convertiria en una forma de
    # no enterarse — que es exactamente el modo de fallo que un arnes existe para impedir un nivel
    # mas arriba.
    import prevuelo                                                    # noqa: E402
    problemas = prevuelo.revisar_arnes("ref")
    if problemas:
        print(f"*** PRE-VUELO: {len(problemas)} problema(s) en la tabla COMPLETA. No se corre nada:")
        for m in problemas:
            print(f"      {m}")
        return 5

    seleccion = list(enumerate(MUTACIONES, start=1))
    if args.solo:
        seleccion = [(n, f) for n, f in seleccion if args.solo.lower() in f[0].lower()]
        if not seleccion:
            print(f"*** `--solo {args.solo}` no casa con ninguna de las {len(MUTACIONES)} filas")
            return 2

    tmp = os.path.realpath(tempfile.mkdtemp(prefix="mutacion_refvalida_"))
    if tmp == os.path.realpath(M.REPO_REAL) or tmp.startswith(os.path.realpath(M.REPO_REAL) + os.sep):
        os.rmdir(tmp)  # mkdtemp propio aún vacío; cualquier fallo de retirada se propaga
        sys.exit(f"El temporal {tmp} cae DENTRO del repo. Aborto: el aislamiento seria ficticio.")

    print(f"arbol real (SOLO LECTURA): {M.QS_REAL}")
    print(f"temporal (fuera del repo): {tmp}")
    huella_antes = M._huella()
    _alcance = (f"{len(seleccion)} de {len(MUTACIONES)} mutaciones (--solo {args.solo!r})"
                if args.solo else f"{len(MUTACIONES)} mutaciones")
    print(f"{_alcance} · copia nueva para cada una · {len(huella_antes)} ficheros vigilados")
    print(f"pre-vuelo sobre las {len(MUTACIONES)} filas: OK\n")

    filas, salida, timeouts, excepcion = [], None, [], None
    try:
        base = M._copia_limpia(tmp, 0)
        todos = sorted({t for _n, fila in seleccion for t in fila[2]})
        razones, recuento, invalida, rc, n_passed, timeout = M._correr(
            base, todos, os.path.join(tmp, "bt_00"), FICHEROS_TEST)
        print(f"  linea base (sin mutar): {recuento}")
        if timeout:
            # ABORTA, pero SIN `return` aqui dentro: el `finally` puede establecer otro resultado al
            # juzgar la deriva del arbol vigilado, y un `return` lo tapaba. Se guarda en `salida` y
            # gana el 4 de la deriva si la hubo, que es lo mas grave de los dos.
            print(f"\n*** LA LINEA BASE AGOTO EL LIMITE ({timeout['limite']}s). NO se ejecuta "
                  f"ninguna mutacion.")
            M._mostrar_timeout("linea base", timeout)
            raise _AbortarCorrida(6)
        problemas = M._problemas_baseline(
            rc, invalida, razones, n_passed, len(todos), conteo_exacto=False)  # tests parametrizados
        if problemas:
            print(f"\n*** LINEA BASE NO UTILIZABLE: {'; '.join(problemas)}")
            print("*** Un rojo tras mutar no probaria nada si la base ya no esta limpia. ABORTO.")
            raise _AbortarCorrida(3)
        # UN TEST DECLARADO QUE NO EXISTE NO PUEDE MORDER, y hasta hoy se contaba como mordida:
        # renombré un test, dejé la fila apuntando al nombre viejo y el arnés lo dio por bueno. Un
        # arnés que aprueba una fila que no ejecuta nada es exactamente el objeto que este arnés
        # existe para detectar, un nivel más arriba. (2026-08-28, encontrado corriéndolo.)
        import subprocess as _sp
        _col = _sp.run([sys.executable, "-m", "pytest", "--collect-only", "-q", *FICHEROS_TEST],
                       cwd=base, capture_output=True, text=True, encoding="utf-8", errors="replace")
        _nodos = _col.stdout
        _huerfanos = [t for t in todos if t not in _nodos]
        if _huerfanos:
            print(f"\n*** FILAS QUE DECLARAN TESTS INEXISTENTES: {', '.join(_huerfanos)}")
            print("*** Un test que no existe no puede FALLAR con su marcador, asi que su fila no")
            print("*** acredita nada. (NO dice «aprobaria siempre»: `_juzgar` compara por pertenencia")
            print("*** EXACTA y la fila saldria COLATERAL - NO ACREDITA. La mesa demostro que la")
            print("*** version anterior de este mensaje era FALSA, y un arnes que miente sobre su")
            print("*** propio alcance es peor que uno que calla.)")
            raise _AbortarCorrida(4)
        print(f"  linea base VERDE y valida: {n_passed}/{len(todos)} tests, rc=0")
        print(f"  los {len(todos)} tests declarados EXISTEN en la coleccion\n")

        for n, fila in seleccion:
            nombre, cambios, tests_causa = fila[0], fila[1], fila[2]
            copia = M._copia_limpia(tmp, n)
            prod = os.path.join(copia, _objetivo(fila))
            t, ok = io.open(prod, encoding="utf-8").read(), True
            for viejo, nuevo in cambios:
                if t.count(viejo) != 1:
                    filas.append((nombre, "*** ANCLA NO UNICA ***", f"{t.count(viejo)} ocurrencias", ""))
                    print(f"  {'*** ANCLA NO UNICA ***':38} {nombre}")
                    ok = False
                    break
                t = t.replace(viejo, nuevo, 1)
            if not ok:
                continue
            io.open(prod, "w", encoding="utf-8", newline="\n").write(t)
            razones, recuento, invalida, rc, n_passed, timeout = M._correr(
                copia, sorted(tests_causa), os.path.join(tmp, f"bt_{n:02d}"), FICHEROS_TEST)
            if timeout:
                # Registrar y SEGUIR. Es la fila que costo dos horas el 2026-09-05: la corrida murio
                # en la 152 de 199 y hubo que repetirla entera.
                estado = "*** TIMEOUT - NO ACREDITA ***"
                # `muestra` es la CADENA para pantalla; `parcial` trae los dos canales enteros.
                detalle = (f"agoto {timeout['limite']}s"
                           + (f" · muestra: ...{timeout['muestra'][-90:]}"
                              if timeout["muestra"] else " · sin salida parcial"))
                filas.append((nombre, estado, recuento, detalle))
                timeouts.append(nombre)
                print(f"  {estado:38} {nombre}")
                print(f"  {'':38} {detalle}")
                M._mostrar_timeout(nombre, timeout)
                M._cerrar_fila_timeout(tmp, copia, os.path.join(tmp, f"bt_{n:02d}"), huella_antes)
                continue
            if invalida:
                estado, detalle = "*** INVALIDA (modulo roto) ***", "ni acredita ni desacredita"
            else:
                estado, detalle = M._juzgar(tests_causa, razones, n_passed)
            filas.append((nombre, estado, recuento, detalle))
            print(f"  {estado:38} {nombre}")
            if detalle:
                print(f"  {'':38} {detalle}")
    except _AbortarCorrida as exc:
        salida = exc.codigo
    except BaseException as exc:
        excepcion = exc
    finally:
        difs, fallo_limpieza = M._finalizar_copia(tmp, huella_antes)

    if fallo_limpieza is not None:
        print(f"*** LIMPIEZA INCOMPLETA: {fallo_limpieza}")
        if excepcion is not None:
            excepcion.add_note(f"Además falló la limpieza: {fallo_limpieza}")
    if any(difs):
        print(f"\n*** EL ARBOL REAL CAMBIO durante la corrida: {difs}")
        salida = 4
    elif fallo_limpieza is not None:
        salida = 7
    if excepcion is not None:
        raise excepcion
    if salida is not None:
        return salida

    malas = [f for f in filas if not f[1].startswith("ROJO")]
    print(f"\n{len(filas) - len(malas)}/{len(seleccion)} comprobaciones MUERDEN con su marcador o fragmento declarado")
    if timeouts:
        # SIN MEDIR no es NO MUERDE, y ninguna de las dos acredita. Va aparte para que el recuento
        # de arriba no se lea como si esas filas se hubieran evaluado.
        print(f"{len(timeouts)} fila(s) SIN MEDIR por agotar el limite de {M.TIMEOUT_S}s: {timeouts}")
        print("No cuentan como mordida ni como salto de plataforma: hay que volver a medirlas.")
    if args.solo:
        print(f"  *** SUBCONJUNTO (--solo {args.solo!r}): esto NO es el recuento del arnes integro.")
        print(f"  *** El integro sobre las {len(MUTACIONES)} filas es OBLIGATORIO antes de cualquier")
        print(f"  *** paquete; este numero sirve para ITERAR, no para acreditar.")
    print("\n  LIMITES, y son los mismos que los del arnes hermano:")
    print("   · acredita la SENSIBILIDAD de los tests, NO la CORRECCION del codigo.")
    print("   · cada mutacion corre con `-k` sobre SUS tests declarados: un test no seleccionado que")
    print("     la mutacion rompiera seria invisible aqui. No se afirma que no exista.")
    # `timeouts` va EXPLICITO y no confiado a que su estado no empiece por «ROJO»: el rc distinto de
    # cero ante un limite agotado es contrato, no una consecuencia del formato de una cadena.
    return 0 if (not malas and not timeouts) else 1


if __name__ == "__main__":
    sys.exit(main())
