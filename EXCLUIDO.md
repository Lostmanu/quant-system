# Lo que esta copia no contiene

Esta copia incluye el código, las pruebas, las comprobaciones y el expediente del laboratorio. Deja fuera
lo que servía para operar la máquina del colector, los mensajes de trabajo entre las partes y los
planes y guías internas del proyecto, con una excepción: si un documento incluido enlaza a otro fichero, ese fichero también se incluye, para que ningún
enlace del expediente quede roto. Por eso `quant-system-ingesta/qs/docs/` conserva sus 7 órdenes de
trabajo y sus 21 recibos de ejecución, y los de la raíz del expediente se quedan fuera.

La regla se aplica a enlaces y no a menciones, porque 105 de los 171 ficheros ausentes aparecen
nombrados en algún documento incluido, casi todos en un inventario que enumera el árbol completo, y
seguir las menciones habría traído el repositorio entero. El constructor de la copia, que no se publica, comprueba que ningún
enlace de los `.md` apunte a un fichero ausente; queda uno a propósito, hacia una carpeta de custodia que
no está en el repositorio.

El repositorio original tiene 344 ficheros bajo control de versiones y aquí hay 173. Los 171 restantes se
reparten así:

| categoría | ficheros | motivo |
|---|---:|---|
| `infra/ (salvo collector.py)` | 10 | unidades systemd, latido y el script de réplica, que contiene la cuenta del almacenamiento externo |
| `quant-system-ingesta/qs/deploy/` | 9 | unidades systemd e instalador de la máquina del colector |
| `quant-system-ingesta/qs/data_hist/` | 14 | agregados derivados; fuera por prudencia con la licencia de los datos |
| `.claude/ (salvo la checklist congelada)` | 7 | configuración de los agentes; la checklist adversarial congelada sí se incluye, porque es evidencia |
| `docs/runs/` | 63 | recibos de ejecución de la raíz del expediente, demasiado detallados para un lector externo |
| `docs/PARA_*` | 26 | órdenes de trabajo entre las partes, en la raíz del expediente |
| `docs/bitacoras/` | 2 | montaje de la infraestructura, con sus identificadores |
| `docs/CONTINUAR_AQUI.md` | 1 | estado operativo, con rutas y modo de acceso a la máquina |
| `otros documentos de proceso` | 29 | estados, planes, encargos y notas de trabajo que ningún documento incluido enlaza |
| `README.md` | 1 | página de navegación del repositorio original, con enlaces a documentos que no se incluyen; la sustituye el README de esta copia |
| `resto del árbol` | 9 | el plan maestro (docx), la especificación de ingesta, la guía y las notas de configuración de los agentes, una orden de trabajo, un log de ejecución, un CSV de comprobación y el `.gitattributes` original, sustituido por el de esta copia |
| **total** | **171** | |

El constructor de la copia genera esta tabla y se detiene si la suma no coincide con `git ls-files` del
repositorio original. Los SHA-256 de los ficheros incluidos están en [`MANIFEST.md`](MANIFEST.md).
