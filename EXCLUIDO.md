# Lo que este espejo NO contiene, y por que

La regla de curacion es una sola: **entra la ciencia y la maquinaria; queda fuera la operacion de
una maquina que sigue corriendo y el trafico interno entre las partes.** Con una excepcion que la
gobierna: **si un documento que SI viaja lo ENLAZA, viaja tambien** — un expediente publicado con
enlaces colgando no es verificable. Por eso `quant-system-ingesta/qs/docs/` conserva sus 7 ordenes
de trabajo y sus 21 recibos de ejecucion, mientras que los de la raiz del expediente se quedan fuera.

La excepcion se enuncia por ENLACES y no por menciones a proposito: 103 de los ficheros ausentes
aparecen NOMBRADOS en algun documento de aqui —casi todos en un inventario que enumera el arbol
entero—, y arrastrarlos por eso habria traido el arbol completo. Lo que se comprueba, y se comprueba
con un verificador sobre los .md del espejo, es que ningun enlace apunte a un fichero que no esta.

El arbol original tiene 344 ficheros bajo control de versiones; aqui hay 173.
Faltan 171, y cada uno cae en una categoria y solo una:

| categoria | ficheros | por que |
|---|---:|---|
| `infra/ (salvo collector.py)` | 10 | unidades systemd, latido y el script de replica, que lleva la cuenta del almacenamiento externo |
| `quant-system-ingesta/qs/deploy/` | 9 | unidades systemd e instalador de una maquina que sigue corriendo |
| `quant-system-ingesta/qs/data_hist/` | 14 | agregados derivados; fuera por prudencia de licencia, no por contenido |
| `.claude/ (salvo la checklist congelada)` | 7 | configuracion de los agentes; la checklist adversarial congelada SI viaja, porque es evidencia |
| `docs/runs/` | 63 | recibos de ejecucion de la raiz del expediente, demasiado granulares para un lector externo |
| `docs/PARA_*` | 26 | ordenes de trabajo entre las partes, en la raiz del expediente |
| `docs/bitacoras/` | 2 | montaje de la infraestructura, con sus identificadores |
| `docs/CONTINUAR_AQUI.md` | 1 | estado operativo con rutas y modo de acceso a la maquina |
| `otros documentos de proceso` | 29 | estados, planes, encargos y notas de trabajo que ningun documento de aqui enlaza |
| `README.md` | 1 | pagina de navegacion del arbol original, con enlaces a documentos que no viajan; la sustituye el README de este espejo |
| `resto del arbol` | 9 | ficheros sueltos que no son ni ciencia ni maquinaria: binarios antiguos, plantillas y scripts de arranque |
| **total** | **171** | |

El recuento de esta tabla lo genera el constructor del espejo y falla si no cuadra con
`git ls-files` del arbol original. Los SHA-256 de lo que si viaja estan en `MANIFEST.md`.
