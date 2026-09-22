# Mesa · Push, CI y simplificación después de I5

2026-09-07. Revisión de PARA_LA_MESA_2026-09-07_PUSH_CI_Y_V2_SUSTRACCION.md.
HEAD observado: 1ca5ca6674ce55ad0aca149b7b5757a87f83f25e, rama codex/wip-m12.20.

**Decisión: aprobar el push de esa rama y ese commit; corregir el guardia mediante
excepciones acotadas; mantener la simplificación aprobada, incluido el retiro completo
de la campaña bajo las condiciones del apartado 5. Conservar el .git del laboratorio.**

Esta revisión es documental y de código. No ejecuta push, suites, arneses, lecturas de
mercado, conexiones al VPS ni borrados. No cambia el resultado, instrumentos o contratos
congelados de I5. El informe de Code se conserva; las correcciones quedan aquí.

## 1. Evidencia y límites de la verificación

La mesa comprobó el manifiesto local completo: 13.074 entradas, sin líneas malformadas,
SHA-256 d302d8cc04470aef799efce35d2bcd0939554b7990081135cb74cbca86c94a01.
Comparó nombres de ficheros, sin abrir cuerpos de mercado, en las seis carpetas principales:

| Carpeta en Desktop/Laboratorio | Ficheros actuales | Incluidos en el manifiesto |
|---|---:|---:|
| I5_L3_CHECKPOINT_20260906_01 | 451 | 451 |
| I5_CHD_OCHO_20260907_02 | 773 | 773 |
| I5_CHD_RESTO_71_20260907_01 | 6.773 | 6.773 |
| I5_REPRODUCCION_OCHO_20260907_01 | 35 | 35 |
| I5_REPRODUCCION_RESTO_71_20260907_01 | 288 | 288 |
| I5_D1_79_20260907_01 | 242 | 242 |

No falta ningún nombre actual de esas carpetas en el manifiesto. Esto acredita inclusión,
no sustituye una comprobación de sus cuerpos. Los hashes en el VPS y la comparación remota
por checksum son verificaciones comunicadas por Code; la mesa no las repitió.
El protocolo de tools/backup.py exige además código de salida cero: stdout vacío por sí
solo no certifica una comparación rsync correcta. Conservar sus salidas y códigos existentes.

Las dos copias comunicadas cierran la tarea de respaldo encargada. No se convierte este
dictamen en otra copia ni en una repetición de descargas. Los temporales incluidos de más
no requieren una limpieza para continuar.

## 2. Corrección material: el .git del laboratorio no está vacío

En <USER_HOME>/Desktop/Laboratorio/.git hay **774 objetos sueltos** y una referencia:

refs/codex/turn-diffs/captures/1787141016051/0609f719-2935-4e30-a80d-29e01768a89f/base

Apunta al objeto a8809278779d5ceef061a2fe05a7cd7eb66a6203, de tipo tree, con 65 rutas.
HEAD no resuelve a un commit y el índice no tiene ficheros; eso no implica ausencia de
objetos o de contenido conservado. No se inspeccionaron los cuerpos de esa captura.
El manifiesto de respaldo incluye **793 ficheros de .git, entre ellos sus 774 objetos
y esa referencia**. No son únicamente hooks de ejemplo, HEAD y config.

**Se rechaza el borrado basado en la premisa de repositorio vacío.** Se conserva tal cual.
El fallo ambiental se resuelve usando una carpeta temporal realmente fuera de cualquier
repositorio, sin borrar metadatos del usuario. No hace falta repetir hoy la suite por ello.

El test test_gate_dos_worktrees.py:111 llama únicamente a raiz_gate_compartida con una
carpeta que presupone ajena a git. El helper de eco_gate_b.py:486 sí descubre repositorios
ascendentes. El fallo respalda el diagnóstico de fixture ambiental, **no demuestra que
una lectura protegida pueda saltarse el gate**: preparar_lectura_gate deriva por defecto
la raíz del código, exige origin/main, atestación y freeze, y pasa explícitamente esa raíz
a la autoridad compartida (eco_gate_b.py:923,945,1050). Se retira la generalización de
que cualquier ejecución desde el laboratorio abriría el gate.

## 3. Orden de publicación y lectura de la CI

Se autoriza a Code a publicar **únicamente** el commit
1ca5ca6674ce55ad0aca149b7b5757a87f83f25e en origin, rama codex/wip-m12.20.
Primero comprobar la referencia remota real y que el avance sea fast-forward. Si ya está
publicado, registrar ese hecho; si hay divergencia, detener ese push y traer la diferencia.
No usar force, no publicar otras ramas, no integrar en main ni incluir archivos untracked.
La autorización comprende observar la CI que dispare ese push y devolver commit, run,
estados por paso y causas. No incluye reintentos automáticos de jobs fallidos.

Ese push publica un punto de partida con fallos conocidos. **No constituye una base verde
ni una acreditación de L, F o de una lectura protegida.** La integración en main sigue aparte.
Un pull request tampoco integra por sí mismo, y normalmente requiere publicar antes la rama.

La suite de 1.997 passed, 2 failed, 7 skipped y 1 xfailed es el resultado local comunicado
por Code. Windows/Python 3.14 no acredita Ubuntu/Python 3.12; los arneses no se ejecutaron
hoy. El rojo de completitud tiene una causa identificada en fuente. El estado del resto
en CI sigue pendiente hasta que la CI lo mida; no se declara verde por expectativa.
El número de objetos git sin cambios tampoco demuestra por sí solo que una suite no haya
modificado el árbol. Al revisar ahora no había modificaciones trackeadas.

## 4. Guardia de completitud: arreglo elegido

Se aprueba corregir el control fuera de los instrumentos congelados, mediante excepciones
de alcance exacto y verificable. Los tres sitios son:

| Sitio | Motivo que se comprobó en código |
|---|---|
| tools/i5_d1.py::load_base::np.load | Verifica tamaño y hash de los mismos bytes que carga, liga el manifiesto y valida el contenido después de cargar; el carril no conforme queda explícito. |
| tools/i5_d1.py::save_annex::np.savez | Anexo diagnóstico con recibo propio, hash, procedencia y canonical_input=false; no es un artefacto canónico acreditado. |
| tools/i5_productor_forense.py::execute::publicar | check_output se llama antes e invoca exigir_produccion; el control AST actual solo reconoce dominancia dentro de la misma función. |

EXENTAS cubre operaciones numpy; **añadir tres filas a esa tabla no resuelve la tercera
ruta**, que pertenece a comprobar_dominancia. El parche debe tratar ambas reglas.

Las excepciones identificarán archivo, función, operación, una llamada esperada y hash
exacto de la fuente auditada. El módulo i5_d1.py está fijado a
8713b171632e75a88001e34c22fdf2264f54c132a8e8a3741a8c9a495d7279f1;
i5_productor_forense.py a e4011fc691d5610fd02c116d3f067a94edf5431afaec56391a5f2b583bf3878e.
Cambio de cuerpo, segunda llamada o excepción sin sitio correspondiente deben dar rojo.
No se admiten comodines, exclusión de carpetas enteras ni relajar la regla para productores
futuros. No se importa ni ejecuta I5 para conceder la excepción.

Codex implementa ese parche separado; Code audita el diff y los focales pertinentes.
Las pruebas deben demostrar rechazo de los casos anteriores y que un productor ajeno
siga vigilado. No repetir D1 ni la suite larga local para este arreglo acotado. La siguiente
publicación del parche tendrá su propia constancia de auditoría y lectura de CI.

## 5. Simplificación: decisión sobre los lotes y el retiro de la campaña

Se mantiene la aprobación de Manuel a los lotes 1, 2 y 4. **Se aprueba también el lote 3
como retiro completo de la campaña eco del árbol activo**, con una lista concreta de
entradas, dependencias, controles y tests que salen juntos. No se aprueba quitar el libro
y el gate dejando operativos productores o lectores cuya protección dependía de ellos.
Si queda una entrada dependiente, se conserva su control hasta retirar esa entrada.

No se exige reconstruir un sistema genérico equivalente para una campaña retirada.
Tampoco se concede que las guardas de I5 lo sustituyan: I5 fue un diagnóstico histórico
sobre una muestra autorizada, no un ensayo de protección de datos reservados. Un plan por
hash y una carpeta de salida exclusiva no impiden por sí mismos repetir en otra carpeta,
otro worktree o proceso. Treinta líneas no son una medida de equivalencia de protección.

La protección viaja con cada objeto es un principio aceptable para diseños futuros;
necesita un contrato concreto cuando exista el objeto. Se mantienen STOP, las ventanas
LIT desde 2026-06-30 y WTI desde 2026-06-05 y D3: custodia ciega autorizada no habilita
medias, signos o pruebas de markout. Retirar el eco no desbloquea esos datos. Antes de
cualquier nuevo lector protegido, la mesa fija alcance, frontera de gasto, autoridad
de uso y recuperación; Codex implementa y Code audita. No se abre ahora esa implementación.

Antes de cada lote, su diff e inventario deben demostrar que lo conservado sigue completo:
imports, comandos, workflows y servicios de captura o respaldo. No se retiran pruebas
para ocultar fallos de código que permanece. En lote 3 se retiran los arneses específicos
de controles retirados; no se elimina por arrastre la prueba de ref_valida si esa pieza queda.
Los límites de líneas y tiempo orientan la reducción, no dispensan estas obligaciones.

ARCHIVO.md conservará ruta, propósito, último commit y motivo. Para I5 la restauración
de referencia es el árbol completo de 1ca5ca6 y la historia de julio que extrae, no once
scripts aislados ni solo 74f0d60: las fuentes y dependencias modernas también están ligadas
por hash en sus planes. Mover instrumentos ejecutables fuera de analysis/ y tools/ solo
para que el guardia deje de verlos no es una corrección admisible.

Los documentos históricos conservan su texto y sus hashes. Un índice breve indicará
qué quedó cerrado y dónde está cada expediente; no reescribir el LEDGER congelado para
presentar decisiones posteriores como anteriores a D1.

Secuencia acordada: publicar el punto de partida y observar CI; resolver el control
acotado; luego lotes de retiro con dependencias verificadas y CI por lote. Esta revisión
no ordena descargas, nuevas hipótesis, lecturas protegidas o cambios en el VPS.
