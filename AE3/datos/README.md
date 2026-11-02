# Datos preparados de AE3

`dataset_preparado.csv` se genera al ejecutar `AE3/notebooks/02_transformacion_enriquecimiento.ipynb` con el módulo `AE3/src/analisis_ae3.py`. Contiene todas las 17.379 observaciones originales y 11 variables seleccionadas o derivadas. Cada fila representa una fecha y una hora agregada de Capital Bikeshare de 2011 o 2012.

Fuente original: Fanaee-T, H. (2013). *Bike Sharing*. UCI Machine Learning Repository. https://doi.org/10.24432/C5W894

Copia utilizada: https://huggingface.co/datasets/t22000t/bike-sharing-tabular — configuración `default`, split `train`, revisión `6b645e0cedbc5208fcca11ac94544b088478bf61`.

Licencia de los datos: **Creative Commons Attribution 4.0 International (CC BY 4.0)**, https://creativecommons.org/licenses/by/4.0/. Se conserva la atribución a la fuente original y al redistribuidor `t22000t`. No se atribuye a los productores el respaldo de las transformaciones ni de las conclusiones del proyecto.

Cambios realizados: selección de seis columnas fuente, nombres en español, fecha interpretada, indicador booleano, fecha y hora combinadas, año, etiquetas de tipo de día y franjas de seis horas. Se conservan filas y conteos; no se imputan faltantes ni se eliminan ceros. Las 165 horas nominales sin registro no se incorporan como filas. No se añade otra fuente ni se asigna una zona horaria no documentada.

Formato: UTF-8, separador coma, punto decimal, sin índice. El diccionario actualizado está en `AE3/resultados/diccionario_variables.csv`. En el CSV, las fechas y categorías son texto; la fecha usa `AAAA-MM-DD HH:MM:SS`. Para cargar con Pandas se pueden interpretar `fecha` y `fecha_hora` mediante `parse_dates`.
