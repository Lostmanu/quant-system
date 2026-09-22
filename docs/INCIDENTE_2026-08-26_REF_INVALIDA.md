# INCIDENTE 2026-08-26 — REFERENCIA INVÁLIDA EN LA RUTA DEL MARKOUT

**Estado: ABIERTO.** Registro del incidente e **invalidación de resultados**, por dictamen de la mesa
del 2026-08-26. Este documento no propone reparaciones: las reglas van en
`docs/ESPEC_POST_INCIDENTE_REF_VALIDA.md`, congelado aparte y antes del código.

---

## 1. Los dos defectos

**P0-A — productivo.** `analysis/pilot_observer.py:122` calculaba el markout sin comprobar que la
referencia fuese un precio válido:

```python
mo[i, k] = lado * (float(ref_px[best]) - e["px"]) / e["px"] * 1e4
```

Con `ref_px = 0` devuelve exactamente `−lado·10.000,00 bps`. **Es un valor finito**, así que el
`isfinite` de toda la cadena aguas abajo lo acepta como observación legítima y lo promedia.

La equivalencia es exacta y no admite otra lectura:

```
mo == −lado·10.000    ⟺    (ref − px)/px == −1    ⟺    ref == 0
```

**P0-B — científico, e independiente.** El pre-registro congelado (`docs/PREREG_MAKER_LIGHTER.md`)
manda, para un símbolo con identidad certificada: *«Certificada → **mid de Binance** como `precio_ref`
en todos los horizontes»*, y nombra *«LIT→mid Binance LITUSDT (ratio 1,001)»*. LIT y DOGE están
certificados (ρ_5m 0,9826 / 0,9521). `analysis/confirm_runner.py:152-157` pasa
`chd.get_trades(...)["price"]`: **el trade más cercano, no el mid.**

**Sanear P0-A no corrige P0-B.** Son dos defectos, no dos caras del mismo.

## 2. Alcance, medido

Censo versionado: `tools/censo_ref_invalida.py`. Los números de esta sección **salen de esa
herramienta**, no de una lectura a mano — que es la razón por la que la mesa rechazó la primera
versión de este informe.

```
RECIBO de la corrida citada
  sha256_censo         09f02a93bb222a2f75566123a79c8b6f4ab1c6fa9d6fa7820de445d32e19f0b4
  sha256_manifiesto    adbb0d93eb5a948a52e2b3c199590867f9205943e1faa81727620d84c8b1815a
  n_ficheros           839
  total_ref0           15.540
```

| bloque | símbolo | Δ | celdas ref=0 | de finitos | % | ficheros |
|---|---|---|---|---|---|---|
| `lighter_confirm` | DOGE | 5s | 5.570 | 446.162 | **1,2484 %** | 70 |
| `lighter_confirm` | DOGE | 25s | 6.072 | 447.498 | **1,3569 %** | 69 |
| `lighter_confirm` | LIT | 5s | 500 | 1.032.151 | 0,0484 % | 35 |
| `lighter_confirm` | LIT | 25s | 512 | 1.160.956 | 0,0441 % | 35 |
| `lighter_pilot` | DOGE | 1s/5s/25s | 817 / 843 / 1.072 | ~58-67 k | 1,26-1,60 % | 10 |
| `lighter_pilot` | LIT | 1s/5s/25s | 12 / 58 / 65 | ~118-160 k | 0,010-0,041 % | 3-5 |
| `lighter_pilot` | WTI | 25s | 15 | 66.950 | 0,0224 % | 1 |
| `lighter_capa2` | WTI | 25s | 4 | 86.105 | 0,0046 % | 1 |

**Dos lecturas, y las dos importan:**

- **DOGE está contaminado ~30× más que LIT** (1,3 % frente a 0,04 %).
- **Capa 2 está prácticamente limpia.** Capa 2 marca contra los prints del propio Lighter
  (`maker_capa2_runner.py:125`); el piloto marca contra Binance. **El defecto vive en el carril de
  referencia Binance**, no en el estimador.

## 3. Efecto sobre el número decisivo

En la celda del titular (LIT × 25 s × AGITADO × cohorte LENTA) hay **1 celda contaminada de 4.413**.
Mismo estimador, mismos npz, excluyendo sólo las celdas con firma de `ref=0`:

```
LENTA [ 5s]   CON  +2,61 (t  +0,29, n_eff 78,5)   →   SIN  +10,38 (t +11,90, n_eff 25,7)
LENTA [25s]   CON +18,24 (t  +6,69, n_eff 79,0)   →   SIN  +15,60 (t  +9,22, n_eff 14,7)
```

**Un solo fill mueve el titular 2,64 bps**, y la aritmética es elemental: un ±10.000 en un día de ~50
fills desplaza esa media diaria ~200 bps, y 200/79 ≈ 2,5 bps sobre la media de medias.

**El `n_eff` cae de 79,0 a 14,7.** El día atípico DEcorrelaba la serie de medias diarias; al quitarlo
aflora la autocorrelación real. El «n_eff 79 = 79 días independientes» estaba sostenido en parte por
un artefacto.

## 4. Qué queda INVALIDADO

Por dictamen de la mesa (2026-08-26):

- **El `+18,24` queda invalidado como resultado confirmatorio.** **No se sustituye por `+15,60` ni
  por ninguna otra cifra.** Hoy no hay número.
- **Todo lo que dependa del carril Binance en LIT/DOGE**, incluida la auditoría **A11**.
- **DOGE pasa a NO EVALUABLE** — ni negativo ni positivo.
- **`+11,19` antisimétrico**: procede del estimando incorrecto y contaminado. No es comparable con el
  suelo de medición de ~0,8 bps del prereg (son magnitudes distintas: mediana/base contra
  descomposición condicional por lados y horizonte sobre fills seleccionados).

**Qué NO queda invalidado:**

- **La capa 2**, marcada contra Lighter y ajena a P0-B (4 celdas contaminadas de 170.643).
- **La capa 3 transaccional**, que no toca esta ruta. Sigue congelada y verde (`7ba8c6c`,
  run 33000187058).
- El conjunto protegido, **intacto y verificado**: `data_hist/blocks_quarantine_heldout/` contiene
  exactamente `LIT_2026-06-30` y WTI 06-08..06-30.

## 5. Un re-cálculo que sale FAVORABLE, y por qué no vale

`tools/censo_ref_invalida.py --forense` corre el screen congelado **dos veces** —original y con las
celdas contaminadas a `NaN`— sin tocar una línea de su lógica (suelos, densidad, BHY, unanimidad).
El veredicto §3 pasa de `INCONCLUSO` a `NULA MUERTA — el edge es HABILIDAD`.

**Eso no es un resultado, y se registra aquí precisamente para que no pueda citarse como tal:**

1. Son **datos ya vistos**. El held-out está gastado. Un re-análisis explora; no confirma.
2. **P0-B sigue abierto**: esa corrida mide el estimando equivocado, sólo que con un defecto menos.
3. La dirección del cambio es **la más favorable posible para la casa**, lo cual es motivo de
   sospecha y no de alivio. Quitar valores de ±10.000 deshincha la varianza y sube todos los `t`
   mecánicamente: la familia BHY entera cambia de base y los `t` de las dos corridas no son
   comparables como evidencia.

La herramienta imprime este aviso antes de la corrida saneada. Si alguna vez se cita como resultado,
el error será de quien lo cite.

## 6. Cómo se encontró — y qué falló en el camino

Lo encontró un **refutador adversarial** al que se le encargó tumbar una afirmación mía sobre el
crecimiento del componente simétrico. La afirmación cayó, y al verificar *por qué* cayó apareció el
defecto.

**Cuatro afirmaciones mías del 2026-08-26 se retiraron**, todas por el mismo vicio —convertir un
número en una historia antes de calcularle su test—: el crecimiento de 9,73× (denominador con
t +0,18, y además el residuo del defecto); la coincidencia del simétrico a 5 s con el medio-spread;
el medio-spread propio de 1,3 bps «con instrumento validado» (la validación era el mismo bit que el
71-91 % ya reportado, y las cifras estaban **hardcodeadas** en el arnés sin artefacto); y la lectura
del antisimétrico como basis identificado (con dos puntos no se separa nivel de deriva que satura —
cosa que `ENCARGO_REDERIVACION_I5.md` ya tenía escrita).

**Y tres correcciones más de la mesa, sobre el propio informe del defecto:**

- **El primer detector no demostraba ceros.** Usaba `abs(mo) >= 9999.99`, que también captura
  `ref ≈ 2·px` y movimientos >100 %. La firma correcta es de signo (§1). En estos datos las dos
  coinciden —1.012 celdas, cero discrepancias— pero eso es un hecho de estos datos, no una propiedad
  del detector.
- **Los conteos no eran reproducibles**: existían sólo en el informe. De ahí
  `tools/censo_ref_invalida.py`, con manifiesto y recibo.
- **El `RuntimeWarning log(0)` de `trailing_vol` NO acreditaba ceros en Binance.** Yo lo cité como
  prueba de que «la casa ya lo sabía». Falso: esa función recibe `tts/tpx`, que son **trades de
  Lighter** (`confirm_runner.py:81,149`). Otra cinta. Los ceros de Binance no se conocían.

**La lección de método, que es la que vale para la próxima:** el arnés `anatomia_del_18_24.py` tenía
una puerta que abortaba si no reproducía el titular EXACTO. La pasó — porque el titular se calculó
**con** el fill corrupto dentro. **Una puerta de reproducción acredita fidelidad al número publicado,
nunca su corrección.** No podía cazar esto, por diseño. Lo cazó un refutador con el encargo explícito
de tumbar, no de comprobar.

## 6-bis. La primera reparación fue rechazada, y con razón (2026-08-27)

La mesa reauditó el commit `ffc53d6` y dictaminó **NO PUSH y NO SONDA**. Siete hallazgos bloqueantes,
todos ciertos, y **todos sobre la reparación, no sobre el defecto**:

| qué estaba mal | qué se hizo |
|---|---|
| el documento se tituló `PREREG` y se escribió **después** del forense que dio la vuelta al veredicto | renombrado a **especificación post-incidente**, con su §0 contando la cronología real; registrado **E-42**; el pre-registro genuino de la sonda vive aparte en `docs/PREREG_SONDA_COBERTURA.md` |
| el guardia exigía `finito and > 0`: **un `ref = 1e-9` seguía pasando** y daba la misma firma | tercera clase `degenerada` (banda `[px/10, px·10]`), tras comprobar que rechazarla es un **no-op** sobre los datos actuales |
| «el defecto vive en el carril Binance», con 4 celdas de capa 2 delante | validación **compartida** en `analysis/ref_valida.py`, usada por `realized_markouts` **y** `maker_sim.markouts` |
| la regla decía «se emite en el npz» y el código descartaba los contadores | fichero **lateral** `{sym}_{day}.contadores.json`; el npz no se toca (identidad-byte M-10) |
| R4 en **un** llamador de cinco y contando **una** de las tres clases | función pura `ref_valida.linea_r4`, cableada en los **cinco** |
| el STOP del carril era documental: nada impedía escribir un artefacto `ok` no conforme | compuerta **fail-closed** en `confirm_runner`, con escape explícito por variable de entorno |
| los npz contaminados seguían siendo consumibles | `confirm_screen._cells` **se niega** a leerlos; escape forense explícito |
| el recibo no ligaba ruta con bytes (permutar hashes no lo cambiaba) y leía cada fichero dos veces | manifiesto canónico `ruta → fecha → bytes → SHA`, **una** lectura, y el `np.load` sobre esos mismos bytes |
| faltaban tests load-bearing y mutación del guardia nuevo | **81 tests** y `tools/mutacion_ref_valida.py`, **8/8**, en CI |

**Y el arnés nuevo encontró dos defectos que nadie buscaba** (E-49, E-50): la regla del guardia estaba
escrita **dos veces** —ninguna copia era load-bearing por sí sola— y la maquinaria de mutación
**compartida** era ciega a los tests parametrizados desde siempre, porque su regex paraba en `[`. El
arnés del gate nunca tuvo filas parametrizadas, así que el defecto vivió invisible **en el instrumento
que acredita a los demás**.

## 7. Lo que queda por hacer

| # | qué | estado |
|---|---|---|
| 1 | especificación del mid y política de referencia inválida | **hecho** (post-incidente, no prereg): `docs/ESPEC_POST_INCIDENTE_REF_VALIDA.md` |
| 2 | guardia R1-R4 **compartido** por los dos brazos + tests | **hecho**: `analysis/ref_valida.py`; 48 + 12 + 21 tests |
| 3 | censo versionado con manifiesto ligado y recibo | **hecho**: `tools/censo_ref_invalida.py` v2 |
| 4 | recalcular la familia completa (masa, densidad, BHY, unanimidad) | **hecho, y marcado forense**: `--forense` |
| 5 | compuertas fail-closed (carril no conforme, consumo de contaminados) | **hecho**, con tests que las hacen **disparar** |
| 6 | mutación específica del guardia nuevo, en CI | **hecho**: `tools/mutacion_ref_valida.py`, **8/8** |
| 7 | pre-registro **genuino** de la sonda, con umbrales numéricos | **hecho**: `docs/PREREG_SONDA_COBERTURA.md` |
| 8 | **ejecutar la sonda**: ¿tiene CHD orderbook de `LITUSDT`/`DOGEUSDT` en la ventana? | **pendiente** — necesita red, créditos y autorización expresa |
| 9 | re-derivar contra mid, o abrir estudio prospectivo separado si no hay cobertura | **pendiente**, depende de (8) |
| 10 | censo del defecto en el resto del programa (capítulo 1, otras rutas) | **pendiente** |

**Suspendido por dictamen hasta cerrar esto:** funding, coste de la segunda pata y selección adversa.
Medirlos ahora sería explicar un número que ya no es científicamente válido.

**Producción:** STOP vigente, campaña sin arrancar, held-out no leído, conjunto protegido intacto.
