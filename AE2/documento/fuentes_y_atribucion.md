# Fuentes y atribución de los datos

Consulta de las fuentes: **22 de octubre de 2026**.

## Dataset utilizado

- **Nombre:** Bike Sharing Demand - Hourly (Poisson).
- **Repositorio:** [`t22000t/bike-sharing-tabular`](https://huggingface.co/datasets/t22000t/bike-sharing-tabular).
- **Configuración:** `default`.
- **Split:** `train`, utilizado completo para descripción, sin entrenamiento ni muestreo.
- **Revisión:** `6b645e0cedbc5208fcca11ac94544b088478bf61`.
- **Archivo:** [hour.csv en la revisión fijada](https://huggingface.co/datasets/t22000t/bike-sharing-tabular/resolve/6b645e0cedbc5208fcca11ac94544b088478bf61/hour.csv).
- **Acceso:** público; no requiere autenticación.
- **Licencia indicada en Hugging Face y UCI:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Atribución

Fanaee-T, H. (2013). *Bike Sharing* [Dataset]. UCI Machine Learning Repository. [https://doi.org/10.24432/C5W894](https://doi.org/10.24432/C5W894).

Se utiliza la copia alojada por **t22000t** en Hugging Face, cuya ficha remite a la fuente UCI. El registro original corresponde a Capital Bikeshare, Washington D. C., Estados Unidos. El `Readme.txt` original explica que los registros de 2011–2012 se agregaron por hora y por día, y se complementaron con información meteorológica y estacional. Por esa procedencia son datos reales agregados, no datos sintéticos. La denominación «Poisson» de la ficha no obliga a realizar modelamiento en este proyecto descriptivo.

Como referencia de la publicación vinculada por los autores: Fanaee-T, H., y Gama, J. *Event labeling combining ensemble detectors and background knowledge*. DOI: [10.1007/s13748-013-0040-3](https://doi.org/10.1007/s13748-013-0040-3). Esta referencia se toma de la documentación del dataset; no se afirma haber revisado el artículo completo.

CC BY 4.0 permite reutilizar y adaptar el material atribuyendo su procedencia, enlazando la licencia e indicando las modificaciones. En esta etapa se cargan todos los registros del CSV sin filtrar ni imputar valores; se generan un resumen técnico y documentación. El dataset no se redistribuye dentro del repositorio del proyecto: se descarga al ejecutar el notebook.

## Comprobación de la copia

Durante la preparación se comparó el CSV de Hugging Face con `hour.csv` extraído en memoria del [ZIP oficial de UCI](https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip). Ambos archivos son idénticos: **1.156.736 bytes** y el mismo SHA-256:

```text
e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f
```

La cardinalidad verificada mediante código es de **17.379 filas y 17 columnas**, con fechas entre `2011-01-01` y `2012-12-31`. Se utiliza el archivo completo; no se presenta una muestra como si fuera el total. La cobertura incluye 731 fechas, con 165 combinaciones fecha-hora ausentes respecto de las 17.544 posibles; no se interpreta su ausencia como cero alquileres.

La ficha web actual de UCI presenta algunas diferencias respecto del CSV y del `Readme.txt` original, entre ellas el total de instancias y la descripción de ciertas variables meteorológicas o estacionales. Las dimensiones se toman del DataFrame comprobado. La pregunta central utiliza `hr`, `workingday` y `cnt`, cuyas definiciones son suficientes y coinciden entre las fuentes; no necesita interpretar `season`, `temp` o `atemp`.

## Fuentes realmente consultadas

| Fuente | Uso en el proyecto |
| --- | --- |
| [Ficha de Hugging Face](https://huggingface.co/datasets/t22000t/bike-sharing-tabular) | Identificador, configuración, acceso, licencia, variables y relación con UCI. |
| [Metadatos públicos del repositorio HF](https://huggingface.co/api/datasets/t22000t/bike-sharing-tabular) | Comprobación de la revisión, carácter público y archivo disponible. |
| [Ficha UCI Bike Sharing](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) | Procedencia original, descripción, cita y licencia. |
| [ZIP oficial UCI: Readme.txt y hour.csv](https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip) | Procedencia, agregación horaria, diccionario original y comparación de la copia. |
| [Creative Commons: CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Condiciones de atribución y reutilización. |
| [Hugging Face: Load](https://huggingface.co/docs/datasets/loading) | Obtención por código, split y fijación de la revisión. |
| [Hugging Face: Use with Pandas](https://huggingface.co/docs/datasets/use_with_pandas) | Conversión del Dataset a DataFrame. |
| [NIST: Measures of Location](https://www.itl.nist.gov/div898/handbook/eda/section3/eda351.htm) | Definición de media y mediana para el diseño descriptivo previsto. |

La comparación por hora deberá acompañar cada grupo con su número de observaciones. La media resume el promedio de alquileres por registro horario y la mediana su valor central; ambas evitan que una comparación basada únicamente en totales confunda diferencias de volumen con diferencias en la cantidad de registros disponibles. No se proponen relaciones causales ni resultados de un análisis detallado en esta etapa.
