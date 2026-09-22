# EL ARCO COMPLETO — quant-system, jun-2026 → jul-2026 (listo, NO publicado)

Este es el relato entero del programa, con los hashes de git como columna vertebral: cada afirmación de
fecha es verificable contra la historia del repo privado (ver MANIFEST). Presupuesto total gastado en
datos y cómputo externo: **$0** (+ ~1.300 créditos de un tier gratuito de 50.000). Se escribe en el
estado exacto en que está: con una observación positiva viva, su apelación pendiente, y sin una sola
afirmación de rentabilidad.

## Cap 0 — La infraestructura y el contrato (jun-2026)

Sonda propia de captura L2 sobre 8 perps finos de Binance (VPS, `ingest.service`, esquema de doble reloj
event/recv, respaldo offsite por checksum). El contrato metodológico que gobierna todo lo demás:
**pre-registro commiteado ANTES del dato (hash = autoridad de fecha), held-out que se gasta al mirarlo,
fortalecer pre-dato sí / aflojar jamás, SCREEN no veredicto, y cada fallo catalogado.** Protocolo de tres
partes: Code (ejecutor, dueño del repo), la mesa (revisión hostil externa), el propietario (firma).

## Cap 1 — Seis frentes en Binance, seis cierres honestos (jun → 01-jul-2026)

El lab completo (CPCV, DSR/PBO, BHY, OFI/VPIN/VR, ~309 tests) aplicado a un trío de primas de servicio y
tres mecanismos más:

| frente | veredicto | evidencia |
|---|---|---|
| Provisión selectiva (OFI/soledad) | SCREEN-NEGATIVE | AUC 0,503; benigna −0,79bps |
| Ejecución OFI-aware | SCREEN-NEGATIVE | ahorro negativo, t −8..−28 |
| Funding carry (~5,5 años) | SCREEN-NEGATIVE | Sharpe +0,12 (t 0,26); bug de beta-rodante cazado |
| Cross-venue Binance→Bybit | ARCHIVADO | lidera ~50ms, no ensancha en stress = juego de velocidad |
| **Contrarian OFI (disparo mayor)** | **SCREEN-NEGATIVE** (`f560554`) | 11 meses CHD, 318/328 días; −10,71bps/evento, t_neff −26,16 — decisivo, no por potencia |
| H3 cascadas / H6 listings | INCONCLUSO-POR-MASA (`8fb5d5e`) / premisa débil (`fbd0f4c`) | pre-checks de 2 capas, held-outs sin gastar |

**META-CONCLUSIÓN (`fbd0f4c`):** los perps maduros de Binance y sus listings NO dan edge
direccional/provisión a un jugador lento con infra retail 2025-26. Resultado positivo: un mapa de dónde
no buscar, una maquinaria validada, y la pista dura que abre el Cap 2 — el flujo de esos libros está
INFORMADO; si algo existe, es del lado maker/selección-adversa.

## Interludio — Hyperliquid (02-jul-2026)

Premisa "suelo de latencia 0,7s" AUDITADA Y CORREGIDA antes de gastar (el feed publica a 0,5s; los
bloques van a 0,1-0,2s; la protección real del maker es la prioridad de cancels en el L1). Formato del
vendor verificado antes de código (snapshots, no diffs — loader propio). Capa 1 maker: **FALLA POR MASA**
(`24ba268`): 6 candidatos < suelo congelado de 30. Los majors de HL son tan competitivos como un CEX. Un
día, $0, y la hipótesis muerta por su propia regla — no renegociada.

## Cap 2 — Lighter: de la sospecha del vendor a la flor con apelación (02-jul → 05-jul-2026)

1. **Mesa de verificación pre-dato** (`6e3fe93`): fees 0/0 verificados en primarias; formato = diffs +
   anclas; **unidades MIXTAS en el mismo venue** (libro en ns, trades en ms) cazadas antes de mergear.
2. **El vendor, desenmascarado** (`4bd3075`→`2cc3440`): cadena de 4 oráculos (anclas → trades → basis
   cross-venue → prints-en-ventanas-malas) dictamina el canal de libro de CHD-Lighter INUTILIZABLE (88%
   de ventanas malas el segundo día auditado). Cero conclusiones se apoyaron en él. Escalada pre-nombrada
   a fuente L3 (0xArchive): snapshots order-level con **cola y wallet observables**, cadencia ~2,9 min.
3. **El número del capítulo** (`b4d156c`→`c123009`): estimador de informatividad venue-agnóstico,
   CALIBRADO primero contra la verdad de Binance (6/6, t−4,11) → **el flujo de Lighter es NEUTRO** → el
   hábitat es MAKER.
4. **Capa 1 maker: el primer "PASA" del programa** (`0a6b85d`): 8 candidatos con half-spread≥1bp a fee 0.
   La ley de mapa se confirma: los majors mueren en todo venue; la cola ancha es el hábitat.
5. **Capa 2 (prereg congelado `15f755f`): INCONCLUSO** (`bca9ab4`) — el simulador 200×-lento da fills
   tóxicos donde hay densidad, pero las celdas sin densidad bloquean la unanimidad. La regla firmada
   impidió tanto el falso negativo como el rescate.
6. **Piloto L3 (§7-bis, congelado en 2ª firma `946504b` tras un freeze DETENIDO POR REGLA `b138326`):
   SEÑAL DE EXISTENCIA** (`62a7f1f`) — la cohorte LENTA de LIT (órdenes reales que sobreviven ≥1
   intervalo) cobra +9/+11/+17bps a 1/5/25s (BHY-sig) contra referencia certificada. Primera observación
   positiva del programa. Cautelas escritas el mismo día: n_eff~5, survivor-tilt, existencia≠edge.
7. **Atlas de wallets** (`afda243`): el hábitat es de la clase paciente (top-5 = 30% — no dominado por
   pros)… **pero la persistencia es ROTATORIA** (`e02fe96`): 61,9% del volumen lento en wallets de un
   solo día. **La flor va al banquillo por su propia regla** — la firma exacta del confound de
   supervivencia.
8. **Confirmación decisiva (prereg congelado `9c8f4b1`; nula = supervivencia): leída en frío**
   (`74f0d60`, 149 símbolo-días vírgenes, 0 errores):
   - §3 formal: **INCONCLUSO por discrepancia de horizontes** — a 25s el edge SOBREVIVE dentro del tercil
     agitado pooled (+18,24bps, t+6,69, n_eff 79: la celda donde la nula decía que moriría es la más
     fuerte de la tabla), pero a 5s es ruido → sin unanimidad no hay decreto, en ninguna dirección.
   - §4: **la rotación era MECÁNICA** (bootstrap condicionado a presencia: observado 51,2% vs nulo
     51,0%) — el cargo principal contra la flor queda desestimado; nunca fue evidencia.
   - §5: **la minoría estable replica fuera de ventana** — persistencia pasada que predice edge futuro.
     ⟨ERRATA A11 2026-07-05: los t de §5 se publicaron con un estadístico iid (bug H1); corregidos con
     N_eff son **LIT t+3,05 (5s) / t+10,83 (25s)** — sólidos — y **DOGE 5s t+2,16 marginal, 25s t−0,05
     NULO** (el +55 era concentración de volumen). La réplica de habilidad la carga **LIT sola**, no
     "ambos símbolos". La dirección del hallazgo se sostiene; su fuerza y su "ambos" no. §3 (el veredicto
     formal) usa N_eff correctamente y queda intacto.⟩
   - **Estado: la flor sale del banquillo; condena pendiente SOLO del horizonte corto (5s).**
9. **El colector propio** (`bd2ce74`, `bb52987`): con el WS oficial verificado antes de código, el
   programa despliega su propia captura tick de Lighter — libro a 50ms + **trades con wallet en tiempo
   real** — con heartbeat, réplica offsite validada y regla de certificación provisional pre-escrita.
   Es el instrumento que juzgará el 5s: tres órdenes de magnitud más resolución que la fuente del
   capítulo, gratis, para siempre.

## El estado al cierre del laboratorio (2026-07-05)

- **Una celda viva** con apelación pendiente (el eco de julio, que se acumula solo; su prereg se
  diseñará con mesa fresca y decidirá el papel del 5s hacia delante, jamás retroactivamente).
- **Un instrumento nuevo** recolectando el dato que ningún vendor da (juez futuro del 5s).
- **Dos mapas negativos completos** (Binance maduro, HL maker) que ahorraron capital real.
- **Una carta de ataque** (adjunta) que formula las 11 mejores objeciones antes que ningún tercero,
  con sus residuos declarados.
- **$0 gastados.** La regla mordió contra el propio programa donde más duele: **un freeze detenido en
  el acto de la firma** (`b138326`, test de identidad fallido → no se congeló, se enmendó con control
  positivo y se re-firmó), dos empaquetados descartados por verificar-después, y los priors de la mesa
  puntuados en acta, aciertos y fallos — incluidos tres modales fallados en días clave.
- **Una auditoría del propio código** (A11, 2026-07-05): dos capas (la mesa + 5 agentes independientes de
  contexto fresco) leyeron las 1.104 líneas de cómputo y **cazaron una errata de FUERZA en un número
  publicado** (el t de la minoría estable estaba calculado como iid, no N_eff; inflado ~7-30×). Corregido
  sobre los mismos datos, con LIT sobreviviendo sólido y DOGE cayendo a nulo — antes de que ningún extraño
  lo encontrara. El veredicto formal (INCONCLUSO) no se movió: el bug vivía en un diagnóstico, no en la
  regla. El protocolo encuentra sus propios errores y los publica; es lo máximo que una auto-auditoría
  puede ofrecer, y no sustituye al tercero con el espejo.

Este paquete queda **listo y NO publicado.** Publicar, a quién, y bajo qué política de atribución son
las tres decisiones de la fase siguiente — del propietario, en frío, y no de este documento.
