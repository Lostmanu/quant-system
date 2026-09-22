# AUDITORÍA DEL MÉTODO — registro de afirmaciones falsas, defectos y correcciones

> **Qué es esto.** Un registro acumulativo de **todo lo que se afirmó y resultó falso**, todo defecto
> encontrado y toda corrección aplicada durante el desarrollo de este sistema. Incluye los errores de
> quien escribe el sistema, los de quien lo audita, y los de quien audita al auditor.
>
> **Por qué existe con este formato.** El campo que lo hace útil no es *qué* se encontró, sino
> **QUIÉN lo encontró y CÓMO**. Una lista de bugs no dice nada sobre el método. Una lista de bugs
> con su descubridor mide la eficacia relativa de cada instrumento de verificación — y esa medida es
> el único resultado de este documento.
>
> **Qué NO es.** No es una lista de logros, no es una disculpa, y no acredita la calidad de nada.
> Un registro de errores propios es condición necesaria del rigor, no prueba de él: se puede llevar
> un registro impecable de un trabajo malo.

---

## 0. REGLAS DEL REGISTRO

1. **Se anota lo que resultó FALSO, no lo que resultó difícil.** Un problema duro bien resuelto no
   entra aquí. Una afirmación cómoda que no aguantó la medida, sí.
2. **Se anota antes de corregir.** Si se corrige primero y se anota después, lo que se anota es la
   versión ya digerida.
3. **El descubridor se anota con precisión**, y «el propio autor» solo cuenta si lo encontró **antes**
   de que se lo dijeran o de que un instrumento lo señalase.
4. **Las entradas no se borran.** Si una entrada resulta a su vez equivocada, se añade otra que la
   corrija, con su fecha. Este documento ya tiene una: **X-07 reclasifica el mecanismo de X-05**.
   *(Esta regla citaba «E-21» cuando esa entrada aún no existía; **hoy sí existe** (§1.1) y la referencia ya resuelve. Se deja constancia de que la referencia colgó un día en un
   documento sobre afirmaciones falsas, en su propia sección de reglas. Se deja anotado en vez de
   corregido en silencio, que es de lo que trata la regla.)*
5. **Nada se declara verificado sin decir con qué se verificó.** «Comprobado» sin método no vale.

---

## 1. EL REGISTRO

Clave de descubridores: **AUTOR** (criterio propio, antes de que nada lo señalase) · **CI** (integración
continua) · **ARNÉS** (harness de mutación) · **SONDA** (medición escrita a propósito para dudar de una
hipótesis propia) · **TRINQUETE** (comprobación automática autoimpuesta, p. ej. CENSO-4) ·
**REV-ADV** (revisión adversarial automatizada, montada por el autor) · **REV-EXT** (revisor externo
humano) · **PROVEEDOR** (un tercero: un correo, un panel) · **SUITE** (la batería de tests LOCAL —
distinta del CI, y ha encontrado cosas que el CI no vio) · **PROPIETARIO** (Manuel: preguntó por una
carpeta que nadie había declarado y destapó el hueco de `.claude/`) · **PROPIEDADES** (falsificador
por propiedades: genera entradas adversariales de un dominio declarado y busca el contraejemplo —
la única clase que no LEE ni EJECUTA lo escrito, sino que **inventa la entrada que nadie escribió**).

### 1.1 · Afirmaciones del AUTOR que resultaron falsas

| id | qué se afirmó | qué resultó | descubridor | cómo |
|---|---|---|---|---|
| E-01 | «`301 passed`» como estado del árbol entregado | medida de un árbol anterior a las últimas ediciones | AUTOR | al reejecutar |
| E-02 | «arnés 174/177» | numerador y denominador falsos; el denominador real era **184** | AUTOR | al contar por AST |
| E-03 | Un prefijo de escritura se reconoce por `e.pos >= len(texto.rstrip())` | solo acierta si el corte cae en frontera de token; **227 de 264** cortes reales se declaraban corrupción → STOP eterno | **CI** | por azar: el `host` del runner es más largo que el de la máquina de desarrollo y movía un corte fijo |
| E-04 | El patrón del *ledger 4* estaba aplicado donde tocaba | aplicado en **3 de 6** `finally`; los otros tres soltaban la única barrera existente | **REV-ADV** | lectura dirigida por lentes |
| E-05 | «ningún prefijo de este protocolo produce UTF-8 inválido» | falso: `ensure_ascii=False` y el `host` va primero, así que un corte parte caracteres multibyte | **REV-ADV** | ídem |
| E-06 | Primer predicado de cola UTF-8 cortada | devolvía `None` ante un byte de continuación en vez de retroceder al líder: fallaba 2 de ~1.500 | **SONDA** | enumeración antes de implementar |
| E-07 | Tres guardias nuevas con `causa` escrita del texto de la aserción del test | la `causa` se verifica **por ausencia** y debe ser el mensaje de PRODUCCIÓN; las tres salieron espurias | **ARNÉS** | criterio propio, documentado y violado por su autor |
| E-08 | «dos causas muertas» | barrido solo de las 5 guardias que se reparaban; el barrido completo da **16 muertas y 41 laxas de 106** | **REV-EXT** | preguntó por el resto |
| E-09 | Suite verde tras cambiar `crear_lock` | solo se corrió el fichero de test que se estaba editando; el rojo vivía en otro | **CI** | suite completa |
| E-10 | `assert not os.path.exists(ruta_lock + ".tmp.<tx>")` comprueba algo | nombre que el protocolo ya no produce: **assert vacío**, siempre verdadero. Y estaba duplicado en el test de al lado | AUTOR | al reapuntar el test |
| E-11 | El dossier para el revisor externo estaba al día | **9 contradicciones internas**, 5 de ellas premisas falsas (tres cifras distintas para el mismo objeto, dos `HEAD` a quince líneas, «cuatro commits» sobre una tabla de cinco) | **REV-ADV** | releerlo como lo leería el destinatario |
| E-12 | «demostrado término a término» (equivalencia de dos predicados de liveness) | sin demostración, y no aguanta: uno compara el host como cadena y el otro como hash de 48 bits, en instantes distintos | **REV-ADV** | cotejo contra el código |
| E-13 | «sigue sin haber copia de seguridad» | **falsa**. Hay réplica externa fuera de la máquina, funcionando desde junio, con recuperación automática tras la caída | **REV-EXT** | preguntó por la réplica externa |
| E-14 | Negativo afirmado desde `systemctl list-timers \| head -8` | la línea que lo refutaba estaba **por debajo del corte** | AUTOR | tras E-13 |
| E-15 | «32 llamadas destructivas crudas» como una sola cifra | mezcla `unlink` (destruye lo que nombra) con `replace` (destruye su **destino**); el segundo no estaba en ninguna tabla de coste | **REV-EXT** | desglosó |
| E-16 | La réplica está bien porque hay 933 ficheros de 939 | contar prueba **presencia**, no integridad: un truncado también cuenta como uno | **REV-EXT** | propuso comparar tamaños |
| E-17 | El VPS es EC2 y la IP se liberó al parar | es **de otro proveedor**; la IP seguía asignada y resolvía al hostname del correo | **PROVEEDOR** | correo del proveedor |
| E-18 | `eco_check.sh` verifica integridad con «los 10 ficheros más recientes» | muestra equivocada: lo interesante estaba en el **borde del hueco**, no al final | AUTOR | tras leer su propia salida |
| E-19 | Script pasado por `stdin` a `bash -s` con un `ssh` dentro | el `ssh` interno **consume el resto del script**; la salida se cortaba en silencio | AUTOR | al medir por qué no salía nada |
| E-20 | Heredoc para pasar Python con comillas | corrompe los escapes — **trampa ya documentada en este mismo proyecto**, pisada otra vez | (el propio error) | `SyntaxError` |
| E-21 | «61 días auditados frente a 21-28 requeridos: **estás listo**», repetido en cuatro mensajes como conclusión de todo lo demás | **ventana equivocada**. Los 61 días son la sonda de **Binance** = capítulo 1, cerrado y NEGATIVO. El eco que juzga la apelación corre sobre **Lighter** (`ECO_CONTEO_FASE0.md` se titula «ECO de LIT»; sus 52 h iniciales coinciden con el archivo de Lighter; y `LIT` **ni siquiera está** entre los 8 símbolos de Binance) | **REV-EXT** | lo levantó como *pregunta*, señalando los dos ficheros que la zanjan |

> **E-21 es el más caro de los 21.** No es un número mal copiado: es la conclusión hacia la que
> apuntaba todo el trabajo del día. Y es el mismo defecto que este documento cataloga seis veces en
> el revisor externo — *vista parcial → conclusión sobre el todo*— cometido por el autor sobre la
> pregunta más importante. La medida (61 días auditados) era correcta; el todo (estar listo) no se
> comprobó nunca contra qué dato necesita el análisis.
>
> Nótese además el modo del descubrimiento: el revisor **no afirmó** que la ventana fuera otra. Dijo
> «no lo afirmo, es la clase de conclusión con la que me he equivocado seis veces hoy», y señaló los
> dos ficheros. Preguntar con la calibración puesta encontró en un mensaje lo que cuatro mensajes de
> afirmación no habían visto.
| E-22 | «El colector lleva sin tocarse desde **nueve días ANTES** del blocker» — narrativa de negligencia | **artefacto de mezclar dos relojes**: comparó el `mtime` de `collector.py` (6-jul) con el **último commit** del blocker (15-jul) en vez de con su **creación** (7-jul). La secuencia real es colector el 6, blocker el 7, pivote el 8: **un día para detectarlo, dos para pivotar** — reflejo, no negligencia | **REV-EXT** | pidió la fecha de creación |
| E-23 | «No hay registro de que la decisión A/B/C se tomara» | **falso**. Lo hay, en `MESA_ECO_BRIEFING.md` (10-jul) y en las fechas de creación de `eco_conteo_wti.py`, `eco_fase2_wti.py`, `eco_runner_lit.py`. Se dedujo de que `LEDGER` y `ESTADO` paran el 6-jul, **sin mirar el resto del repo** | AUTOR | al buscar el vendor que Manuel mencionó |
| E-24 | «La rama de 5 s está aplazada, así que **instrumentar el colector NO es urgente**; sería alcance de más» | **falso, y era una recomendación**. Se dedujo de UNA línea del briefing sin leer `PREREG_ECO_LIT_INSUMOS.md`, que declara la acumulación del colector **«ruta crítica, no lujo»**: el 2º símbolo no-token a 50 ms es «lo ÚNICO» que responde A2 | **REV-EXT** | condicionó correctamente («si la rama vive…») y el autor resolvió mal el condicional |
| E-25 | «Sustituir la ruta del colector por la del vendor sin dictamen sería **aflojar**» | sobrepasado. *«Aflojar JAMÁS»* protege reglas **congeladas**; `PREREG_ECO_LIT_INSUMOS.md` dice «BORRADOR, **NO congelado**». No es una regla relajada: es **una decisión que nunca se cerró** | **REV-EXT** | leyó la cabecera que el autor había citado sin usar |

> **E-22 nombra una disciplina que faltaba.** En este repo conviven **cuatro relojes** con el mismo
> aspecto de dato: `mtime`, fecha de commit, fecha de creación (`git log --diff-filter=A`) y la fecha
> que el contenido *afirma*. Mezclar dos produjo una narrativa falsa. Regla: **toda reconstrucción
> cronológica usa un solo reloj y lo nombra.** Misma familia que `medida.py`.

> **E-23, E-24 y E-25 son el mismo defecto que E-21 y que X-01..X-06**: vista parcial → conclusión
> sobre el todo. Cinco veces por el autor en un solo día, dos de ellas sobre **recomendaciones**, no
> sobre hechos. El registro deja de ser una lista de descuidos y pasa a ser una medición: bajo presión
> de producir conclusiones, **la tasa no baja aunque el defecto esté catalogado y a la vista**.

### 1.2 · Afirmaciones del REVISOR EXTERNO que resultaron falsas

Se registran con el mismo rasero. El revisor las catalogó él mismo como **un solo defecto con varios
síntomas**: *mirar una vista parcial y concluir sobre el todo*.

| id | qué se afirmó | qué resultó | descubridor |
|---|---|---|---|
| X-01 | «`adoptar_lock` y `_crear_recovery_directo` difieren en tres cadenas de texto y en nada más», presentado como **verificado en el código** | 25-35 líneas difieren, tres de ellas semántica de carga (precondición de liveness, relectura byte a byte, revalidación bajo el recovery). Las ventanas del `diff` se eligieron a mano y recortaban justo donde estaban las diferencias | AUTOR |
| X-02 | El eco llevaba semanas o meses roto | **9,4 días**. La cadena fue: documentación rancia → nadie ha mirado → el sistema está caído. Los dos primeros eslabones eran ciertos; el tercero no | medición |
| X-03 | «el archivo de Lighter casi con seguridad no se está replicando» | se replicaba desde julio, semanalmente, con verificación | AUTOR |
| X-04 | «el latido externo es media hora de trabajo» | existe, funciona, y disparó los dos avisos por el canal de alertas | AUTOR |
| X-05 | «14 días del archivo de Lighter sin copia externa acreditada» | el `ERROR` del log es de la **pasada de verificación**, no de la presencia; la comparación de tamaños sale limpia (933/933) | AUTOR |
| X-06 | El fallo del 22-ago es la verificación comiéndose el fichero de la hora en curso | el script **sí** excluye la hora en curso; el mecanismo real es que `EXC` se calcula una vez y **caduca durante la propia ejecución**, más los `market_map_*.json`, que no están excluidos | AUTOR |

| X-07 | «14 días del archivo de Lighter sin copia externa acreditada» | inflado. La tabla del propio revisor decía correctamente «presente pero SIN verificar»; **la prosa tres párrafos después lo convirtió en «sin copia acreditada»**. El dato estaba bien y el resumen lo infló | AUTOR |

> **X-07 es de otra clase que X-01..X-06 y conviene no fundirlos.** Los seis primeros son *vista
> parcial → conclusión sobre el todo*: el arreglo es mirar más. X-07 es *el resumen no arrastra las
> salvedades de la tabla*: el dato era correcto y la prosa lo degradó al comprimirlo. El arreglo es
> distinto —que el resumen herede las cualificaciones de la evidencia— y por eso se registra aparte.
> Es, además, el modo de fallo más peligroso para un documento destinado a publicarse: la tabla la
> lee un revisor; el resumen lo lee todo el mundo.
| X-08 | Re-correr los 7 checks sobre la copia restaurada «convierte los 496 PASS en **verificación independiente**» | sobrepasado, y se corrigió **él mismo antes de que nadie se lo dijera**: usa el mismo código que emitió el veredicto original. Prueba (a) que los bytes sobrevivieron el viaje y (b) que el veredicto es determinista. **No** prueba que los checks estén bien implementados — eso exigiría una segunda implementación | (el propio revisor) |
| X-09 | «H1 es infraestructura de ~20 módulos» — nunca llegó a escribirse | falsa: un `grep "h1"` **por subcadena** contaba módulos que solo contienen esas letras; son **cinco**. La cazó su autor al remedir, antes de publicarla | (el propio revisor) |

> **X-09 se registra aunque no llegara a publicarse**, y su autor pidió expresamente que constara. Por
> la **regla 1** lo que cuenta es que la afirmación era falsa, no que no saliera; por la **regla 3**,
> «lo encontró al remedir» es una categoría del registro, no una exención. Es, además, el noveno caso
> del mismo defecto en la misma persona: *vista parcial → conclusión sobre el todo*.

### 1.3 · Defectos del SISTEMA encontrados (no del método)

| id | defecto | gravedad | descubridor |
|---|---|---|---|
| D-01 | Frontera prefijo/corrupción mal trazada: 86 % de los prefijos de crash a STOP permanente | P0 | CI |
| D-02 | `ErrorMainSinAutenticar` incumplido en 3 de 6 sitios → sistema sin ninguna barrera | P0 | REV-ADV |
| D-03 | Los tres instaladores del gate no censan reclamos → mutex global permanente | P0 (abierto) | REV-ADV |
| D-04 | Corte a mitad de carácter UTF-8 declarado corrupción | P1 | REV-ADV |
| D-05 | Cierre P0-5 aplicado en **1 de 3** call-sites, y en el único donde era redundante | P1 (abierto) | REV-ADV |
| D-06 | 5 guardias con mutante que rompe el módulo: medían **cero** | — | ARNÉS |
| D-07 | 16 `causa` muertas + 41 laxas de 106: el 54 % no discrimina | — | REV-EXT → medición |
| D-08 | `CENSO-4` ciego a `match=` pasado por variable | P1 (abierto) | REV-ADV |
| D-09 | Hueco de 9,4 días en el eco (13-ago 08:57 → 22-ago 20:15), por **impago** | — | inspección del VPS |
| D-10 | `2026-08-13` fuera de **todos** los mecanismos: sin consolidar, sin auditar, sin respaldar | — | inspección del VPS |
| D-11 | el servicio de réplica: la verificación falla y seguirá fallando (coste O(archivo entero), creciente) | — | inspección del VPS |
| D-12 | `EXC` se calcula una vez y caduca durante una ejecución de horas; `market_map_*` sin excluir | — | lectura del script |
| D-13 | Los `testigos` que la réplica verifica cada semana llevan **congelados desde el 5-jul**: la mitad que siempre pasa es la que no cambia | — | inspección del VPS |
| D-14 | **La auditoría no puede detectar un día parcial.** `C6` mide `max_gap` **entre eventos consecutivos**; un día que se corta no tiene hueco posterior, así que pasa limpio. Y `audit.json` no guarda primer/último timestamp ni cobertura | — | lectura de `ingestion/audit.py` |
| D-15 | **Ya hay un día parcial acreditado dentro del dataset**: `2026-06-12` cubre 18:03→23:59 (24 % de los eventos de un día normal) y está `PASS`, consolidado y respaldado, **indistinguible** de uno completo salvo comparando `n_events` a ojo | — | ídem |
| D-16 | `compact_day` borra los parts con `os.remove(p)` **por ruta**, tras leerlos y escribir cientos de MB en medio: destruye *lo que haya en ese nombre*, no lo que absorbió. Es el defecto **K/L/F** del libro transaccional, vivo en el colector — donde está el dato irreemplazable | — | lectura dirigida |
| D-17 | **El prereg del eco sigue en BORRADOR.** Su propia cabecera dice «a congelar con MESA FRESCA antes de que el eco tenga masa»; el eco tiene ya **61 días**. La ventana para congelarlo antes de la masa ya pasó | — | lectura del prereg |
| D-19 | **El eco corre sobre Lighter, no sobre Binance.** Los 61 días auditados son el capítulo 1 (cerrado, negativo). El archivo relevante es el de Lighter: 939 ficheros horarios desde 2026-07-05, **sin auditoría diaria de ningún tipo** — cero `audit.json`, cero checks. El activo del que depende la apelación tiene **cero auditorías**; el capítulo cerrado tiene 496 | — | REV-EXT (como pregunta) + verificación |
| D-21 | **El colector graba WTI, XPT y BRENTOIL a 50 ms desde el 5-jul** — símbolo correcto, resolución correcta, **capa de dato equivocada** (L2 agregado, no L3). El prereg declara ese 2º símbolo no-token a 50 ms «lo ÚNICO» que responde A2, y el blocker del día siguiente estableció que esa ruta exige L3 | **abierto** | lectura del prereg + `SYMBOLS` |
| D-22 | **Los dos vendors de la réplica LIT tienen huecos de archivo documentados**: el canal de libro del primer proveedor está «defectuoso y descartado» (`ESTADO:352`) y la ruta tick-L2 del segundo proveedor resultó tener agujeros de días (`LEDGER:1799-1808`, diligencia 2026-07-06). «El agujero es del archivo, no del mercado» | — | lectura del LEDGER |
| D-20 | **El colector lleva 7 semanas grabando dato cuya suficiencia está declarada abierta.** `ECO_CONTEO_FASE0.md` (commit 2026-07-15) establece que la cohorte lenta exige order-level **L3**; que el WS da **L2 agregado** sin id de orden; y que la única vía prospectiva es instrumentar `orderBookOrders`. Deja **tres opciones abiertas «para decisión de la mesa»**. Verificado hoy: el colector **nunca se instrumentó** (`collector.py` sin tocar desde **Jul 6 11:24**, nueve días ANTES del blocker; `grep` de toda la máquina por `orderBookOrders` → vacío; y un frame real del 12-ago da `asks[0] = {'price','size'}`, sin `order_index`). Y **no hay registro de que la decisión se tomara**: `LEDGER.md` y `ESTADO.md` se detienen el **2026-07-06** | **abierto** | lectura dirigida por la pregunta del revisor |

> **Lo que D-20 NO afirma**, y conviene que conste con la misma fuerza: no dice que el dato sea
> inútil. La opción **A** (redefinir la cohorte) podría hacer suficientes el L2 y la dimensión wallet
> del canal `trade`. Puede que la decisión se tomara y no se registrara. Lo establecido es que **la
> pregunta se levantó, se dejaron tres opciones abiertas, y no consta que se cerrara** — mientras el
> colector seguía grabando con la configuración anterior al blocker.

| D-18 | **Ningún prereg define qué días entran** en la ventana de análisis (5 de 6 con cero coincidencias). Hueco de spec sobre el insumo, no sobre el método | — | ídem |

### 1.4 · Correcciones estructurales (no parches)

Se registran solo las que atacan **la clase**, no el caso.

| id | qué | por qué es estructural |
|---|---|---|
| C-01 | `tools/medida.py` | El número deja de escribirlo quien informa. Lleva el **sha dentro**; una cifra rancia pasa de improbable a imposible de presentar sin que se vea. Su primera víctima fue su autor |
| C-02 | `tools/comprobador_destrucciones.py` | Pone **precio** al criterio de parada antes de firmarlo, e **imprime sus propias reglas** para que se congelen con la salida: un recuento de un clasificador retocable es tan infalsable como un cero |
| C-03 | `_MATCH_LAXO_CONGELADO` (previo) | Trinquete de dos direcciones: falla si aparece un `match` laxo nuevo **y** si uno congelado se cura y no se retira. Caducidad automática |
| C-04 | Criterio de mutación por **ausencia** | La `causa` debe DESAPARECER al mutar. Antes bastaba con que apareciera, lo que un eco satisface sin demostrar nada |
| C-05 | Enumerar en vez de muestrear | Un test que muestrea un punto de un espacio que el código trata uniformemente **no acredita cobertura** |
| C-06 | Medir contra **todos** los ficheros que importan producción | No contra el que se está editando (origen de E-09) |
| C-07 | Reejecutar aislado todo fallo nuevo del arnés | Una pasada larga puede inventarse fallos en su cola por agotamiento de recursos del SO |

| C-08 | **Poller L3 aislado** (servicio propio, 2026-08-23) | Ataca la clase, no el caso: en vez de **modificar** el colector que lleva 7 semanas sin fallar, se añade un proceso con usuario, unit y directorio propios. Guardia de disco al **70 %** —el colector muere al 85— para que el aislado no pueda ser NUNCA la causa de esa muerte. `Restart=on-failure` y no `always`, porque la guardia sale con código 0 **a propósito** y un reinicio en bucle se comería el aviso. `ProtectSystem=strict` + `ReadWritePaths`: no puede escribir fuera de su árbol aunque el código tenga un bug |
| C-09 | **Medir antes de construir** (la sonda L3 previa al poller) | La sonda contestó lo único que decidía —`order_index` sobrevive 99-100 % a 5 s, luego la cohorte ES definible— y de paso destapó que el esquema del REST en vivo **no coincide** con el que consume `pilot_observer` (`remaining_base_amount` vs `remaining_size`; el lado implícito en `asks`/`bids`). Sin esa hora de lectura, el poller habría parseado al capturar y habría guardado un formato que no encaja: **capturar lo que no toca es peor que no capturar**, porque crea la ilusión de tener el dato. Es exactamente lo que le pasó al colector durante 7 semanas |

| C-10 | **Arnés de mutación del gate** (`tools/mutacion_gate_b.py`, 2026-08-25) | Los veinte tests de los tres P0 se acreditan **por ausencia**: se rompe cada guardia y el test TIENE que ponerse rojo. Distingue «ANCLA NO ÚNICA» de «VERDE — TEST VACUO» a propósito: un ancla rancia porque el código se movió y un test que no muerde son problemas distintos. **Ver E-31: su 10/10 fue cierto y dio confianza falsa** |
| C-11 | **`tools/feasibility_objetivo.py`** (2026-08-25) | Traduce el objetivo del proyecto (100-200 €/mes) a nocional, fills y cuota de volumen, con los insumos medidos y sus supuestos DECLARADOS. Debió ser la primera línea del programa: si el objetivo exigiera un edge 10× mayor que lo medible, se sabría en una tarde y no en seis meses |
| C-12 | **Atacar el propio arreglo antes de declararlo cerrado** (2026-08-25) | Cinco lentes adversariales contra tres commits que su autor ya había presentado como cerrados, con 100 tests verdes. Encontró 4 P0. La regla que queda: *un arreglo no está cerrado porque su autor lo diga y su suite pase* |

### 1.5 — las 24 h del 2026-08-24/25 (auditoría del método, revisión completa y los tres P0)

| id | qué pasó | clase | descubridor |
|---|---|---|---|
| E-26 | **Prefiltro de bytes silenciosamente vacío.** `if b'"trades"' not in linea` sobre un frame que viaja como cadena JSON **escapada** (los bytes llevan `\"trades\"`) no casa nunca. Devolvió una tabla limpia de **40 días con ceros** que parecía un hallazgo («sin actividad, sin cambio de régimen») | instrumento que devuelve algo plausible **sin medir nada** | AUTOR |
| E-27 | **Mapa de símbolos mal parseado y etiquetas puestas a mano.** `market_map_*.json` es `{"code":…,"order_books":[…]}`; `for k,v in d.items()` devolvía `{200:'code'}` y el `TypeError` de la lista se lo tragaba un `except Exception: pass`. Los nombres «LIT», «WTI», «XPT» de la tabla de masa **los escribió el autor al transcribir** | un `except` amplio convirtiendo un **fallo** en un **resultado** | AUTOR |
| E-28 | **Citar de memoria teniendo el `grep` propio delante.** Tres veces en 24 h y **por las dos partes**: «LIT ha caído 3-5×» (era 0,63× por mediana); «14× a 22× el suelo declarado» (compara una **mediana** de la base con una **media de medias diarias** del markout: no es un múltiplo válido, retirado); y dos atribuciones de cita a fichero equivocado | sustituir **el registro** por **el recuerdo** en un proyecto cuyo método entero es `fichero:línea` | REV-EXT |
| E-29 | **Guardias específicas de un brazo metidas en el helper COMPARTIDO.** El prefijo `LIT_` y la frontera 2026-06-30 mataron el brazo A2 en el acto: su ventana es fija y anterior (2026-03) | no comprobar quién más usa lo que tocas | SUITE |
| E-30 | **P0: frontera de seguridad construida sobre rutas RELATIVAS.** `BLOCKS` y `GATE_SELLADO` se resuelven contra el `cwd`, así que la compuerta de la ventana gastada es un **no-op en cualquier proceso que no arranque desde `qs/`** — y `_daymeans_replicacion` llega a abrir el npz gastado. Invalida los tres P0 que se habían declarado cerrados con 100 tests en verde | una constante relativa **no puede ser** una frontera de seguridad | REV-ADV |
| E-31 | **El arnés de mutación dio 10/10 y no probaba lo que parecía.** Acreditó que los tests se ponen rojos al borrar cada guardia — cierto. Pero **todos los tests corren con `cwd=qs`**, así que ninguno ejercita el modo de fallo de E-30. Un arnés de mutación acredita la **sensibilidad del test**, no la **corrección del código**; se presentó como lo segundo | confundir *el test detecta el cambio* con *el código es correcto* | REV-ADV |
| E-32 | **El propio arnés envenenó el estado de producción.** `mutacion_gate_b.py` corriendo pytest con `cwd=QS` dejó un `gate_read_lock.json` REAL con `hash_freeze` = 40 aes (la F falsa del fixture). El gate quedó en `GASTADA-PENDIENTE-DE-MESA` **sin haberse leído nada**. NO se ha borrado: es fail-closed y borrarlo sería el «reintento silencioso» que el propio diseño prohíbe — lo despeja la mesa | un instrumento de verificación que **muta lo que verifica** | REV-ADV |
| E-33 | **`print` afirmando `[nada inyectado]` en una función que sí admite inyección**: `chd` fija la mitad del listón del bar (7,0 vs 49,5 con la misma muestra y los mismos pins) | el código **afirmando** algo falso sobre sí mismo | REV-ADV |
| E-34 | **Copiar a medias el patrón del brazo ya blindado.** El brazo WTI deriva `blocks_dir` **absoluto** desde `repo_root` y tiene jaula `realpath` contra traversal; la versión LIT no tenía ninguna de las dos. Segundo caso del mismo patrón en 24 h (E-29 fue el primero) | entender la idea y no copiar **lo que parecía detalle** | REV-ADV |
| E-35 | **`.claude/` no figuraba en la tabla de cobertura de la revisión completa** — ni siquiera constaba como hueco. Dentro estaba el `quant-reviewer` congelado el 2026-06-13, con la regla que contestaba por adelantado la objeción viva más fuerte, **sin usar desde junio** | un documento que presume de declarar lo que no ha leído falla si el hueco **no llega a la lista** | PROPIETARIO |

### 1.6 — el 2026-08-26: cuatro historias sobre un número que estaba roto

| id | qué pasó | clase | descubridor |
|---|---|---|---|
| E-36 | **`realized_markouts` aceptaba referencias inválidas.** `pilot_observer.py:122` multiplicaba por `ref_px[best]` sin mirarlo; con `ref = 0` devuelve exactamente `−lado·10.000,00 bps`, que es **finito** y por tanto pasa el `isfinite` de toda la cadena y se promedia. **15.540 celdas** en el programa (1,3 % en DOGE); **una sola** mueve el titular 2,64 bps y el `n_eff` de 79,0 a 14,7 | un valor absurdo **que es finito** atraviesa un filtro escrito contra `NaN` | REV-ADV |
| E-37 | **Cuatro lecturas del +18,24 en una tarde, ninguna con su test hecho.** Crecimiento «9,73×» (denominador con t +0,18 — dividir por ruido — y además residuo de E-36); el simétrico a 5 s «coincidiendo» con el medio-spread; el medio-spread propio «con instrumento validado»; y el antisimétrico «identificado» como basis. Las cuatro retiradas el mismo día | convertir un número en una **historia** antes de calcularle su contraste | REV-ADV |
| E-38 | **Una «validación» que era una identidad algebraica.** `mediana \|px−mid\|/half = 1,000` equivale a «≥50 % de los prints en el toque»: **el mismo bit** que el 71-91 % reportado al lado, presentado como segunda confirmación independiente. Y se eligió la mediana, que satura en 1, en vez de la media, que sí informa de la cola | dos cifras que son **una sola**, contadas como dos | REV-ADV |
| E-39 | **Cifras medidas, hardcodeadas como literales en el arnés.** `1,22 / 1,36 / 1,30 / 71-91 %` estaban tecleadas en `tools/anatomia_del_18_24.py`; los scripts que las midieron vivían en un scratchpad del VPS sin versionar. Es el defecto que `tools/medida.py` existe para prohibir, **dos días después** de que `a6ae845` lo tumbara para otro número | el mismo vicio reincide cuando el arreglo fue **puntual** y no **estructural** | REV-EXT |
| E-40 | **Un detector de contaminación que no demostraba lo que decía.** `abs(mo) >= 9999.99` también captura `ref ≈ 2·px` y cualquier movimiento >100 %. La firma correcta es de **signo** (`mo == −lado·10.000 ⟺ ref == 0`). En estos datos coinciden —1.012 celdas, cero discrepancias— pero eso es un hecho **de los datos**, no una propiedad del detector | acertar el número con un instrumento que **no podía** acertarlo por construcción | REV-EXT |
| E-41 | **Atribuir a la casa un conocimiento que no tenía.** Se citó el `RuntimeWarning log(0)` de `trailing_vol` como prueba de que los ceros «ya estaban declarados». Falso: esa función recibe `tts/tpx`, que son trades de **Lighter** (`confirm_runner.py:81,149`), no la cinta de Binance donde estaban los ceros | usar un precedente **sin comprobar que hablaba de lo mismo** | REV-EXT |

### 1.7 — el 2026-08-27: la reparación tenía los mismos vicios que el defecto

| id | qué pasó | clase | descubridor |
|---|---|---|---|
| E-42 | **Un documento titulado `PREREG` escrito DESPUÉS de ver el resultado.** La cronología real fue: censo → **recálculo forense** (que dio la vuelta al veredicto a `NULA MUERTA`, el desenlace más favorable posible) → **y luego** se redactó el «pre-registro», afirmando en su primera línea que decidía reglas *«sin haber mirado qué le hacen a ningún resultado»*. Falso. Un pre-registro lo es respecto del **resultado**, no del teclado | escribir la regla **sabiendo hacia dónde se mueve el dato**, y llamarlo pre-registro | REV-EXT |
| E-43 | **El arreglo no cerraba el agujero que arreglaba.** El guardia v1 exigía `finito and > 0`, así que **un `ref` positivo diminuto (`1e-9`) seguía pasando** y producía la misma firma de −10.000 bps. El caso central sobrevivía a su propia reparación | validar el **tipo** del dato en vez de su **consecuencia** | REV-EXT |
| E-44 | **«El defecto vive en el carril Binance»** — dicho con 4 celdas contaminadas en capa 2 delante, en el propio censo del informe. Cuatro no es cero: `maker_sim.markouts` tenía el mismo agujero, otra función y otro carril | convertir una **diferencia de tasa** (1,3 % vs 0,002 %) en una **afirmación de exclusividad** | REV-EXT |
| E-45 | **Una especificación que prometía lo que el código descartaba.** R2 decía que los indicadores de sospecha «se emiten en el npz»; el código sólo tenía contadores efímeros. Y R4 se declaró como regla general viviendo en **un solo** llamador de cinco, contando **una** de las tres clases de rechazo | la regla escrita y la regla ejecutada **divergiendo desde el primer día** | REV-EXT |
| E-46 | **Un STOP sólo documental sobre una ruta productiva abierta.** Se declaró que el runner incumplía el pre-registro (usa trades donde se exige mid) y se dejó **ejecutable**: nada impedía escribir un artefacto `ok` no conforme | confundir **declarar** una prohibición con **implementarla** | REV-EXT |
| E-47 | **Arreglar el productor y dar por saneado lo producido.** Los npz históricos siguieron siendo consumibles aguas abajo: `confirm_screen` los leía y promediaba sus celdas de ±10.000 sin enterarse | el arreglo aguas arriba **no viaja** hacia atrás | REV-EXT |
| E-48 | **Un recibo que no ligaba ruta con bytes.** Hacía hash de la lista ORDENADA de SHA-256, así que **intercambiar dos hashes entre rutas dejaba el agregado idéntico**. Y cada fichero se leía dos veces —una para el hash y otra para el análisis—, de modo que en rigor el hash no acreditaba los bytes analizados | un artefacto de reproducibilidad que **no reproduce la asociación** que dice acreditar | REV-EXT |

| E-49 | **La regla del guardia estaba escrita DOS VECES y ninguna copia sostenía nada.** `realized_markouts` combinaba una máscara vectorizada con una comprobación de banda **en el punto de llamada**, duplicando lo que `ref_valida.clasificar` ya hacía. Desactivar cualquiera de las dos **no abría el agujero**, porque la otra lo tapaba: dos guardias, cero acreditadas. Es el mismo vicio que el módulo compartido existía para eliminar, cometido dentro del propio módulo | duplicar la regla **mientras se escribe el fichero que existe para no duplicarla** | **ARNÉS** |
| E-50 | **El arnés de mutación era ciego a los tests parametrizados, y llevaba así desde siempre.** `_FALLO` capturaba el nodo con `(\w+)`, que para en `[`; con el `$` detrás, un `FAILED …::test_x[nan-no_finita] - AssertionError` **no casaba en absoluto**, y `_juzgar` además contaba esos fallos como COLATERAL. Resultado: **6 de 8 mutaciones que sí rompían tests se declaraban inocuas**. El arnés del gate nunca tuvo filas parametrizadas, así que el defecto vivió invisible en el instrumento que acredita a los demás. Un primer parche (`(?:\[[^\]]*\])?`) seguía fallando con ids de corchetes **anidados** (`test_x[51-1000-[R4]]`) | el instrumento de verificación **con un defecto que sólo se ve al usarlo para algo nuevo** | **ARNÉS** |

| E-51 | **La banda de validez toleraba markouts diez veces más absurdos por arriba que por abajo.** Se fijó a mano en `[0,1 ; 10]` afirmando que fuera de ella `\|markout\| ≥ 9.000 bps`; **falso por arriba**: como `mo = (ref/px − 1)·1e4`, el borde 10 da **+90.000**. Un `ref = 45,68` con `px = 6,13` se clasificaba «ok» produciendo **+64.500 bps**. Y el primer arreglo —derivar `1,0 ∓ 0,9`— tampoco era simétrico: `1.0 - 0.9 = 0.09999999999999998` en float64 mientras `1.0 + 0.9` es exacto, así que un borde quedaba dentro y el otro fuera | escribir una regla en una unidad (ratio) y **justificarla en otra** (bps), sin comprobar la traducción | **PROPIEDADES** |

| E-52 | **El guardia documental puso rojo el build por el documento que lo describía.** Su regex localizaba el marcador `IDS-IMPLEMENTADOS` en cualquier `.md` y no comprobaba que lo declarado **tuviera forma de id de regla**: en el informe a la mesa, escrito como ejemplo en prosa, el `…` se tomó por un identificador. Un guardia que falla al documentarse es un guardia que alguien desactiva en una semana — y entonces no guarda nada | no distinguir el USO de un marcador de su **MENCIÓN** | **TRINQUETE** |

**La lección de este día:** las siete primeras entradas son de la **reparación**, no del defecto. Un arreglo
escrito con prisa hereda los vicios del fallo que arregla — y aquí los heredó casi uno a uno:
sobre-afirmar el alcance (E-44), prometer sin implementar (E-45, E-46), y validar la forma en vez de
la consecuencia (E-43). El descubridor de las siete es el mismo: **una reauditoría externa del commit
ya escrito**, no la suite ni el CI, que estaban verdes.

**La lección de método del día anterior, y es la que más generaliza:** el arnés `anatomia_del_18_24.py`
tenía una puerta que abortaba si no reproducía el titular EXACTO. **La pasó** — porque el titular se
había calculado *con* el fill corrupto dentro. Una puerta de reproducción acredita **fidelidad al
número publicado**, jamás su corrección: por diseño no puede cazar un defecto que ya estuviera dentro
del original. Lo cazó un refutador con el encargo explícito de **tumbar**, no de comprobar. Verificar
y refutar no son el mismo acto, y sólo el segundo encuentra esto.


### 1.8 — el 2026-08-27 (tarde): la reparación de la reparación

| id | qué pasó | clase | descubridor |
|---|---|---|---|
| E-53 | **La compuerta del carril cubría UN productor de TRES.** Se declaró cerrada la ruta «producir artefactos con el carril equivocado» habiéndola cerrado sólo en `confirm_runner`. `pilot_runner` y —peor— `eco_runner_lit`, que es el **productor prospectivo oficial**, seguían pudiendo escribir npz no conformes | declarar cerrada una ruta **habiendo tapado una de sus salidas** | REV-EXT |
| E-54 | **El orden de escritura hacía inútil la marca.** El npz se escribía ANTES del lateral, y `main` omite los npz que ya existen: un crash entre medias dejaba un artefacto **sin marca que nadie volvería a marcar**, y por tanto indistinguible de uno limpio. La no-conformidad vivía sólo en un JSON que ningún consumidor exigía | proteger con un artefacto que **se escribe después** de aquello que protege | REV-EXT |
| E-55 | **Un consumidor cerrado de tres.** `confirm_screen` rechazaba lo contaminado; `pilot_screen` y `maker_capa2_screen` seguían leyendo los npz antiguos sin mirar | el mismo patrón que E-53, en el otro extremo de la tubería | REV-EXT |
| E-56 | **`maker_sim` atribuía a la REFERENCIA un fallo del PRECIO DEL FILL** (`px` inválido → `ref_*`), y carecía del cuadre vivo que sí tenía el otro brazo. El diagnóstico del incidente se apoya en esos contadores | reintroducir en el diagnóstico **la confusión de causas** que R3 existe para impedir | REV-EXT |
| E-57 | **Falso verde ESTRUCTURAL en el guardia documental.** Comprobaba la cronología mirando el árbol de trabajo, así que pasaba *precisamente porque* los artefactos que el prerregistro debe preceder aún no existían — y habría fallado para siempre el día que existieran legítimamente. Y su spec-vs-código buscaba el identificador **como texto**: un comentario la satisfacía | un guardia que **se vuelve rojo al cumplirse lo que vigila** | REV-EXT |
| E-58 | **La prueba del umbral no estaba en la herramienta que decía acreditarla.** Se afirmó «no-op demostrable: 0 celdas entre 3.000 y 9.000» con un número salido de un **script de sesión sin versionar**; el censo versionado ni siquiera medía en 9.000 —medía en 9.999,99— y las bandas no entraban en las filas que forman `sha256_censo`. **Es E-39 otra vez, cometido dentro de la herramienta escrita para impedirlo** | citar como acreditado lo que **el artefacto no acredita** | REV-EXT |
| E-61 | **Un test verde por un camino que no era el declarado.** El test del ORDEN de publicación parcheaba `os.replace` sobre el módulo global, así que el doble se llamaba a sí mismo; con el código correcto nunca se llegaba a esa rama, pero si el orden se hubiera invertido de verdad el test habría muerto con `RecursionError` en lugar de con su aserción —**señalando una causa falsa justo cuando importa**. Lo destapó el arnés de mutación, no la suite | test que pasa por **una razón distinta de la que dice** | ARNÉS |
| E-62 | **Una comprobación acreditada por otra.** El test de sustitución de bytes cambiaba también el TAMAÑO, así que lo atrapaba la comprobación de tamaño: el SHA-256 no estaba acreditado por sí solo y su mutación mordía declarando una causa ajena. Corregido con una sustitución de **idéntico tamaño**, donde la única defensa en pie es el hash | defensa en profundidad que **enmascara** la ausencia de una de sus capas | ARNÉS |
| E-63 | **Una guardia que falla ABIERTO.** La cronología descartaba la relación MALA (`el artefacto es ancestro del prerregistro`) en vez de exigir la BUENA. Con dos commits **hermanos** en ramas divergentes ninguno es ancestro del otro, así que caía en el `else` y la guardia daba el caso por bueno: **la precedencia no estaba establecida y se afirmaba igual** | comprobar descartando lo malo en vez de **exigir lo bueno** | REV-EXT |
| E-64 | **Atarse al NOMBRE del documento en vez de a su TEXTO.** El recibo citaba el commit que introdujo el prerregistro. `PREREG_SONDA_COBERTURA.md` nació en `546148e` y sus reglas vigentes se escribieron en `807d0fe`: el recibo habría certificado un texto que ya no rige, y un artefacto aparecido entre ambos pasaba la cronología siendo anterior a las reglas que decían pre-registrarlo | identificar un objeto congelado por su **etiqueta** y no por su **contenido** | REV-EXT |
| E-65 | **Una guardia roja mientras se hace trabajo legítimo** (evitado, no cometido). Exigir que el texto del prerregistro estuviese commiteado ponía roja la guardia durante cualquier edición — el antipatrón que su propia cabecera describe y que la desactivaría en una semana. El bloqueo pertenece a `--exigir`, justo antes de gastar, no al chequeo general | poner rojo el build por **hacer el trabajo**, que es como muere un control | AUTOR |
| E-66 | **El artefacto aportaba la premisa con la que se le juzgaba.** `cargar()` recalculaba la conformidad —correcto— pero contra la **capa que el propio manifiesto se atribuía**. Un bloque legítimo de capa 2 trasplantado al directorio decisivo de confirmación entraba sin una queja; y ni siquiera hacía falta trasplantarlo, porque el SHA cubría el npz pero no el JSON: **cambiar una palabra** volvía aceptable lo inaceptable. Es el `extra`-que-se-sobrescribe-`conforme` un nivel más arriba | verificar contra un criterio que **aporta el verificado**: no es verificación, es tautología | REV-EXT |
| E-67 | **Un control que ninguna mutación podía matar** (retirado, no enviado). Añadí un `sha256_manifiesto` sobre los campos normativos; su mutación en el arnés no mataba ningún test porque **los siete campos ya se validaban uno a uno**. Dos mecanismos donde quitar cualquiera no abre nada es E-49, y un control que no es load-bearing da una seguridad que no da. Se sustituyó por un test que fija la propiedad real: cada campo normativo tiene su propio rechazo | añadir una capa que **parece** defensa y no puede fallar sola | ARNÉS |
| E-68 | **El mismo commit se daba por precedente.** `_es_ancestro` devolvía `True` para `a == b`; lo escribí razonando «el mismo commit no es posterior, luego vale», y es al revés: escribir el prerregistro y el resultado **a la vez** es justo lo que haría quien redacta el prerregistro con el resultado delante | confundir «no es posterior» con «es anterior» | REV-EXT |
| E-69 | **Un worktree sucio presentado como normativa congelada.** El sello hasheaba el ÁRBOL DE TRABAJO y buscaba en la historia un commit que coincidiera: revertir el documento a una versión pasada **sin commitear** devolvía `commiteado: True` apuntando a esa versión mientras `HEAD` tenía otra | sellar **lo que se lee en disco** en vez de lo que la historia contiene | REV-EXT |
| E-70 | **«La última línea de `git log` es la más antigua» es falso en un DAG.** `git log` ordena por FECHA de commit, no topológicamente; con fechas sesgadas —o dos máquinas con relojes distintos, que es lo normal— la línea leída no es ancestro de nada. Y con un comodín se inspeccionaba **una sola adición** de las varias que casan. Los dos juntos producían el falso verde | apoyarse en un orden que la herramienta **no garantiza** | REV-EXT |
| E-71 | **Una variable LOCAL acreditaba una regla.** `ast.walk` recorre también los cuerpos de función, así que `regla_uno = 1` dentro de cualquier otra función satisfacía `mod.py:regla_uno`. Mi propio docstring decía «sigue sin probar que la regla sea correcta»; no vi que ni siquiera probaba que fuera **algo invocable** | recorrer el árbol ENTERO cuando la propiedad es del **nivel superior** | REV-EXT |
| E-72 | **Un arreglo que rompía un caso bueno sin cerrar el malo** (detectado por la propia guardia al primer intento). Exigir que toda regla fuese una FUNCIÓN puso roja la guardia sobre `R2`, que es un umbral y se implementa legítimamente como constante. El agujero eran las variables **locales**, no las constantes de módulo: la distinción correcta es el nivel, y la clase se declara con `!constante` | endurecer por la dimensión **equivocada** — más estricto no es más correcto | AUTOR |
| E-73 | **Un escape de emergencia convertido en puerta principal.** `exigido_para('LIT','eco')` es `mid_binance` y `eco_runner_lit` pasa `trade_mas_cercano_binance` FIJO: su conformidad era **estructuralmente imposible**, así que `QS_CARRIL_NO_CONFORME=1` no era una excepción sino su ÚNICA vía de escritura, encendida de forma permanente. Y su promesa —«queda marcado NO conforme y los consumidores lo rechazarán»— era falsa: salía por `np.savez`, ningún campo llevaba el carril y el gate no recalculaba nada | escribir una regla que **su propio productor no puede cumplir**, y una salida que promete una marca inexistente | REV-EXT |
| E-74 | **El productor sellaba trece campos y el gate comprobaba otros**, y ninguna de las dos listas incluía el CARRIL: un bloque medido contra otra referencia pasaba el gate con el hash perfecto. Dos listas que se parecen pero no son la misma es E-49 con otro disfraz — quitar una comprobación de un lado no abre nada visible | validar en dos sitios con **dos listas** en vez de una compartida | REV-EXT |
| E-75 | **Una exención FANTASMA inventada por una coincidencia de texto.** El censo buscaba `np.load` como subcadena, así que `cryptohft_adapter.py` figuraba EXIMIDO sin tener una sola llamada. Cubría algo inexistente y habría cubierto en silencio a la que apareciera mañana | eximir por **texto** en vez de por llamada, y por fichero en vez de por callsite | AUTOR |
| E-76 | **El arnés aprobaba una fila que declaraba un test INEXISTENTE.** Renombré un test, dejé la fila apuntando al nombre viejo, y como ese test no podía fallar la fila aprobaba siempre. Es el objeto que el arnés existe para detectar, un nivel más arriba: ahora comprueba contra la colección de pytest que los tests declarados existen | un control que **aprueba lo que no ejecuta** | ARNÉS |
| E-77 | **Un test que pasaba con la comprobación rota.** El test del glob recursivo sólo ponía un fichero ANIDADO, y con `recursive=False` el patrón `**` degenera en `*`: encuentra el anidado y pierde el de nivel superior — al revés de lo que asumí. El arnés lo declaró VACUO | comprobar la recursión **en la dirección equivocada** | ARNÉS |
| E-78 | **Commiteé un cambio de contrato midiendo sólo los tests focales.** `406d66a` subía el esquema del eco y hacía `carril_usado` obligatorio; los siete ficheros focales daban 209 verdes y la suite completa tenía **39 regresiones** en `test_eco_gate_b`/`test_eco_runner_lit` (43 fallos frente a los 4 preexistentes por `pandas` ausente). Un cambio de contrato se mide contra TODO lo que consume el contrato, no contra lo que escribí ese día | confundir «mis tests pasan» con «no he roto nada» tras cambiar un **contrato compartido** | AUTOR |
| E-79 | **Un aflojamiento SILENCIOSO al unificar.** Al escribir el validador único del eco dejé caer `sha_trades` y `sha_snaps` de los campos exigidos: el gate llevaba tiempo comprobándolos y mi «unificación» los perdió sin que nadie lo pidiera. Es la peor clase de cambio — nadie lo nota y el gate acepta lo que antes rechazaba. Lo destapó reparar la regresión, no los focales | al unificar dos listas, quedarse con la **intersección** en vez de la unión | AUTOR |
| E-80 | **Edité el árbol mientras una medición corría** (segunda vez en la serie). Lancé la suite completa y, mientras corría, escribí el registro de la sonda: su `exit 0` no medía el árbol de ningún commit. La segunda corrida murió por `timeout` a los 25 minutos. Dos intentos, cero mediciones válidas | tratar una corrida larga como algo que sigue siendo válido si el árbol cambia debajo | AUTOR |
| E-81 | **El oráculo de identidad-byte de M-10 llevaba roto desde `807d0fe`** y nadie podía verlo: su fichero no se ejecutaba en local por falta de `pyarrow` y no ha habido CI desde entonces. La rama habría fallado el CI en cuanto se empujara. La garantía en sí estaba intacta —arrays y bytes del npz idénticos—; lo que había cambiado era la cadena de estado, que ganó su etiqueta de conformidad. **Se encontró instalando las dependencias que faltaban y corriendo la suite ENTERA** | un control que existe, es el más importante, y **no puede informar** porque su entorno no lo deja correr | AUTOR |
| E-82 | **Diez ficheros de test llevaban meses sin ejecutarse en esta máquina y se había normalizado.** «`pyarrow` ausente ⇒ la suite completa solo la acredita el CI» era cierto y se convirtió en excusa: `pip install --only-binary :all:` con las versiones DEL LOCK bastó para levantarla entera (1.400 tests, 40 min). Al primer intento apareció E-81 | aceptar una limitación del entorno **sin volver a comprobar si sigue siendo real** | AUTOR |
| E-83 | **«Un único validador» que solo cableé para una de las dos familias.** P0-3 pedía un validador estricto compartido entre productor y gate; lo hice para WTI y dejé el consumidor de LIT (`_revalidar_bloque`) repitiendo las seis comprobaciones a mano y **sin mirar el carril**. Lo destapó mi propia revisión al notar que `EP.EXTRA_LIT` estaba definida y **no la usaba nadie**: una constante decorativa es el síntoma de una abstracción a medio cablear | declarar «unificado» tras cablear **el primer caso** | AUTOR |
| E-84 | **Una fixture mal construida que habría hecho pasar el test por otra razón.** Al escribir el test del carril de LIT puse `descartes` con forma `(0,2)` cuando son contadores por horizonte, `(2,)`. Sin mutar, el test pasaba porque el carril saltaba primero; con la mutación puesta se vio que lo rechazaba la coherencia interna. El arnés no sólo acredita el código: acredita también **las fixtures** | construir el caso de prueba **de memoria** en vez de contra el esquema | ARNÉS |
| E-85 | **Atribuir una causa antes de medirla — TRES veces en el mismo día.** (1) Culpé a la memoria de unos fallos sin mirar la memoria; (2) di por buena la causa que decía un mensaje de error; (3) dije «es cosa mía, no del código» ante un agotamiento de recursos, y al medir resultó que `OneDrive.exe` retenía **102 GB de 128 GB de commit** mientras había **un solo** proceso Python vivo. Las tres veces la explicación ENCAJABA. Encajar no es medir | ofrecer la hipótesis que encaja como si fuera el diagnóstico | AUTOR |
| E-59 | **Un umbral perezoso presentado como proporción.** C3 fijaba «≥ 60 símbolo-días» para los dos símbolos sin mirar que el decisivo real es **LIT 79 y DOGE 70**: exigir 60 a DOGE es el **85,7 %**, no el 75 % que el propio documento decía pretender | escribir un número redondo y **llamarlo una regla** | REV-EXT |

**La lección, y es incómoda:** las siete son de la reparación de la reparación. El patrón que se repite
—E-53, E-55— es **cerrar una salida y declarar cerrada la ruta**; y E-58 es reincidencia directa de
E-39 **dentro del fichero escrito para impedir E-39**. Un arreglo hecho con prisa no hereda sólo los
vicios del defecto: hereda los del arreglo anterior.

**La lección transversal de estas 24 h, y es la que generaliza fuera de este proyecto:** en `.claude/`
conviven las dos clases de control. El **hook** cableado en `settings.json` llevaba **dos meses**
corriendo pytest solo. Los **agentes y comandos**, que hay que invocar, se dejaron de invocar en
junio; las bitácoras paran en dos. Misma carpeta, misma calidad, mismo autor. **Lo enchufado
sobrevivió; lo que había que recordar, no.** Al diseñar un control la pregunta no es «¿es bueno?»
sino **«¿qué lo dispara sin que nadie se acuerde?»**; y al auditar, hay que buscar primero **los
controles que ya existen y no se están usando**.

---

## 2. EL RECUENTO — que es el único resultado de este documento

<!-- RECUENTO:INICIO — generado por tools/recuento_auditoria.py, NO editar a mano -->

De **93 afirmaciones falsas** registradas (**84** del autor, **9** del revisor externo):

| descubridor | nº |
|---|---|
| REV-EXT | 35 |
| AUTOR | 25 |
| REV-ADV | 12 |
| ARNÉS | 9 |
| CI | 2 |
| el propio revisor | 2 |
| PROPIEDADES | 1 |
| PROPIETARIO | 1 |
| PROVEEDOR | 1 |
| SONDA | 1 |
| SUITE | 1 |
| TRINQUETE | 1 |
| el propio error | 1 |
| medición | 1 |
| **TOTAL** | **93** |

> *Este bloque lo genera `tools/recuento_auditoria.py` desde **todas** las tablas del*
> *registro (§1.1, §1.2, §1.5 y las que se añadan). Rechaza publicar si hay un id duplicado.*
> *Llegó a decir tres cifras distintas a la vez cuando se mantenía a mano; lo cazó un*
> *revisor externo contando las filas. Si el total de la tabla no cuadra con la suma de*
> *las filas, el fallo está en el generador o en el formato de una fila — no en el número.*

<!-- RECUENTO:FIN -->

**El resultado, dicho sin adornos: ninguna de estas afirmaciones falsas fue detectada por el juicio de
su autor en el momento de emitirla.** Todas las detectó un instrumento, un interlocutor, o el propio
autor **al volver a medir**. Y el defecto que más se repite, en las dos partes, es el mismo: **mirar
una vista parcial y concluir sobre el todo**.

> **Lectura honesta de este recuento.** No dice «el autor es descuidado». Dice algo más útil y menos
> cómodo: **el juicio de primera pasada no es un instrumento de verificación**, ni siquiera bajo un
> protocolo explícito de rigor y con el autor esforzándose en aplicarlo. Lo que funciona es medir, y
> que otro mire.
>
> **Y este mismo §2 es la prueba.** Se mantuvo a mano y llegó a decir **tres cifras distintas a la
> vez** —33 en la cabecera, 26 en la conclusión, 22 en la tabla—. Lo cazó un revisor externo contando
> las filas. El bloque de arriba lo genera ahora `tools/recuento_auditoria.py` desde las tablas: es la
> doctrina de `medida.py` aplicada al documento que la enuncia.

---

## 3. EL HALLAZGO QUE NO ESTABA EN NINGÚN PLAN

Doce sesiones endureciendo el libro transaccional contra colisiones entre escritores, sustituciones
de bytes en ventana y colisiones cross-host. Durante ese tiempo el colector de datos funcionó solo,
sin vigilancia, dos meses, con **496 auditorías diarias y cero fallos**.

**Lo único que detuvo la producción de datos fue una factura de 
hosting sin pagar.**

El modelo de amenaza apuntaba a un activo (la integridad del registro) que estaba bien protegido, y
no a otro (la **disponibilidad** del insumo) que dependía de un pago y de que alguien se acordara de
mirar. Ninguna cantidad de rigor en el libro habría cambiado eso.

Corolario, que es lo que hay que llevarse: **el rigor no se distribuye solo.** Se concentra donde el
trabajo es interesante, y el trabajo interesante casi nunca coincide con el punto donde el sistema
se rompe de verdad.

---

## 4. LIMITACIONES DE ESTE PROPIO REGISTRO

Sin esta sección, el documento sería un ejemplo de lo que denuncia.

1. **La muestra no es aleatoria ni completa.** Recoge lo encontrado en el periodo en que se llevó
   registro. Los errores que nadie encontró no están aquí, **por construcción**, y son los que más
   interesarían.
2. **El recuento del §2 lo hace una de las partes.** Es el mismo defecto estructural que `medida.py`
   corrige para los tests: el número lo escribe quien informa. Un tercero debería recontarlo.
3. **La clasificación de descubridor tiene juicio dentro.** «El autor lo encontró al remedir» y «se lo
   señaló un instrumento» a veces se solapan.
4. **No hay grupo de control.** No se puede afirmar que este método encuentre más defectos que otro:
   no se ha desarrollado el mismo sistema dos veces.
5. **La gravedad de los defectos no está normalizada.** «P0» significa lo que el proyecto decidió que
   significa.
6. **Llevar este registro no acredita la calidad del sistema.** Se puede llevar un registro impecable
   de un trabajo malo. Lo que acredita —si acredita algo— es que las afirmaciones de este proyecto se
   pueden auditar, no que sean correctas.
