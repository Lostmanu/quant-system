# SANEAMIENTO DEL ESPEJO — acta del escaneo (2026-07-05)

Ningún byte se empaqueta sin verificar. Este documento registra QUÉ se buscó, QUÉ se encontró y QUÉ se
redacta, para que el auditor del futuro no tenga que fiarse de la palabra "limpio".

## Escaneo realizado (5 comprobaciones, working tree + HISTORIA completa)

| # | comprobación | método | resultado |
|---|---|---|---|
| 1 | Claves de API reales (CHD, 0xArchive) | prefijo de la clave real greppeado contra working tree y `git log --all -S` (la clave jamás se imprime) | **0 y 0** — jamás tocaron el repo |
| 2 | Ficheros de secretos (`.env`, `*key*`, `*secret*`, `*token*`) | `git ls-files` + `git log --all --diff-filter=A` | solo `telegram.env.example` (plantilla sin valores); `.env` jamás commiteado |
| 3 | Token de Telegram (formato `dígitos:base64`) | `git log --all -SG` con regex de formato | **0** en toda la historia |
| 4 | Literales token-like (≥40 chars alfanuméricos) | `git grep -E` sobre tracked | benignos: nombres de papers, rutas, hashes de git |
| 5 | Datos crudos de vendor | `git ls-files data_hist` + tamaños | solo AGREGADOS derivados (CSVs de stats, outputs de screen, listas de `owner_account_index` = identificadores públicos on-chain vía 0xA); cero filas crudas de CHD/0xA; ficheros >1MB tracked: ninguno |

## Hallazgos que el espejo PÚBLICO debe redactar (presentes en tracked + historia)

- **IP del VPS** (`<VPS_IP>`), **hostname** (`<VPS_HOST>`) y **cuenta de almacenamiento externo**
  (`<STORAGEBOX_USER>…<STORAGEBOX_HOST>`) en 8 ficheros (CLAUDE.md, docs/, infra/, config, tests, tools).
- **Rutas absolutas con usuario** (`<USER_HOME>\…`, incl. ubicación de ficheros de clave — la RUTA,
  no la clave).

Ninguno es un secreto criptográfico; todos son superficie de ataque/identidad innecesaria en un
artefacto publicable.

## Diseño resultante: DOS artefactos

1. **TESTIGO INTERNO (privado, no publicable):** `git bundle --all` = la historia completa con todos los
   hashes de freeze — el notario. Contiene IP/rutas (da igual: es privado). SHA256 en el MANIFEST.
2. **ESPEJO SANEADO (publicable, listo-NO-publicado):** snapshot del working tree SIN historia, con
   redacciones (`IP→<VPS_IP>`, `host→<VPS_HOST>`, `storagebox→<STORAGEBOX_USER>`,
   `<USER_HOME>→<USER_HOME>`), verificado post-empaquetado (grep de cada patrón = 0 hits) + el
   MANIFEST con la cadena de hashes de freeze, para que quien reciba acceso al privado pueda verificar
   que el espejo corresponde a la historia real.

**Por qué sin historia:** la historia contiene los hallazgos de arriba en commits antiguos (bitácoras);
reescribirla destruiría la autoridad de fecha de los freezes. La historia queda como notario privado; el
espejo lleva el manifiesto de hashes como puente verificable.

## Nota de procedencia de la evidencia tracked

Los ficheros bajo `data_hist/` versionados a la fuerza son SALIDAS de screens (números agregados,
t-stats, conteos) y listas de identificadores públicos de un libro on-chain. No contienen datos
redistribuibles de vendor. La materia prima (L2/L3/trades crudos) vive fuera del repo, gitignorada, y
se re-deriva de las fuentes (CHD/0xA/colector propio) con los scripts congelados.

## Acta de ejecución (2026-07-05, post-commit `c687595`)

Empaquetado ejecutado y VERIFICADO: bundle `git bundle verify` íntegro; espejo con **0 hits en 8
patrones** (IP, host, storagebox, usuario, email personal, usuario GitHub, noreply, arroba-local — los
patrones se nombran aquí SIN su forma cruda, para que este acta no dispare su propia verificación) tras
4 pasadas de redacción. Tres lecciones de la propia validación, fechadas: (1) el entorno de shell COME un
backslash en scripts sed/heredoc (patrones `\\` llegan como `\` → seds "exit ok" sin efecto; esta misma
frase llegó comida al primer commit: el bug documentándose a sí mismo) — la
redacción definitiva se hizo en Python construyendo el patrón con `chr(92)`; (2) los `.log` de evidencia
no estaban en la lista de extensiones de la primera pasada; (3) **verificar-antes-de-empaquetar como
orden obligatorio** — dos tars se descartaron por verificar después. El MANIFEST (huellas SHA256 +
cadena de hashes + protocolo del auditor) vive JUNTO a los artefactos, fuera del repo.

## Dos cláusulas de la contrafirma de la mesa (2026-07-05)

1. **Este fichero se redacta a sí mismo en el espejo.** SANEAMIENTO.md es, por construcción, el fichero
   con más probabilidad de contener lo que redacta (cita IP, host y cuenta en texto plano para
   documentar el escaneo). Consta explícitamente: la copia PÚBLICA de este documento pasa por las mismas
   pasadas de redacción y el grep de verificación final la cubre — en el espejo, las menciones de arriba
   aparecen como placeholders. El sitio donde un descuido sería a la vez más probable y más irónico
   queda vigilado por regla escrita.
2. **El paquete de testigos no vive solo en un Desktop.** El notario de todo el programa a un incidente
   de disco de no haber existido es inaceptable: `quant-system-testigos\` se replica al almacenamiento externo
   (vía VPS, junto a la réplica del colector), con sus huellas en el MANIFEST. El juzgado entero,
   asegurado por las mismas dos líneas de rsync que ya protegen los datos.
