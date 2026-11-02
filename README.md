# Proyecto integrador — AE2 y AE3

## Patrones horarios de alquiler de bicicletas según tipo de día

Este proyecto formula y responde una necesidad de analítica descriptiva a partir de un dataset de Hugging Face. AE2 conserva la ideación y el reconocimiento original. AE3 transforma y enriquece esos datos, responde tres preguntas con tablas y deja archivos preparados para su representación gráfica en AE4. Cada etapa incluye su Word y su notebook ejecutado.

**Repositorio:** [jecasadiego/proyecto-integrador-analitica-bicicletas](https://github.com/jecasadiego/proyecto-integrador-analitica-bicicletas).

### Necesidad y escenario de uso

El beneficiario propuesto es una coordinación operativa de un sistema de bicicletas compartidas. En un **escenario hipotético de aprendizaje**, necesita conocer cómo se distribuyen los alquileres registrados a lo largo del día y cómo cambian entre días laborables y no laborables, como insumo para revisar horarios de atención y seguimiento operativo. No se ha comprobado un problema de disponibilidad, pérdidas o insatisfacción del servicio.

**Pregunta de análisis:** ¿Cómo varía el número de alquileres de bicicletas por hora entre días laborables y no laborables en Capital Bikeshare durante 2011 y 2012?

Las variables centrales de origen son `hr` (hora), `workingday` (tipo de día) y `cnt` (alquileres registrados). AE2 diseña la comparación; AE3 la ejecuta mediante medias, medianas, cantidades de observaciones y cobertura. El periodo y la unidad de análisis permanecen iguales.

## AE3 Transformación y respuestas descriptivas

Se mantiene la pregunta de AE2 y se desglosa sin ampliar la población ni añadir fuentes:

| Pregunta | Variables finales | Tabla para AE4 |
| --- | --- | --- |
| P1 ¿Cómo varían el promedio y la mediana por hora entre tipos de día? | `hora`, `tipo_dia`, `alquileres_total` | `AE3/resultados/p1_perfil_horario.csv`, 48 filas |
| P2 ¿Qué franjas de seis horas concentran más alquileres dentro de cada tipo de día? | `franja_horaria`, `orden_franja`, `tipo_dia`, `alquileres_total` | `AE3/resultados/p2_franjas.csv`, 8 filas |
| P3 ¿Se mantienen los horarios de mayor promedio al separar 2011 y 2012? | `anio`, `hora`, `tipo_dia`, `alquileres_total` | `AE3/resultados/p3_perfil_anual.csv`, 96 filas |

P2 facilita una lectura por intervalos iguales y P3 comprueba si el perfil combinado oculta diferencias de año. Son desgloses descriptivos de la necesidad original, no nuevas preguntas causales.

**Transformaciones y enriquecimiento.** Se conserva en memoria una copia completa sin modificar (`df_original`, 17.379 × 17). La base de trabajo selecciona seis columnas fuente, cambia sus nombres al español, interpreta la fecha y convierte el indicador laborable a booleano. Añade cinco variables: `fecha_hora = fecha + hora`, `anio = año(fecha)`, etiqueta `tipo_dia`, `orden_franja = hora // 6` y `franja_horaria` con intervalos 00–05, 06–11, 12–17 y 18–23. El resultado tiene **17.379 filas y 11 columnas**. No se eliminan filas ni se imputan valores. El diccionario y la bitácora documentan las reglas y los registros afectados.

Las categorías son reglas del proyecto. Las variables meteorológicas no aportan a estas preguntas y requieren verificar algunos ceros originales; no se seleccionan, pero siguen intactas en el original y AE2. El año y mes codificados se contrastan antes contra la fecha. No se agregan tablas externas. La cuadrícula auxiliar usa las fechas y la clasificación de días del mismo archivo para medir cobertura sin añadir filas ni alquileres al dataset.

**Resultados principales.** El máximo promedio conjunto corresponde a las 17:00 en días laborables (525,29 alquileres por hora registrada) y a las 13:00 en no laborables (372,73). La franja 12–17 concentra el 34,84 % y el 49,39 %, respectivamente, del total de su tipo de día. Las horas máximas se mantienen en ambos años. Las interpretaciones completas, tamaños de grupo y límites aparecen en el notebook y el Word de AE3.

**Unidades y denominadores.** `horas_observadas` cuenta registros; `alquileres_total` suma alquileres, no personas únicas. El promedio y la mediana se expresan en alquileres por hora registrada. La participación P2 divide por los alquileres del mismo tipo de día y suma 100 % dentro de cada tipo antes de redondear. `cobertura_pct` divide las horas observadas entre las esperadas en una cuadrícula nominal de 24 horas por fecha, sin zona horaria ni ajuste de cambios de horario no documentados. Las ausencias no equivalen a cero alquileres; la cobertura no corrige su posible sesgo.

### Ejecutar AE3

Utiliza el mismo entorno y `requirements.txt` de AE2. Desde la raíz del proyecto:

```console
# Windows
.venv\Scripts\python.exe AE3/src/ejecutar_notebook.py
.venv\Scripts\python.exe AE3/src/verificar_entrega.py

# macOS o Linux
.venv/bin/python AE3/src/ejecutar_notebook.py
.venv/bin/python AE3/src/verificar_entrega.py
```

El primer comando ejecuta y guarda `AE3/notebooks/02_transformacion_enriquecimiento.ipynb`, descarga o recupera la misma revisión de Hugging Face y **regenera todos los CSV, el TXT y las validaciones**. No requiere ejecutar AE2 de nuevo: usa su ficha publicada para comprobar la misma huella original. `--desde-notebooks` permite comprobar la ejecución con el kernel iniciado en la carpeta del notebook.

```console
# Apertura interactiva en Windows
.venv\Scripts\python.exe -m jupyterlab AE3/notebooks/02_transformacion_enriquecimiento.ipynb
```

Los cálculos se implementan en `AE3/src/analisis_ae3.py`, importado por el notebook. Se verifica que el original no cambie, se conserven filas y totales, los porcentajes sean consistentes y los CSV releídos coincidan celda a celda con las tablas en memoria. La segunda orden verifica de forma adicional los grupos desde el CSV preparado, las huellas y las salidas del notebook.

### Archivos de AE3

```text
AE3/
├── documento/proyecto_avance_AE3.docx
├── notebooks/02_transformacion_enriquecimiento.ipynb
├── datos/
│   ├── dataset_preparado.csv
│   └── README.md
├── src/
│   ├── analisis_ae3.py
│   ├── ejecutar_notebook.py
│   └── verificar_entrega.py
└── resultados/
    ├── p1_perfil_horario.csv
    ├── p2_franjas.csv
    ├── p3_perfil_anual.csv
    ├── resumen_dataframe_transformado.txt
    ├── diccionario_variables.csv
    ├── comparacion_antes_despues.csv
    ├── tipos_y_nulos_antes_despues.csv
    ├── controles_calidad.csv
    ├── bitacora_transformaciones.csv
    ├── cobertura_por_anio_tipo.csv
    └── validaciones.json
```

Los CSV usan UTF-8, coma como separador, punto decimal y no incluyen índice de Pandas. Fechas y categorías se serializan como texto; sus tipos y reglas constan en el diccionario. Las tablas se exportan sin redondeo deliberado; el notebook y el Word redondean solo la presentación. P1 y P3 permiten perfiles de líneas por hora y tipo de día; P2 permite comparar participación y volumen por franja. AE3 no incluye aún la presentación gráfica final.

El Word de AE3 actualiza el documento de AE2 con metodología, diccionario, resultados, discusión, conclusiones y referencias. El original de AE2 permanece conservado en su carpeta. Para entregar en la plataforma, adjunta el Word de AE3 y comparte el enlace público del repositorio; la publicación no constituye la confirmación de envío en el aula.

## AE2 Fuente y reconocimiento conservados

### Dataset y cobertura

| Elemento | Selección utilizada |
| --- | --- |
| Nombre | Bike Sharing Demand - Hourly (Poisson) |
| Identificador Hugging Face | `t22000t/bike-sharing-tabular` |
| Ficha | [Dataset en Hugging Face](https://huggingface.co/datasets/t22000t/bike-sharing-tabular) |
| Configuración y split | `default` / `train` |
| Revisión fijada | `6b645e0cedbc5208fcca11ac94544b088478bf61` |
| Archivo de origen | `hour.csv` |
| Alcance utilizado | Todos los registros del split; sin muestreo ni filtrado |
| Dimensiones comprobadas | 17.379 filas y 17 columnas |
| Periodo observado | 1 de enero de 2011 a 31 de diciembre de 2012 |
| Unidad de análisis | Registro de una hora del sistema agregado de alquiler de bicicletas |
| Procedencia | Registros reales históricos de Capital Bikeshare, Washington D. C., agregados y publicados en UCI; copia alojada por `t22000t` en Hugging Face |
| Consulta | 22 de octubre de 2026 |
| Condiciones de uso | [Creative Commons Attribution 4.0 International — CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |

Los datos son reales y agregados; no son sintéticos. El split se llama `train` por la organización del repositorio de Hugging Face; en este proyecto se usa para descripción, sin entrenamiento de modelos. La descarga pública no requiere una cuenta ni un token.

El periodo contiene 731 fechas, pero se observan 17.379 de las 17.544 combinaciones fecha-hora posibles: **165 horas no están representadas**. Una hora ausente no se interpreta como cero alquileres. Tampoco deben confundirse los nulos de columnas con las horas que no aparecen como filas. Los conteos describen alquileres registrados, no personas únicas ni demanda insatisfecha. Los datos agregados no permiten analizar estaciones o trayectos, establecer causalidad ni extrapolar resultados a la operación actual o a otras ciudades.

### Archivos

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── .gitattributes
└── AE2/
    ├── documento/
    │   ├── proyecto_inicial_AE2.docx
    │   └── fuentes_y_atribucion.md
    ├── notebooks/
    │   └── 01_reconocimiento_dataset.ipynb
    ├── resultados/
    │   ├── resumen_dataframe.txt
    │   ├── ficha_tecnica.json
    │   └── auditoria_calidad.json
    └── src/
        ├── ejecutar_notebook.py
        └── auditar_dataset.py
```

- El documento desarrolla la necesidad, justificación, objetivos, conceptos, metodología, diccionario inicial, alcance y diseño del proyecto.
- El notebook muestra registros, dimensiones, columnas, tipos y nulos; explica la unidad de análisis y las variables que sustentan la pregunta.
- El notebook crea la carpeta de resultados cuando hace falta y **regenera** `resumen_dataframe.txt` en UTF-8 con la identificación del dataset, revisión, split, alcance, dimensiones, tipos y nulos. También lee el archivo para verificar su contenido.
- `ficha_tecnica.json` conserva metadatos verificables del DataFrame y de la descarga para comprobar la correspondencia entre entregables.
- `auditar_dataset.py` contrasta nuevas descargas de Hugging Face y UCI, verifica la huella del DataFrame del notebook y genera `auditoria_calidad.json` con los controles de calidad y la interpretación de los ceros.
- `fuentes_y_atribucion.md` identifica las fuentes consultadas y las condiciones del dataset.

AE2 no incluye el CSV original en GitHub. Al ejecutar, la biblioteca `datasets` descarga los datos públicos y utiliza su caché local de Hugging Face, fuera del historial del repositorio. AE3 sí publica la versión seleccionada y enriquecida bajo la misma licencia CC BY 4.0. La primera ejecución necesita conexión a Internet. El archivo original ocupa aproximadamente 1,16 MB; el entorno de Python y sus dependencias requieren espacio adicional.

### Ejecución reproducible

Se comprobó con **Python 3.12**. Ejecuta los comandos desde la raíz del repositorio.

Primero clona el proyecto:

```console
git clone https://github.com/jecasadiego/proyecto-integrador-analitica-bicicletas.git
cd proyecto-integrador-analitica-bicicletas
```

**Windows (PowerShell o CMD):** no es necesario activar el entorno virtual.

```console
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe AE2/src/ejecutar_notebook.py
```

**macOS o Linux:** utiliza una instalación disponible de Python 3.12.

```console
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python AE2/src/ejecutar_notebook.py
```

El script ejecuta el notebook con el Python del entorno utilizado y guarda sus resultados visibles. El notebook descarga la revisión fijada, construye el DataFrame y actualiza los dos archivos de `AE2/resultados/`. No se necesita registrar un kernel de forma global.

El repositorio fija finales de línea LF mediante `.gitattributes` para conservar los bytes UTF-8 del resumen y su verificación SHA-256 al clonar en diferentes sistemas.

Para repetir la auditoría adicional contra la fuente original, después de ejecutar el notebook:

```console
# Windows
.venv\Scripts\python.exe AE2/src/auditar_dataset.py

# macOS o Linux
.venv/bin/python AE2/src/auditar_dataset.py
```

La auditoría necesita Internet y lee el CSV de Hugging Face y el ZIP oficial de UCI en memoria, sin incorporarlos al repositorio. La igualdad entre fuentes verifica la fidelidad de la copia, no garantiza que cada medición original sea correcta.

### Por qué aparecen ceros

El notebook distingue los nulos de los valores numéricos iguales a cero y muestra ejemplos de ambos años y tipos de día. En la tabla `valores_nulos`, **0 significa que no se encontraron celdas vacías**. En los controles de duplicados o discrepancias, 0 significa que no se encontraron esos problemas. En las variables, `yr = 0` representa 2011 y `workingday = 0` identifica un fin de semana o festivo; son códigos válidos.

La nueva revisión confirmó que `cnt` contiene valores entre 1 y 977, con un total observado de 3.292.679 alquileres. El archivo no es una tabla de ceros. Sí se documentan 22 valores de humedad iguales a cero concentrados en el 10 de marzo de 2011. La fuente no explica su causa: deben verificarse antes de un análisis meteorológico. Se conservan sin imputarlos ni eliminarlos y no intervienen en la pregunta principal, que usa `hr`, `workingday` y `cnt`.

Para abrirlo de manera interactiva:

```console
# Windows
.venv\Scripts\python.exe -m jupyterlab AE2/notebooks/01_reconocimiento_dataset.ipynb

# macOS o Linux
.venv/bin/python -m jupyterlab AE2/notebooks/01_reconocimiento_dataset.ipynb
```

En Jupyter, selecciona el kernel del entorno y ejecuta todas las celdas en orden. El notebook ubica la raíz del proyecto para escribir los resultados mediante una ruta relativa.

### Atribución y fuentes

Fanaee-T, H. (2013). *Bike Sharing* [Dataset]. UCI Machine Learning Repository. [https://doi.org/10.24432/C5W894](https://doi.org/10.24432/C5W894). Copia utilizada: `t22000t/bike-sharing-tabular`, alojada en Hugging Face. La licencia CC BY 4.0 permite compartir y adaptar los datos con atribución, enlace a la licencia e indicación de modificaciones. Este proyecto conserva los registros del CSV sin muestreo; genera resúmenes y documentación.

La procedencia y la verificación de la copia se describen en [fuentes y atribución](AE2/documento/fuentes_y_atribucion.md). Referencias técnicas: [carga desde Hugging Face](https://huggingface.co/docs/datasets/loading), [conversión a Pandas](https://huggingface.co/docs/datasets/use_with_pandas) y [medidas de posición — NIST](https://www.itl.nist.gov/div898/handbook/eda/section3/eda351.htm).
