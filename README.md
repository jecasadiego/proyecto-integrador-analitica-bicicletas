# Proyecto integrador — AE2

## Patrones horarios de alquiler de bicicletas según tipo de día

Este proyecto formula y documenta una necesidad de analítica descriptiva a partir de un dataset de Hugging Face. La etapa AE2 incluye el documento inicial en Word, un notebook ejecutado que obtiene y reconoce los datos y un resumen `.txt` generado automáticamente desde el mismo DataFrame.

**Repositorio:** [jecasadiego/proyecto-integrador-analitica-bicicletas](https://github.com/jecasadiego/proyecto-integrador-analitica-bicicletas).

### Necesidad y escenario de uso

El beneficiario propuesto es una coordinación operativa de un sistema de bicicletas compartidas. En un **escenario hipotético de aprendizaje**, necesita conocer cómo se distribuyen los alquileres registrados a lo largo del día y cómo cambian entre días laborables y no laborables, como insumo para revisar horarios de atención y seguimiento operativo. No se ha comprobado un problema de disponibilidad, pérdidas o insatisfacción del servicio.

**Pregunta de análisis:** ¿Cómo varía el número de alquileres de bicicletas por hora entre días laborables y no laborables en Capital Bikeshare durante 2011 y 2012?

Las variables centrales son `hr` (hora), `workingday` (tipo de día) y `cnt` (alquileres registrados). El diseño posterior propone comparar media, mediana y cantidad de observaciones en cada combinación de hora y tipo de día. AE2 realiza únicamente la carga y el reconocimiento básico necesarios para plantear ese análisis.

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

No se incluye una copia del dataset en GitHub. Al ejecutar, la biblioteca `datasets` descarga los datos públicos y utiliza su caché local de Hugging Face, fuera del historial del repositorio. La primera ejecución necesita conexión a Internet. El archivo original ocupa aproximadamente 1,16 MB; el entorno de Python y sus dependencias requieren espacio adicional.

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

### Revisión y entrega en la plataforma

La portada identifica a Juan Esteban Casadiego Benavides y Evelyn Cerro, grupo 17, asignatura Proyecto Integrador Diseño y Documentación, docente Andrés Felipe Callejas Jaramillo e Institución Universitaria Digital de Antioquia. El documento utiliza un formato académico editable. No se suministró la plantilla institucional; su conformidad requiere contrastarlo con ella antes de presentar el trabajo.

1. Abre el Word, confirma sus datos académicos y revisa los apartados desarrollados.
2. Confirma que el notebook tenga resultados visibles y que el `.txt` coincida con el DataFrame.
3. Adjunta `AE2/documento/proyecto_inicial_AE2.docx` en la actividad.
4. Comparte el enlace de este repositorio y comprueba que el docente pueda abrirlo.
5. Confirma el envío en la plataforma según las condiciones publicadas por el curso.

La publicación del repositorio no sustituye el envío de la actividad en la plataforma.
