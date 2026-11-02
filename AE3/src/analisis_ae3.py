"""Transformaciones, tablas y exportaciones reproducibles de AE3.

La ejecución principal y las interpretaciones se presentan en el notebook.
Este módulo no modifica AE2 ni descarga fuentes externas adicionales.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

DATASET_ID = "t22000t/bike-sharing-tabular"
REVISION = "6b645e0cedbc5208fcca11ac94544b088478bf61"
CONFIGURACION = "default"
SPLIT = "train"
TIPOS_DIA = ["Laborable", "No laborable"]
FRANJAS = ["00 a 05", "06 a 11", "12 a 17", "18 a 23"]
PREGUNTAS = [
    {"id": "P1", "pregunta": "¿Cómo varían el promedio y la mediana de alquileres por hora entre días laborables y no laborables?", "variables": "hora, tipo_dia, alquileres_total", "detalle": "hora × tipo de día (48 filas)", "resultado": "Perfil horario con media, mediana, cantidad de observaciones y cobertura."},
    {"id": "P2", "pregunta": "¿Qué franjas de seis horas concentran más alquileres dentro de cada tipo de día?", "variables": "franja_horaria, orden_franja, tipo_dia, alquileres_total", "detalle": "franja de seis horas × tipo de día (8 filas)", "resultado": "Totales, participación dentro del tipo de día y promedio por hora registrada."},
    {"id": "P3", "pregunta": "¿Se mantienen los horarios de mayor promedio al separar 2011 y 2012 para cada tipo de día?", "variables": "anio, hora, tipo_dia, alquileres_total", "detalle": "año × hora × tipo de día (96 filas)", "resultado": "Comparación anual de perfiles horarios, máximos y cobertura."},
]
DICCIONARIO = [
    ("fecha", "Fecha del registro; dteday interpretado con formato AAAA-MM-DD.", "Fecha", "P1 P2 P3 y cobertura"),
    ("hora", "Hora original hr, entero entre 0 y 23.", "Hora del día", "P1 P3"),
    ("es_laborable", "workingday convertido a booleano; True si no es fin de semana ni festivo.", "True o False", "P1 P2 P3"),
    ("alquileres_total", "Conteo original cnt en una hora del sistema.", "Alquileres por registro horario", "P1 P2 P3"),
    ("alquileres_ocasionales", "Conteo original casual; no representa personas únicas.", "Alquileres por registro horario", "Comprobar el total"),
    ("alquileres_registrados", "Conteo original registered; no representa personas únicas.", "Alquileres por registro horario", "Comprobar el total"),
    ("fecha_hora", "fecha + hora expresada en horas; sin asignar zona horaria no documentada.", "Fecha y hora sin zona", "Clave única y cobertura"),
    ("anio", "Año calendario extraído de fecha; se contrasta con yr + 2011.", "Año", "P3"),
    ("tipo_dia", "Etiqueta de es_laborable: Laborable o No laborable.", "Categoría", "P1 P2 P3 y leyendas AE4"),
    ("orden_franja", "División entera hora // 6; códigos de 0 a 3.", "Código ordinal", "Orden de P2 y eje AE4"),
    ("franja_horaria", "Etiqueta de orden_franja: 00 a 05, 06 a 11, 12 a 17, 18 a 23.", "Intervalo de seis horas", "P2"),
]


def huella_dataframe(df: pd.DataFrame) -> str:
    esquema = json.dumps([(str(c), str(t)) for c, t in df.dtypes.items()], ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(pd.util.hash_pandas_object(df, index=True).to_numpy().tobytes() + esquema).hexdigest()


def calidad_original(df: pd.DataFrame) -> pd.DataFrame:
    fechas = pd.to_datetime(df["dteday"], format="%Y-%m-%d", errors="coerce")
    dia = fechas.dt.dayofweek
    controles = {
        "Celdas nulas en las 17 columnas": int(df.isna().sum().sum()),
        "Fechas no interpretables": int(fechas.isna().sum()),
        "Filas completas duplicadas": int(df.duplicated().sum()),
        "Duplicados fecha y hora": int(df.duplicated(["dteday", "hr"]).sum()),
        "Horas fuera de 0 a 23": int((~df["hr"].between(0, 23)).sum()),
        "Códigos workingday fuera de 0 y 1": int((~df["workingday"].isin([0, 1])).sum()),
        "Conteos negativos": int(df[["cnt", "casual", "registered"]].lt(0).any(axis=1).sum()),
        "Discrepancias cnt y componentes": int(df["cnt"].ne(df["casual"] + df["registered"]).sum()),
        "Año codificado distinto de la fecha": int(df["yr"].ne(fechas.dt.year - 2011).sum()),
        "Mes codificado distinto de la fecha": int(df["mnth"].ne(fechas.dt.month).sum()),
        "Día de semana distinto de la fecha": int(df["weekday"].ne((dia + 1) % 7).sum()),
        "Tipo de día inconsistente con fecha y holiday": int(df["workingday"].ne(((dia < 5) & df["holiday"].eq(0)).astype(int)).sum()),
    }
    return pd.DataFrame([{"control": k, "incidencias": v, "tratamiento": "Conservar; no se detectan incidencias" if v == 0 else "Detener y revisar antes de transformar"} for k, v in controles.items()])


def preparar(df_original: pd.DataFrame):
    huella_antes = huella_dataframe(df_original)
    controles = calidad_original(df_original)
    if controles["incidencias"].sum():
        raise ValueError("Hay incidencias en los controles de calidad; deben revisarse, no eliminarse automáticamente.")
    seleccion = ["dteday", "hr", "workingday", "cnt", "casual", "registered"]
    df = df_original[seleccion].copy(deep=True).rename(columns={
        "dteday": "fecha", "hr": "hora", "workingday": "es_laborable", "cnt": "alquileres_total",
        "casual": "alquileres_ocasionales", "registered": "alquileres_registrados",
    })
    df["fecha"] = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="raise")
    df["es_laborable"] = df["es_laborable"].astype(bool)
    df["fecha_hora"] = df["fecha"] + pd.to_timedelta(df["hora"], unit="h")
    df["anio"] = df["fecha"].dt.year.astype("int64")
    df["tipo_dia"] = pd.Categorical(df["es_laborable"].map({True: "Laborable", False: "No laborable"}), categories=TIPOS_DIA, ordered=True)
    df["orden_franja"] = (df["hora"] // 6).astype("int64")
    df["franja_horaria"] = pd.Categorical(df["orden_franja"].map(dict(enumerate(FRANJAS))), categories=FRANJAS, ordered=True)
    assert len(df) == len(df_original)
    assert df["alquileres_total"].sum() == df_original["cnt"].sum()
    assert huella_dataframe(df_original) == huella_antes, "El original fue modificado."
    assert not df.isna().any().any()
    assert df["fecha_hora"].is_unique

    # Cuadrícula auxiliar de cobertura. No se incorpora al dataset ni imputa conteos.
    calendario = pd.DataFrame({"fecha_hora": pd.date_range(df["fecha"].min(), df["fecha"].max() + pd.Timedelta(hours=23), freq="h")})
    calendario["fecha"] = calendario["fecha_hora"].dt.normalize()
    clasificacion = df.groupby("fecha", observed=True)["es_laborable"]
    assert clasificacion.nunique().eq(1).all()
    assert df["fecha"].nunique() == calendario["fecha"].nunique(), "Hay días enteros sin clasificación observada."
    calendario["es_laborable"] = calendario["fecha"].map(clasificacion.first())
    assert not calendario["es_laborable"].isna().any()
    calendario["tipo_dia"] = pd.Categorical(calendario["es_laborable"].map({True: "Laborable", False: "No laborable"}), categories=TIPOS_DIA, ordered=True)
    calendario["hora"] = calendario["fecha_hora"].dt.hour
    calendario["anio"] = calendario["fecha_hora"].dt.year
    calendario["orden_franja"] = calendario["hora"] // 6
    calendario["franja_horaria"] = pd.Categorical(calendario["orden_franja"].map(dict(enumerate(FRANJAS))), categories=FRANJAS, ordered=True)
    calendario["tiene_registro"] = calendario["fecha_hora"].isin(df["fecha_hora"])
    cobertura = calendario.groupby(["anio", "tipo_dia"], observed=True).agg(horas_esperadas=("fecha_hora", "size"), horas_observadas=("tiene_registro", "sum")).reset_index()
    cobertura["horas_sin_registro"] = cobertura["horas_esperadas"] - cobertura["horas_observadas"]
    cobertura["cobertura_pct"] = cobertura["horas_observadas"] / cobertura["horas_esperadas"] * 100

    excluidas = [c for c in df_original if c not in seleccion]
    n = len(df)
    bitacora = pd.DataFrame([
        ("Selección de seis variables fuente", n, "Se excluyen 11 columnas del DataFrame de trabajo, no filas: " + ", ".join(excluidas) + ". yr y mnth se usan antes como controles. El original completo se conserva en memoria."),
        ("Nombres descriptivos en español", n, "Se renombran seis columnas sin alterar sus valores."),
        ("Fecha de texto a datetime64", n, "dteday con formato %Y-%m-%d; errores=raise. No se inventa zona horaria."),
        ("Indicador laborable de entero a bool", n, "0 a False y 1 a True tras comprobar el dominio."),
        ("Cinco variables derivadas", n, "fecha_hora, anio, tipo_dia, orden_franja y franja_horaria; todas con regla explícita."),
        ("Nulos, duplicados e inconsistencias", 0, "No se eliminan registros, no se imputan ni reemplazan valores. Los ceros de controles son ausencia de incidencias."),
        ("Horas sin fila en calendario", int((~calendario["tiene_registro"]).sum()), "Se contabilizan como ausencias, no se agregan al dataset y no equivalen a cero alquileres. Cuadrícula nominal de 24 horas; sin zona ni ajuste de horario de verano no documentados."),
        ("Humedad igual a cero en el original", int(df_original["hum"].eq(0).sum()), "Se conserva el original. La humedad no se selecciona por no aportar a las preguntas y por requerir verificación; también se excluyen las demás variables meteorológicas."),
    ], columns=["operacion", "registros_afectados_o_incidencias", "regla_y_justificacion"])
    comparacion = pd.DataFrame([
        {"version": "Original AE2", "filas": len(df_original), "columnas": len(df_original.columns), "celdas_nulas": int(df_original.isna().sum().sum()), "total_alquileres": int(df_original["cnt"].sum())},
        {"version": "Preparado AE3", "filas": len(df), "columnas": len(df.columns), "celdas_nulas": int(df.isna().sum().sum()), "total_alquileres": int(df["alquileres_total"].sum())},
    ])
    tipos = pd.concat([
        pd.DataFrame({"version": "Original AE2", "variable": df_original.columns, "tipo": df_original.dtypes.astype(str).to_numpy(), "nulos": df_original.isna().sum().to_numpy()}),
        pd.DataFrame({"version": "Preparado AE3", "variable": df.columns, "tipo": df.dtypes.astype(str).to_numpy(), "nulos": df.isna().sum().to_numpy()}),
    ], ignore_index=True)
    diccionario = pd.DataFrame([{"variable": v, "significado_o_regla": s, "tipo_pandas": str(df[v].dtype), "unidad_o_codigos": u, "utilidad": f} for v, s, u, f in DICCIONARIO])
    return df, calendario, {"controles_calidad": controles, "comparacion_antes_despues": comparacion, "tipos_y_nulos_antes_despues": tipos, "bitacora_transformaciones": bitacora, "diccionario_variables": diccionario, "cobertura_por_anio_tipo": cobertura}


def tabla_grupos(df, calendario, claves):
    tabla = df.groupby(claves, observed=True).agg(
        horas_observadas=("alquileres_total", "size"),
        alquileres_total=("alquileres_total", "sum"),
        promedio_alquileres_por_hora=("alquileres_total", "mean"),
        mediana_alquileres_por_hora=("alquileres_total", "median"),
    )
    esperadas = calendario.groupby(claves, observed=True).size()
    tabla["horas_esperadas"] = esperadas.reindex(tabla.index)
    assert tabla["horas_esperadas"].notna().all()
    tabla["horas_sin_registro"] = tabla["horas_esperadas"] - tabla["horas_observadas"]
    assert tabla["horas_sin_registro"].ge(0).all()
    tabla["cobertura_pct"] = tabla["horas_observadas"] / tabla["horas_esperadas"] * 100
    assert tabla["horas_observadas"].sum() == len(df)
    assert tabla["alquileres_total"].sum() == df["alquileres_total"].sum()
    return tabla.reset_index()


def responder(df, calendario):
    p1 = tabla_grupos(df, calendario, ["tipo_dia", "hora"])
    p2 = tabla_grupos(df, calendario, ["tipo_dia", "orden_franja", "franja_horaria"])
    denominador = p2.groupby("tipo_dia", observed=True)["alquileres_total"].transform("sum")
    p2["participacion_alquileres_pct"] = p2["alquileres_total"] / denominador * 100
    p3 = tabla_grupos(df, calendario, ["anio", "tipo_dia", "hora"])
    p3["rango_promedio"] = p3.groupby(["anio", "tipo_dia"], observed=True)["promedio_alquileres_por_hora"].rank(method="min", ascending=False).astype("int64")
    assert (len(p1), len(p2), len(p3)) == (48, 8, 96)
    assert p2.groupby("tipo_dia", observed=True)["participacion_alquileres_pct"].sum().sub(100).abs().lt(1e-10).all()
    assert (p3["rango_promedio"].eq(1).groupby([p3["anio"], p3["tipo_dia"]], observed=True).sum() >= 1).all()
    # Comprobación independiente por filtros, sin reutilizar la agrupación.
    for _, r in p1.iterrows():
        x = df.loc[df["hora"].eq(r["hora"]) & df["tipo_dia"].eq(r["tipo_dia"]), "alquileres_total"]
        assert abs(float(x.mean()) - r["promedio_alquileres_por_hora"]) < 1e-10
        assert float(x.median()) == r["mediana_alquileres_por_hora"]
    return {"p1_perfil_horario": p1, "p2_franjas": p2, "p3_perfil_anual": p3}


def interpretar(tablas):
    p1, p2, p3 = (tablas[k] for k in ("p1_perfil_horario", "p2_franjas", "p3_perfil_anual"))
    textos = {}
    partes = []
    for tipo in TIPOS_DIA:
        grupo = p1[p1["tipo_dia"].eq(tipo)]
        maximo = grupo["promedio_alquileres_por_hora"].max()
        for _, r in grupo[grupo["promedio_alquileres_por_hora"].eq(maximo)].iterrows():
            partes.append(f"{tipo}: el mayor promedio corresponde a las {int(r['hora']):02d}:00, con {r['promedio_alquileres_por_hora']:.2f} alquileres por hora registrada, mediana {r['mediana_alquileres_por_hora']:.1f} y {int(r['horas_observadas'])} observaciones (cobertura {r['cobertura_pct']:.2f} %).")
    textos["P1"] = " ".join(partes) + " Son franjas para revisar en el escenario operativo, sin inferir faltantes de bicicletas ni causalidad. Las medias describen horas observadas y no se ajustan por clima o año."
    partes = []
    for tipo in TIPOS_DIA:
        grupo = p2[p2["tipo_dia"].eq(tipo)]
        for _, r in grupo[grupo["alquileres_total"].eq(grupo["alquileres_total"].max())].iterrows():
            partes.append(f"{tipo}: la franja {r['franja_horaria']} reúne {int(r['alquileres_total']):,} alquileres, {r['participacion_alquileres_pct']:.2f} % del total de ese tipo de día y un promedio de {r['promedio_alquileres_por_hora']:.2f} por hora registrada.")
    textos["P2"] = " ".join(partes) + " La participación usa como denominador los alquileres del mismo tipo de día, no los de todo el dataset. Las franjas tienen seis horas nominales; se informa cobertura para reconocer ausencias."
    partes = []
    for (anio, tipo), g in p3.groupby(["anio", "tipo_dia"], observed=True):
        picos = g[g["rango_promedio"].eq(1)]
        partes.append(f"{int(anio)}, {tipo}: máximo a las " + ", ".join(f"{int(r['hora']):02d}:00 ({r['promedio_alquileres_por_hora']:.2f} alquileres por hora registrada)" for _, r in picos.iterrows()) + ".")
    for tipo in TIPOS_DIA:
        a = set(p3.loc[p3["anio"].eq(2011) & p3["tipo_dia"].eq(tipo) & p3["rango_promedio"].eq(1), "hora"])
        b = set(p3.loc[p3["anio"].eq(2012) & p3["tipo_dia"].eq(tipo) & p3["rango_promedio"].eq(1), "hora"])
        partes.append(f"{tipo}: " + ("el conjunto de horas máximas coincide entre ambos años." if a == b else "el conjunto de horas máximas cambia entre ambos años."))
    textos["P3"] = " ".join(partes) + " El máximo se selecciona por la media; la tabla conserva todas las horas y los empates. Esta comparación histórica no demuestra una tendencia futura ni explica sus causas."
    return textos


def resumen_final(df, originales, tablas, controles):
    lineas = ["AE3 RESUMEN DEL DATAFRAME TRANSFORMADO Y ENRIQUECIDO", f"Dataset: {DATASET_ID}", f"Revision: {REVISION}", f"Configuracion: {CONFIGURACION}; split: {SPLIT}", "Muestra: no. Se conservan todas las filas; se seleccionan variables pertinentes.", f"Original: {originales.shape[0]} filas y {originales.shape[1]} columnas", f"Filas: {len(df)}", f"Columnas: {len(df.columns)}", "", "COLUMNAS TIPOS Y NULOS", "Nota: nulos=0 significa ausencia de celdas vacias, no que todos los valores sean cero.", "variable | tipo_pandas | nulos"]
    lineas += [f"{c} | {df[c].dtype} | {int(df[c].isna().sum())}" for c in df]
    lineas += ["", "ESTADISTICAS NUMERICAS", "Incluye codigos de hora, anio y orden_franja solo como rangos; no representan cantidades de negocio.", df.select_dtypes(include="number").describe().to_string(float_format=lambda x: f"{x:.6f}"), "", "CATEGORIAS", "tipo_dia:", df["tipo_dia"].value_counts(sort=False).to_string(), "franja_horaria:", df["franja_horaria"].value_counts(sort=False).to_string(), "", f"Fecha inicial: {df['fecha'].min():%Y-%m-%d}", f"Fecha final: {df['fecha'].max():%Y-%m-%d}", f"Fechas distintas: {df['fecha'].nunique()}", f"Total alquileres: {int(df['alquileres_total'].sum())}", f"Total ocasionales: {int(df['alquileres_ocasionales'].sum())}", f"Total registrados: {int(df['alquileres_registrados'].sum())}", f"Horas sin registro en cuadricula nominal: {int(controles['cobertura_por_anio_tipo']['horas_sin_registro'].sum())}", "No se imputan horas ausentes como cero. No se asigna zona horaria no documentada.", "", "TABLAS DE RESPUESTA"]
    for nombre, t in tablas.items():
        lineas += [f"{nombre}: {len(t)} filas; total alquileres = {int(t['alquileres_total'].sum())}"]
    lineas += ["Participacion P2: suma 100 % dentro de cada tipo de dia antes del redondeo de presentacion.", "", "dataframe.info"]
    from io import StringIO
    buffer = StringIO()
    df.info(buf=buffer, show_counts=True)
    lineas.append(buffer.getvalue())
    return "\n".join(lineas) + "\n"


def exportar_y_verificar(raiz, original, preparado, tablas, controles, respuestas):
    raiz = Path(raiz)
    base = raiz / "AE3"
    datos, resultados = base / "datos", base / "resultados"
    datos.mkdir(parents=True, exist_ok=True)
    resultados.mkdir(parents=True, exist_ok=True)
    exportaciones = {"datos/dataset_preparado.csv": preparado, **{f"resultados/{k}.csv": v for k, v in tablas.items()}, **{f"resultados/{k}.csv": v for k, v in controles.items()}}
    manifiesto = []
    for ruta, df in exportaciones.items():
        path = base / ruta
        df.to_csv(path, index=False, encoding="utf-8", lineterminator="\n", date_format="%Y-%m-%d %H:%M:%S")
        leido = pd.read_csv(path)
        # Comparar todas las celdas al releer, incluidas categorias y fechas.
        esperado = df.copy()
        for c in esperado:
            if isinstance(esperado[c].dtype, pd.CategoricalDtype):
                esperado[c] = esperado[c].astype("str")
            elif pd.api.types.is_datetime64_any_dtype(esperado[c]):
                esperado[c] = esperado[c].dt.strftime("%Y-%m-%d %H:%M:%S")
        assert_frame_equal(esperado.reset_index(drop=True), leido, check_dtype=False, check_categorical=False, rtol=1e-12, atol=1e-10)
        manifiesto.append({"ruta": f"AE3/{ruta}", "filas": len(df), "columnas": len(df.columns), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    resumen = resumen_final(preparado, original, tablas, controles)
    ruta_txt = resultados / "resumen_dataframe_transformado.txt"
    ruta_txt.write_text(resumen, encoding="utf-8", newline="\n")
    assert ruta_txt.read_text(encoding="utf-8") == resumen
    assert all(f"{c} | {preparado[c].dtype} | {int(preparado[c].isna().sum())}" in resumen for c in preparado)
    manifiesto.append({"ruta": "AE3/resultados/resumen_dataframe_transformado.txt", "sha256": hashlib.sha256(ruta_txt.read_bytes()).hexdigest()})
    reporte = {"dataset_id": DATASET_ID, "revision": REVISION, "configuracion": CONFIGURACION, "split": SPLIT, "fecha_desarrollo": "2026-11-02", "filas_originales": len(original), "columnas_originales": len(original.columns), "filas_preparadas": len(preparado), "columnas_preparadas": len(preparado.columns), "filas_eliminadas": 0, "nulos_originales": int(original.isna().sum().sum()), "nulos_preparados": int(preparado.isna().sum().sum()), "alquileres_total": int(preparado["alquileres_total"].sum()), "huella_original": huella_dataframe(original), "huella_preparado": huella_dataframe(preparado), "horas_sin_registro": int(controles["cobertura_por_anio_tipo"]["horas_sin_registro"].sum()), "verificaciones": {"original_sin_modificar": True, "csv_releidos_comparados_celda_a_celda": True, "totales_conservados_en_tres_tablas": True, "porcentajes_p2_suman_100_por_tipo": True, "resumen_releido_coincide": True}, "porcentajes_p2_por_tipo": {str(k): float(v) for k,v in tablas['p2_franjas'].groupby('tipo_dia',observed=True)['participacion_alquileres_pct'].sum().items()}, "respuestas": respuestas, "archivos": manifiesto}
    (resultados / "validaciones.json").write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return pd.DataFrame(manifiesto), reporte
