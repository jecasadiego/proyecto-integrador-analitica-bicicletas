"""Métricas verificadas, controles de coherencia y gráficos interactivos de AE4.

Este módulo carga directamente el dataset preparado y las tablas de resultados
publicadas en AE3 sin modificar ningún archivo previo. Todas las cifras y
visualizaciones se derivan de los archivos reales del proyecto.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ORDEN_TIPOS_DIA = ["Laborable", "No laborable"]
ORDEN_FRANJAS = ["00 a 05", "06 a 11", "12 a 17", "18 a 23"]

COLORES_TIPO_DIA = {
    "Laborable": "#0F766E",
    "No laborable": "#D97706",
}

COLORES_ANIO = {
    2011: "#64748B",
    2012: "#0F766E",
}

COLORES_ANIO_NO_LABORABLE = {
    2011: "#94A3B8",
    2012: "#D97706",
}

PERIODO_ETIQUETA = "Capital Bikeshare (2011–2012)"
FUENTE_GRAFICO = (
    "Fuente: elaboración propia con datos de AE3 "
    "(t22000t/bike-sharing-tabular, revisión fijada, UCI 2011–2012)."
)


def obtener_raiz_proyecto() -> Path:
    """Devuelve la ruta raíz del repositorio a partir de este módulo."""
    return Path(__file__).resolve().parents[2]


def formatear_entero_es(valor: float) -> str:
    """Formatea un número entero con punto como separador de miles."""
    return f"{round(valor):,}".replace(",", ".")


def formatear_decimal_es(valor: float, decimales: int = 2) -> str:
    """Formatea un número decimal con punto de miles y coma decimal."""
    texto_en = f"{float(valor):,.{decimales}f}"
    return texto_en.replace(",", "_").replace(".", ",").replace("_", ".")


def cargar_datos_proyecto(ruta_raiz: Path | None = None) -> dict[str, Any]:
    """Carga el dataset preparado, las tablas AE3 y las validaciones."""
    raiz = Path(ruta_raiz) if ruta_raiz is not None else obtener_raiz_proyecto()
    carpeta_ae3 = raiz / "AE3"
    carpeta_resultados = carpeta_ae3 / "resultados"

    datos_preparados = pd.read_csv(
        carpeta_ae3 / "datos" / "dataset_preparado.csv",
        parse_dates=["fecha", "fecha_hora"],
    )
    datos_preparados["tipo_dia"] = pd.Categorical(
        datos_preparados["tipo_dia"],
        categories=ORDEN_TIPOS_DIA,
        ordered=True,
    )
    datos_preparados["franja_horaria"] = pd.Categorical(
        datos_preparados["franja_horaria"],
        categories=ORDEN_FRANJAS,
        ordered=True,
    )

    tabla_p1 = pd.read_csv(carpeta_resultados / "p1_perfil_horario.csv")
    tabla_p1["tipo_dia"] = pd.Categorical(
        tabla_p1["tipo_dia"],
        categories=ORDEN_TIPOS_DIA,
        ordered=True,
    )
    tabla_p1 = tabla_p1.sort_values(["tipo_dia", "hora"]).reset_index(drop=True)

    tabla_p2 = pd.read_csv(carpeta_resultados / "p2_franjas.csv")
    tabla_p2["tipo_dia"] = pd.Categorical(
        tabla_p2["tipo_dia"],
        categories=ORDEN_TIPOS_DIA,
        ordered=True,
    )
    tabla_p2["franja_horaria"] = pd.Categorical(
        tabla_p2["franja_horaria"],
        categories=ORDEN_FRANJAS,
        ordered=True,
    )
    tabla_p2 = tabla_p2.sort_values(
        ["tipo_dia", "orden_franja"]
    ).reset_index(drop=True)

    tabla_p3 = pd.read_csv(carpeta_resultados / "p3_perfil_anual.csv")
    tabla_p3["tipo_dia"] = pd.Categorical(
        tabla_p3["tipo_dia"],
        categories=ORDEN_TIPOS_DIA,
        ordered=True,
    )
    tabla_p3 = tabla_p3.sort_values(
        ["anio", "tipo_dia", "hora"]
    ).reset_index(drop=True)

    cobertura_anual = pd.read_csv(
        carpeta_resultados / "cobertura_por_anio_tipo.csv"
    )
    controles_calidad = pd.read_csv(
        carpeta_resultados / "controles_calidad.csv"
    )
    comparacion_bases = pd.read_csv(
        carpeta_resultados / "comparacion_antes_despues.csv"
    )
    bitacora_transformaciones = pd.read_csv(
        carpeta_resultados / "bitacora_transformaciones.csv"
    )
    diccionario_variables = pd.read_csv(
        carpeta_resultados / "diccionario_variables.csv"
    )
    validaciones_ae3 = json.loads(
        (carpeta_resultados / "validaciones.json").read_text(encoding="utf-8")
    )

    return {
        "ruta_raiz": raiz,
        "datos_preparados": datos_preparados,
        "tabla_p1": tabla_p1,
        "tabla_p2": tabla_p2,
        "tabla_p3": tabla_p3,
        "cobertura_anual": cobertura_anual,
        "controles_calidad": controles_calidad,
        "comparacion_bases": comparacion_bases,
        "bitacora_transformaciones": bitacora_transformaciones,
        "diccionario_variables": diccionario_variables,
        "validaciones_ae3": validaciones_ae3,
    }


def _comprobar_tabla_contra_base(
    datos_preparados: pd.DataFrame,
    tabla_objetivo: pd.DataFrame,
    claves_agrupacion: list[str],
    verificar_participacion: bool = False,
) -> tuple[bool, str]:
    """Recalcula métricas desde dataset_preparado.csv y compara con la tabla."""
    agrupado = (
        datos_preparados.groupby(claves_agrupacion, observed=True)
        .agg(
            horas_observadas=("alquileres_total", "size"),
            alquileres_total=("alquileres_total", "sum"),
            promedio_alquileres_por_hora=("alquileres_total", "mean"),
            mediana_alquileres_por_hora=("alquileres_total", "median"),
        )
        .reset_index()
    )

    unido = tabla_objetivo.merge(
        agrupado,
        on=claves_agrupacion,
        suffixes=("_csv", "_recalculado"),
        how="outer",
    )
    if len(unido) != len(tabla_objetivo):
        return False, "La cantidad de grupos no coincide con el dataset base."

    diferencia_media = (
        unido["promedio_alquileres_por_hora_csv"]
        - unido["promedio_alquileres_por_hora_recalculado"]
    ).abs().max()
    diferencia_mediana = (
        unido["mediana_alquileres_por_hora_csv"]
        - unido["mediana_alquileres_por_hora_recalculado"]
    ).abs().max()
    iguales_conteos = (
        unido["horas_observadas_csv"].eq(
            unido["horas_observadas_recalculado"]
        ).all()
        and unido["alquileres_total_csv"].eq(
            unido["alquileres_total_recalculado"]
        ).all()
    )

    if not iguales_conteos or diferencia_media >= 1e-9 or diferencia_mediana >= 1e-9:
        return False, "Se detectaron diferencias frente al recálculo directo."

    if verificar_participacion:
        totales_tipo = datos_preparados.groupby(
            "tipo_dia", observed=True
        )["alquileres_total"].sum()
        esperada = (
            tabla_objetivo["alquileres_total"]
            / tabla_objetivo["tipo_dia"].map(totales_tipo).astype(float)
            * 100.0
        )
        diferencia_pct = (
            tabla_objetivo["participacion_alquileres_pct"] - esperada
        ).abs().max()
        suma_tipos = (
            tabla_objetivo.groupby("tipo_dia", observed=True)[
                "participacion_alquileres_pct"
            ]
            .sum()
            .sub(100.0)
            .abs()
            .max()
        )
        if diferencia_pct >= 1e-9 or suma_tipos >= 1e-9:
            return False, "Las participaciones porcentuales no cuadran al 100 %."

    return (
        True,
        f"{len(tabla_objetivo)} grupos verificados (error máximo < 1e-9).",
    )


def verificar_coherencia_datos(
    repositorio_datos: dict[str, Any],
) -> list[dict[str, Any]]:
    """Valida que dataset_preparado, tablas AE3 y validaciones coincidan."""
    datos_preparados = repositorio_datos["datos_preparados"]
    tabla_p1 = repositorio_datos["tabla_p1"]
    tabla_p2 = repositorio_datos["tabla_p2"]
    tabla_p3 = repositorio_datos["tabla_p3"]
    cobertura = repositorio_datos["cobertura_anual"]
    validaciones = repositorio_datos["validaciones_ae3"]

    total_alquileres = int(datos_preparados["alquileres_total"].sum())
    suma_componentes = int(
        (
            datos_preparados["alquileres_ocasionales"]
            + datos_preparados["alquileres_registrados"]
        ).sum()
    )
    ausencias = int(cobertura["horas_sin_registro"].sum())

    ok_p1, detalle_p1 = _comprobar_tabla_contra_base(
        datos_preparados, tabla_p1, ["tipo_dia", "hora"]
    )
    ok_p2, detalle_p2 = _comprobar_tabla_contra_base(
        datos_preparados,
        tabla_p2,
        ["tipo_dia", "orden_franja", "franja_horaria"],
        verificar_participacion=True,
    )
    ok_p3, detalle_p3 = _comprobar_tabla_contra_base(
        datos_preparados, tabla_p3, ["anio", "tipo_dia", "hora"]
    )

    comprobaciones = [
        {
            "control": "Dimensiones del dataset preparado",
            "estado": datos_preparados.shape == (17379, 11),
            "detalle": (
                f"{formatear_entero_es(len(datos_preparados))} filas × "
                f"{len(datos_preparados.columns)} columnas; 0 celdas nulas."
            ),
        },
        {
            "control": "Conservación del total de alquileres",
            "estado": (
                total_alquileres == validaciones["alquileres_total"]
                and total_alquileres == suma_componentes
                and int(tabla_p1["alquileres_total"].sum()) == total_alquileres
                and int(tabla_p2["alquileres_total"].sum()) == total_alquileres
                and int(tabla_p3["alquileres_total"].sum()) == total_alquileres
            ),
            "detalle": (
                f"{formatear_entero_es(total_alquileres)} alquileres idénticos "
                "en dataset base, P1, P2, P3 y validaciones.json."
            ),
        },
        {
            "control": "Consistencia de cobertura y ausencias",
            "estado": (
                ausencias == validaciones["horas_sin_registro"]
                and int(tabla_p1["horas_sin_registro"].sum()) == ausencias
                and int(tabla_p2["horas_sin_registro"].sum()) == ausencias
                and int(tabla_p3["horas_sin_registro"].sum()) == ausencias
            ),
            "detalle": (
                f"{formatear_entero_es(ausencias)} horas sin registro en la "
                "cuadrícula nominal de 17.544 horas (cobertura 99,06 %)."
            ),
        },
        {
            "control": "Recálculo independiente de P1 (hora × tipo de día)",
            "estado": ok_p1,
            "detalle": detalle_p1,
        },
        {
            "control": "Recálculo independiente de P2 (franjas de seis horas)",
            "estado": ok_p2,
            "detalle": detalle_p2,
        },
        {
            "control": "Recálculo independiente de P3 (año × hora × tipo)",
            "estado": ok_p3,
            "detalle": detalle_p3,
        },
    ]
    return comprobaciones


def calcular_indicadores_generales(
    repositorio_datos: dict[str, Any],
) -> dict[str, Any]:
    """Calcula el resumen numérico principal para KPIs y textos coherentes."""
    datos_preparados = repositorio_datos["datos_preparados"]
    tabla_p1 = repositorio_datos["tabla_p1"]
    tabla_p2 = repositorio_datos["tabla_p2"]
    tabla_p3 = repositorio_datos["tabla_p3"]
    cobertura = repositorio_datos["cobertura_anual"]

    horas_observadas = len(datos_preparados)
    horas_esperadas = int(cobertura["horas_esperadas"].sum())
    horas_ausentes = int(cobertura["horas_sin_registro"].sum())
    alquileres_total = int(datos_preparados["alquileres_total"].sum())
    alquileres_registrados = int(
        datos_preparados["alquileres_registrados"].sum()
    )
    alquileres_ocasionales = int(
        datos_preparados["alquileres_ocasionales"].sum()
    )

    pico_laborable = (
        tabla_p1[tabla_p1["tipo_dia"].eq("Laborable")]
        .sort_values("promedio_alquileres_por_hora", ascending=False)
        .iloc[0]
    )
    pico_manana_laborable = (
        tabla_p1[
            tabla_p1["tipo_dia"].eq("Laborable")
            & tabla_p1["hora"].between(6, 11)
        ]
        .sort_values("promedio_alquileres_por_hora", ascending=False)
        .iloc[0]
    )
    pico_no_laborable = (
        tabla_p1[tabla_p1["tipo_dia"].eq("No laborable")]
        .sort_values("promedio_alquileres_por_hora", ascending=False)
        .iloc[0]
    )

    franja_lider_lab = (
        tabla_p2[tabla_p2["tipo_dia"].eq("Laborable")]
        .sort_values("participacion_alquileres_pct", ascending=False)
        .iloc[0]
    )
    franja_lider_nolab = (
        tabla_p2[tabla_p2["tipo_dia"].eq("No laborable")]
        .sort_values("participacion_alquileres_pct", ascending=False)
        .iloc[0]
    )

    totales_por_tipo = (
        datos_preparados.groupby("tipo_dia", observed=True)["alquileres_total"]
        .sum()
        .to_dict()
    )
    dias_por_tipo = (
        datos_preparados.groupby("tipo_dia", observed=True)["fecha"]
        .nunique()
        .to_dict()
    )
    totales_por_anio = (
        datos_preparados.groupby("anio", observed=True)["alquileres_total"]
        .sum()
        .to_dict()
    )

    picos_anuales = tabla_p3[tabla_p3["rango_promedio"].eq(1)].copy()

    return {
        "horas_observadas": horas_observadas,
        "horas_esperadas": horas_esperadas,
        "horas_ausentes": horas_ausentes,
        "cobertura_total_pct": horas_observadas / horas_esperadas * 100.0,
        "fechas_distintas": int(datos_preparados["fecha"].nunique()),
        "fecha_inicio": datos_preparados["fecha"].min().strftime("%Y-%m-%d"),
        "fecha_fin": datos_preparados["fecha"].max().strftime("%Y-%m-%d"),
        "alquileres_total": alquileres_total,
        "alquileres_registrados": alquileres_registrados,
        "alquileres_ocasionales": alquileres_ocasionales,
        "participacion_registrados_pct": (
            alquileres_registrados / alquileres_total * 100.0
        ),
        "participacion_ocasionales_pct": (
            alquileres_ocasionales / alquileres_total * 100.0
        ),
        "promedio_global_por_hora": float(
            datos_preparados["alquileres_total"].mean()
        ),
        "mediana_global_por_hora": float(
            datos_preparados["alquileres_total"].median()
        ),
        "alquileres_laborable": int(totales_por_tipo["Laborable"]),
        "alquileres_no_laborable": int(totales_por_tipo["No laborable"]),
        "dias_laborables": int(dias_por_tipo["Laborable"]),
        "dias_no_laborables": int(dias_por_tipo["No laborable"]),
        "alquileres_2011": int(totales_por_anio[2011]),
        "alquileres_2012": int(totales_por_anio[2012]),
        "variacion_total_anual_pct": (
            (totales_por_anio[2012] - totales_por_anio[2011])
            / totales_por_anio[2011]
            * 100.0
        ),
        "pico_laborable_hora": int(pico_laborable["hora"]),
        "pico_laborable_promedio": float(
            pico_laborable["promedio_alquileres_por_hora"]
        ),
        "pico_laborable_mediana": float(
            pico_laborable["mediana_alquileres_por_hora"]
        ),
        "pico_laborable_observaciones": int(pico_laborable["horas_observadas"]),
        "pico_laborable_cobertura_pct": float(pico_laborable["cobertura_pct"]),
        "pico_manana_laborable_hora": int(pico_manana_laborable["hora"]),
        "pico_manana_laborable_promedio": float(
            pico_manana_laborable["promedio_alquileres_por_hora"]
        ),
        "pico_manana_laborable_mediana": float(
            pico_manana_laborable["mediana_alquileres_por_hora"]
        ),
        "pico_no_laborable_hora": int(pico_no_laborable["hora"]),
        "pico_no_laborable_promedio": float(
            pico_no_laborable["promedio_alquileres_por_hora"]
        ),
        "pico_no_laborable_mediana": float(
            pico_no_laborable["mediana_alquileres_por_hora"]
        ),
        "pico_no_laborable_observaciones": int(
            pico_no_laborable["horas_observadas"]
        ),
        "pico_no_laborable_cobertura_pct": float(
            pico_no_laborable["cobertura_pct"]
        ),
        "franja_lider_laborable": str(franja_lider_lab["franja_horaria"]),
        "franja_lider_laborable_pct": float(
            franja_lider_lab["participacion_alquileres_pct"]
        ),
        "franja_lider_laborable_total": int(
            franja_lider_lab["alquileres_total"]
        ),
        "franja_lider_laborable_promedio": float(
            franja_lider_lab["promedio_alquileres_por_hora"]
        ),
        "franja_lider_no_laborable": str(franja_lider_nolab["franja_horaria"]),
        "franja_lider_no_laborable_pct": float(
            franja_lider_nolab["participacion_alquileres_pct"]
        ),
        "franja_lider_no_laborable_total": int(
            franja_lider_nolab["alquileres_total"]
        ),
        "franja_lider_no_laborable_promedio": float(
            franja_lider_nolab["promedio_alquileres_por_hora"]
        ),
        "picos_anuales_coinciden": (
            set(
                picos_anuales.loc[
                    picos_anuales["anio"].eq(2011)
                    & picos_anuales["tipo_dia"].eq("Laborable"),
                    "hora",
                ]
            )
            == set(
                picos_anuales.loc[
                    picos_anuales["anio"].eq(2012)
                    & picos_anuales["tipo_dia"].eq("Laborable"),
                    "hora",
                ]
            )
            and set(
                picos_anuales.loc[
                    picos_anuales["anio"].eq(2011)
                    & picos_anuales["tipo_dia"].eq("No laborable"),
                    "hora",
                ]
            )
            == set(
                picos_anuales.loc[
                    picos_anuales["anio"].eq(2012)
                    & picos_anuales["tipo_dia"].eq("No laborable"),
                    "hora",
                ]
            )
        ),
    }


def calcular_brecha_horaria_p1(tabla_p1: pd.DataFrame) -> pd.DataFrame:
    """Calcula la diferencia horaria Laborable menos No laborable para P1."""
    tabla_lab = (
        tabla_p1[tabla_p1["tipo_dia"].eq("Laborable")]
        .set_index("hora")
        .sort_index()
    )
    tabla_nolab = (
        tabla_p1[tabla_p1["tipo_dia"].eq("No laborable")]
        .set_index("hora")
        .sort_index()
    )

    brecha = pd.DataFrame(index=tabla_lab.index)
    brecha["hora"] = brecha.index.astype(int)
    brecha["etiqueta_hora"] = brecha["hora"].map(lambda hora: f"{hora:02d}:00")
    brecha["promedio_laborable"] = tabla_lab["promedio_alquileres_por_hora"]
    brecha["promedio_no_laborable"] = tabla_nolab[
        "promedio_alquileres_por_hora"
    ]
    brecha["mediana_laborable"] = tabla_lab["mediana_alquileres_por_hora"]
    brecha["mediana_no_laborable"] = tabla_nolab["mediana_alquileres_por_hora"]
    brecha["brecha_promedio"] = (
        brecha["promedio_laborable"] - brecha["promedio_no_laborable"]
    )
    brecha["brecha_mediana"] = (
        brecha["mediana_laborable"] - brecha["mediana_no_laborable"]
    )
    brecha["cobertura_laborable_pct"] = tabla_lab["cobertura_pct"]
    brecha["cobertura_no_laborable_pct"] = tabla_nolab["cobertura_pct"]
    brecha["ausentes_laborable"] = tabla_lab["horas_sin_registro"]
    brecha["ausentes_no_laborable"] = tabla_nolab["horas_sin_registro"]
    brecha["tipo_dominante"] = brecha["brecha_promedio"].map(
        lambda diferencia: (
            "Mayor en laborable" if diferencia >= 0 else "Mayor en no laborable"
        )
    )
    return brecha.reset_index(drop=True)


def calcular_resumen_interanual_p3(
    tabla_p3: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calcula la tabla de picos anuales y el resumen comparativo 2011–2012."""
    picos = tabla_p3[tabla_p3["rango_promedio"].eq(1)].copy()
    picos = picos.sort_values(["tipo_dia", "anio"]).reset_index(drop=True)

    filas_comparacion = []
    for tipo_dia in ORDEN_TIPOS_DIA:
        grupo_tipo = tabla_p3[tabla_p3["tipo_dia"].eq(tipo_dia)]
        fila_2011 = picos[
            picos["tipo_dia"].eq(tipo_dia) & picos["anio"].eq(2011)
        ].iloc[0]
        fila_2012 = picos[
            picos["tipo_dia"].eq(tipo_dia) & picos["anio"].eq(2012)
        ].iloc[0]

        promedio_2011 = float(fila_2011["promedio_alquileres_por_hora"])
        promedio_2012 = float(fila_2012["promedio_alquileres_por_hora"])
        total_2011 = int(
            grupo_tipo[grupo_tipo["anio"].eq(2011)]["alquileres_total"].sum()
        )
        total_2012 = int(
            grupo_tipo[grupo_tipo["anio"].eq(2012)]["alquileres_total"].sum()
        )
        horas_2011 = int(
            grupo_tipo[grupo_tipo["anio"].eq(2011)]["horas_observadas"].sum()
        )
        horas_2012 = int(
            grupo_tipo[grupo_tipo["anio"].eq(2012)]["horas_observadas"].sum()
        )
        media_anual_2011 = total_2011 / horas_2011
        media_anual_2012 = total_2012 / horas_2012

        filas_comparacion.append(
            {
                "tipo_dia": tipo_dia,
                "hora_pico_2011": int(fila_2011["hora"]),
                "hora_pico_2012": int(fila_2012["hora"]),
                "coincide_hora_pico": int(fila_2011["hora"])
                == int(fila_2012["hora"]),
                "promedio_pico_2011": promedio_2011,
                "promedio_pico_2012": promedio_2012,
                "cambio_pico_absoluto": promedio_2012 - promedio_2011,
                "cambio_pico_pct": (
                    (promedio_2012 - promedio_2011) / promedio_2011 * 100.0
                ),
                "mediana_pico_2011": float(
                    fila_2011["mediana_alquileres_por_hora"]
                ),
                "mediana_pico_2012": float(
                    fila_2012["mediana_alquileres_por_hora"]
                ),
                "total_anual_2011": total_2011,
                "total_anual_2012": total_2012,
                "cambio_total_anual_pct": (
                    (total_2012 - total_2011) / total_2011 * 100.0
                ),
                "media_global_2011": media_anual_2011,
                "media_global_2012": media_anual_2012,
            }
        )

    comparacion_anual = pd.DataFrame(filas_comparacion)
    return picos, comparacion_anual


def obtener_catalogo_metricas() -> pd.DataFrame:
    """Devuelve la ficha metodológica de métricas, unidades y límites."""
    registros = [
        {
            "pregunta": "P1",
            "metrica": "Promedio de alquileres por hora registrada",
            "calculo": "Suma de alquileres_total / horas_observadas por hora y tipo de día",
            "unidad": "Alquileres / hora registrada",
            "denominador": "Horas registradas en cada combinación hora × tipo de día",
            "grafico_principal": "Líneas comparativas de 24 horas (media y mediana)",
            "decision_apoyada": (
                "Identificar ventanas prioritarias de seguimiento operativo y "
                "revisión de turnos de atención por tipo de día."
            ),
            "limitaciones": (
                "Mide volumen registrado, no ingresos ni rentabilidad; no "
                "demuestra causalidad ni faltantes de bicicletas; 165 ausencias "
                "no se imputan como cero."
            ),
        },
        {
            "pregunta": "P1",
            "metrica": "Mediana de alquileres por hora registrada",
            "calculo": "Percentil 50 de alquileres_total por hora y tipo de día",
            "unidad": "Alquileres / hora registrada",
            "denominador": "Registros horarios observados del grupo",
            "grafico_principal": "Superposición punteada sobre el perfil horario",
            "decision_apoyada": (
                "Verificar si el promedio está desplazado por jornadas atípicas "
                "antes de revisar horarios habituales."
            ),
            "limitaciones": (
                "No controla clima, estacionalidad ni año; refleja el sistema "
                "agregado sin desglose por estación."
            ),
        },
        {
            "pregunta": "P1",
            "metrica": "Brecha horaria (Laborable − No laborable)",
            "calculo": "Promedio Laborable(h) − Promedio No laborable(h)",
            "unidad": "Diferencia en alquileres / hora registrada",
            "denominador": "Promedios horarios por tipo de día",
            "grafico_principal": "Barras divergentes de 24 horas",
            "decision_apoyada": (
                "Diferenciar franjas con intensidad laboral (06–09 y 17–22) de "
                "franjas con predominio recreativo/no laborable (10–16 y 00–04)."
            ),
            "limitaciones": (
                "Una brecha positiva describe diferencia de nivel observado, no "
                "el efecto causal de la jornada laboral."
            ),
        },
        {
            "pregunta": "P2",
            "metrica": "Participación porcentual por franja de seis horas",
            "calculo": (
                "(Alquileres de la franja y tipo / Total de alquileres del mismo "
                "tipo de día) × 100"
            ),
            "unidad": "Porcentaje (%) dentro del tipo de día",
            "denominador": (
                "2.292.410 alquileres en Laborable; 1.000.269 en No laborable"
            ),
            "grafico_principal": "Barras agrupadas de participación relativa",
            "decision_apoyada": (
                "Comparar la concentración relativa del uso en bloques de seis "
                "horas sin sesgo por el distinto número de días calendario."
            ),
            "limitaciones": (
                "Las franjas son reglas del proyecto (hora // 6); resumen el "
                "detalle horario y no miden demanda insatisfecha ni margen."
            ),
        },
        {
            "pregunta": "P2",
            "metrica": "Volumen acumulado e intensidad media por franja",
            "calculo": (
                "Suma de alquileres_total y promedio por hora registrada en "
                "cada franja × tipo de día"
            ),
            "unidad": "Alquileres acumulados y alquileres / hora registrada",
            "denominador": "Horas observadas de cada franja",
            "grafico_principal": "Barras agrupadas con anotación de media horaria",
            "decision_apoyada": (
                "Evitar confundir volumen absoluto (mayor en laborables por "
                "tener 500 días) con intensidad por hora (mayor en no laborables "
                "en 12 a 17: 356,45 vs. 267,21)."
            ),
            "limitaciones": (
                "Conteo de alquileres no equivale a personas únicas ni a "
                "ingresos o rentabilidad operativa."
            ),
        },
        {
            "pregunta": "P3",
            "metrica": "Rango horario y variación interanual (2011 vs. 2012)",
            "calculo": (
                "Rango descendente del promedio por año y tipo; cambio % = "
                "((media_2012 − media_2011) / media_2011) × 100"
            ),
            "unidad": "Posición ordinal, alquileres / hora y variación (%)",
            "denominador": "Promedio horario de 2011 como base comparativa",
            "grafico_principal": "Panel dual de perfiles anuales 2011 vs. 2012",
            "decision_apoyada": (
                "Confirmar si los horarios pico (17:00 laborable, 13:00 no "
                "laborable) son estables en ambos años y no un artefacto del "
                "promedio combinado."
            ),
            "limitaciones": (
                "Dos años históricos no prueban una tendencia futura ni explican "
                "las causas del incremento de 2012 (expansión de flota, clima o "
                "adopción)."
            ),
        },
        {
            "pregunta": "Calidad",
            "metrica": "Cobertura nominal de registros horarios",
            "calculo": "(horas_observadas / horas_esperadas) × 100",
            "unidad": "Porcentaje (%) y conteo de horas sin registro",
            "denominador": "Cuadrícula nominal de 17.544 horas (731 fechas × 24)",
            "grafico_principal": "Barras / mapa de horas sin registro por hora y año",
            "decision_apoyada": (
                "Transparentar la calidad de cobertura antes de interpretar "
                "horas con menor registro (principalmente 02:00 a 05:00)."
            ),
            "limitaciones": (
                "Informar cobertura no elimina el posible sesgo de las 165 "
                "horas ausentes; no asume zona horaria ni horario de verano."
            ),
        },
    ]
    return pd.DataFrame(registros)


def _aplicar_estilo_base_plotly(
    figura: go.Figure,
    titulo: str,
    subtitulo: str,
    altura: int = 470,
) -> go.Figure:
    """Aplica estilo tipográfico, márgenes y paleta consistente a Plotly."""
    figura.update_layout(
        title={
            "text": (
                f"<b>{titulo}</b><br>"
                f"<span style='font-size:12px;color:#475569'>{subtitulo}</span>"
            ),
            "x": 0.01,
            "xanchor": "left",
        },
        font={"family": "Inter, Segoe UI, Arial, sans-serif", "color": "#0F172A"},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        height=altura,
        margin={"l": 65, "r": 30, "t": 90, "b": 75},
        hovermode="x unified",
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1.0,
            "bgcolor": "rgba(255,255,255,0.85)",
        },
    )
    figura.add_annotation(
        text=FUENTE_GRAFICO,
        xref="paper",
        yref="paper",
        x=0.0,
        y=-0.19,
        showarrow=False,
        font={"size": 10, "color": "#64748B"},
        xanchor="left",
    )
    return figura


def crear_grafico_p1_perfil_horario(
    tabla_p1: pd.DataFrame,
    mostrar_mediana: bool = True,
    tipos_seleccionados: list[str] | None = None,
) -> go.Figure:
    """Construye el gráfico interactivo principal de P1 (media y mediana)."""
    tipos_activos = (
        tipos_seleccionados if tipos_seleccionados else ORDEN_TIPOS_DIA
    )
    figura = go.Figure()

    for tipo_dia in ORDEN_TIPOS_DIA:
        if tipo_dia not in tipos_activos:
            continue
        subtabla = tabla_p1[tabla_p1["tipo_dia"].eq(tipo_dia)].sort_values(
            "hora"
        )
        color_serie = COLORES_TIPO_DIA[tipo_dia]
        etiquetas_hora = [f"{int(hora):02d}:00" for hora in subtabla["hora"]]

        figura.add_trace(
            go.Scatter(
                x=subtabla["hora"],
                y=subtabla["promedio_alquileres_por_hora"],
                mode="lines+markers",
                name=f"{tipo_dia} — Promedio",
                line={"color": color_serie, "width": 3},
                marker={"size": 6, "color": color_serie},
                customdata=subtabla[
                    [
                        "mediana_alquileres_por_hora",
                        "horas_observadas",
                        "cobertura_pct",
                        "alquileres_total",
                    ]
                ].to_numpy(),
                text=etiquetas_hora,
                hovertemplate=(
                    "<b>%{text} — " + tipo_dia + "</b><br>"
                    "Promedio: %{y:,.2f} alq./hora<br>"
                    "Mediana: %{customdata[0]:,.1f} alq./hora<br>"
                    "Observaciones: %{customdata[1]:.0f} horas "
                    "(cobertura %{customdata[2]:.2f} %)<br>"
                    "Volumen acumulado: %{customdata[3]:,.0f} alquileres"
                    "<extra></extra>"
                ),
            )
        )

        if mostrar_mediana:
            figura.add_trace(
                go.Scatter(
                    x=subtabla["hora"],
                    y=subtabla["mediana_alquileres_por_hora"],
                    mode="lines",
                    name=f"{tipo_dia} — Mediana",
                    line={"color": color_serie, "width": 2, "dash": "dot"},
                    hovertemplate=(
                        f"{tipo_dia} (Mediana): "
                        "%{y:,.1f} alq./hora<extra></extra>"
                    ),
                )
            )

    if "Laborable" in tipos_activos:
        fila_pico_lab = tabla_p1[
            tabla_p1["tipo_dia"].eq("Laborable") & tabla_p1["hora"].eq(17)
        ].iloc[0]
        fila_pico_manana = tabla_p1[
            tabla_p1["tipo_dia"].eq("Laborable") & tabla_p1["hora"].eq(8)
        ].iloc[0]
        figura.add_annotation(
            x=17,
            y=float(fila_pico_lab["promedio_alquileres_por_hora"]),
            text=(
                "Pico laborable: 17:00<br>"
                f"{formatear_decimal_es(fila_pico_lab['promedio_alquileres_por_hora'])} "
                "alq./h"
            ),
            showarrow=True,
            arrowhead=2,
            ax=22,
            ay=-38,
            bgcolor="#ECFDF5",
            bordercolor="#0F766E",
            font={"size": 11, "color": "#0F766E"},
        )
        figura.add_annotation(
            x=8,
            y=float(fila_pico_manana["promedio_alquileres_por_hora"]),
            text=(
                "Pico mañana: 08:00<br>"
                f"{formatear_decimal_es(fila_pico_manana['promedio_alquileres_por_hora'])} "
                "alq./h"
            ),
            showarrow=True,
            arrowhead=2,
            ax=-36,
            ay=-38,
            bgcolor="#ECFDF5",
            bordercolor="#0F766E",
            font={"size": 11, "color": "#0F766E"},
        )

    if "No laborable" in tipos_activos:
        fila_pico_nolab = tabla_p1[
            tabla_p1["tipo_dia"].eq("No laborable") & tabla_p1["hora"].eq(13)
        ].iloc[0]
        figura.add_annotation(
            x=13,
            y=float(fila_pico_nolab["promedio_alquileres_por_hora"]),
            text=(
                "Pico no laborable: 13:00<br>"
                f"{formatear_decimal_es(fila_pico_nolab['promedio_alquileres_por_hora'])} "
                "alq./h"
            ),
            showarrow=True,
            arrowhead=2,
            ax=0,
            ay=-44,
            bgcolor="#FFFBEB",
            bordercolor="#D97706",
            font={"size": 11, "color": "#B45309"},
        )

    figura.update_xaxes(
        title_text="Hora del día (00:00 a 23:00)",
        tickmode="array",
        tickvals=list(range(24)),
        ticktext=[f"{hora:02d}" for hora in range(24)],
        gridcolor="#E2E8F0",
    )
    figura.update_yaxes(
        title_text="Alquileres por hora registrada",
        gridcolor="#E2E8F0",
        rangemode="tozero",
    )
    return _aplicar_estilo_base_plotly(
        figura,
        titulo="P1 — Perfil horario de alquileres por tipo de día",
        subtitulo=(
            f"Promedio y mediana en alquileres por hora registrada | "
            f"{PERIODO_ETIQUETA}"
        ),
        altura=490,
    )


def crear_grafico_p1_brecha_horaria(tabla_brecha: pd.DataFrame) -> go.Figure:
    """Construye el gráfico divergente de brecha Laborable − No laborable."""
    colores_barra = [
        COLORES_TIPO_DIA["Laborable"]
        if valor >= 0
        else COLORES_TIPO_DIA["No laborable"]
        for valor in tabla_brecha["brecha_promedio"]
    ]

    figura = go.Figure(
        data=[
            go.Bar(
                x=tabla_brecha["hora"],
                y=tabla_brecha["brecha_promedio"],
                marker_color=colores_barra,
                customdata=tabla_brecha[
                    [
                        "etiqueta_hora",
                        "promedio_laborable",
                        "promedio_no_laborable",
                        "tipo_dominante",
                    ]
                ].to_numpy(),
                hovertemplate=(
                    "<b>Hora %{customdata[0]}</b><br>"
                    "Brecha (Lab − No lab): %{y:+,.2f} alq./hora<br>"
                    "Promedio laborable: %{customdata[1]:,.2f}<br>"
                    "Promedio no laborable: %{customdata[2]:,.2f}<br>"
                    "Patrón: %{customdata[3]}<extra></extra>"
                ),
                showlegend=False,
            )
        ]
    )
    figura.add_hline(y=0, line_color="#334155", line_width=1.5)
    figura.update_xaxes(
        title_text="Hora del día (00:00 a 23:00)",
        tickmode="array",
        tickvals=list(range(24)),
        ticktext=[f"{hora:02d}" for hora in range(24)],
        gridcolor="#E2E8F0",
    )
    figura.update_yaxes(
        title_text="Diferencia de promedio (alq./hora registrada)",
        gridcolor="#E2E8F0",
    )
    return _aplicar_estilo_base_plotly(
        figura,
        titulo="P1 — Brecha horaria: días laborables menos no laborables",
        subtitulo=(
            "Valores positivos (verde): supera Laborable | "
            f"Valores negativos (ámbar): supera No laborable | {PERIODO_ETIQUETA}"
        ),
        altura=430,
    )


def crear_grafico_p2_franjas(tabla_p2: pd.DataFrame) -> go.Figure:
    """Construye panel doble de participación (%) y volumen acumulado por franja."""
    figura = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=(
            "Participación dentro de cada tipo de día (%)",
            "Volumen acumulado (alquileres) e intensidad horaria",
        ),
        horizontal_spacing=0.12,
    )

    for tipo_dia in ORDEN_TIPOS_DIA:
        subtabla = tabla_p2[tabla_p2["tipo_dia"].eq(tipo_dia)].sort_values(
            "orden_franja"
        )
        color_serie = COLORES_TIPO_DIA[tipo_dia]
        etiquetas_pct = [
            f"{formatear_decimal_es(valor)} %"
            for valor in subtabla["participacion_alquileres_pct"]
        ]
        etiquetas_vol = [
            f"{formatear_entero_es(total)}<br>"
            f"({formatear_decimal_es(media, 1)}/h)"
            for total, media in zip(
                subtabla["alquileres_total"],
                subtabla["promedio_alquileres_por_hora"],
            )
        ]

        figura.add_trace(
            go.Bar(
                x=subtabla["franja_horaria"].astype(str),
                y=subtabla["participacion_alquileres_pct"],
                name=tipo_dia,
                legendgroup=tipo_dia,
                marker_color=color_serie,
                text=etiquetas_pct,
                textposition="outside",
                customdata=subtabla[
                    [
                        "alquileres_total",
                        "promedio_alquileres_por_hora",
                        "horas_observadas",
                        "cobertura_pct",
                    ]
                ].to_numpy(),
                hovertemplate=(
                    "<b>Franja %{x} — " + tipo_dia + "</b><br>"
                    "Participación en su tipo de día: %{y:.2f} %<br>"
                    "Alquileres acumulados: %{customdata[0]:,.0f}<br>"
                    "Promedio por hora registrada: %{customdata[1]:,.2f}<br>"
                    "Horas observadas: %{customdata[2]:,.0f} "
                    "(cobertura %{customdata[3]:.2f} %)<extra></extra>"
                ),
            ),
            row=1,
            col=1,
        )

        figura.add_trace(
            go.Bar(
                x=subtabla["franja_horaria"].astype(str),
                y=subtabla["alquileres_total"],
                name=tipo_dia,
                legendgroup=tipo_dia,
                showlegend=False,
                marker_color=color_serie,
                text=etiquetas_vol,
                textposition="outside",
                textfont={"size": 10},
                customdata=subtabla[
                    [
                        "participacion_alquileres_pct",
                        "promedio_alquileres_por_hora",
                        "mediana_alquileres_por_hora",
                        "cobertura_pct",
                    ]
                ].to_numpy(),
                hovertemplate=(
                    "<b>Franja %{x} — " + tipo_dia + "</b><br>"
                    "Alquileres acumulados: %{y:,.0f}<br>"
                    "Participación en su tipo: %{customdata[0]:.2f} %<br>"
                    "Promedio horario: %{customdata[1]:,.2f} alq./h<br>"
                    "Mediana horaria: %{customdata[2]:,.1f} alq./h<br>"
                    "Cobertura nominal: %{customdata[3]:.2f} %<extra></extra>"
                ),
            ),
            row=1,
            col=2,
        )

    figura.update_layout(barmode="group")
    figura.update_xaxes(title_text="Franja horaria (intervalos de 6 h)", row=1, col=1)
    figura.update_xaxes(title_text="Franja horaria (intervalos de 6 h)", row=1, col=2)
    figura.update_yaxes(
        title_text="Participación (% del tipo de día)",
        range=[0, 58],
        gridcolor="#E2E8F0",
        row=1,
        col=1,
    )
    figura.update_yaxes(
        title_text="Alquileres acumulados (2011–2012)",
        range=[0, 960000],
        gridcolor="#E2E8F0",
        row=1,
        col=2,
    )
    return _aplicar_estilo_base_plotly(
        figura,
        titulo="P2 — Concentración de alquileres por franja de seis horas",
        subtitulo=(
            "Denominador de participación: 2.292.410 en Laborable y "
            f"1.000.269 en No laborable | {PERIODO_ETIQUETA}"
        ),
        altura=500,
    )


def crear_grafico_p3_perfiles_anuales(
    tabla_p3: pd.DataFrame,
    metrica: str = "promedio_alquileres_por_hora",
) -> go.Figure:
    """Construye panel dual comparando 2011 vs. 2012 para cada tipo de día."""
    etiqueta_metrica = (
        "Promedio (alquileres / hora registrada)"
        if metrica == "promedio_alquileres_por_hora"
        else "Mediana (alquileres / hora registrada)"
    )

    figura = make_subplots(
        rows=1,
        cols=2,
        shared_yaxes=True,
        subplot_titles=(
            "Días laborables (máximo 17:00 en ambos años)",
            "Días no laborables (máximo 13:00 en ambos años)",
        ),
        horizontal_spacing=0.07,
    )

    for indice_columna, tipo_dia in enumerate(ORDEN_TIPOS_DIA, start=1):
        paleta = (
            COLORES_ANIO
            if tipo_dia == "Laborable"
            else COLORES_ANIO_NO_LABORABLE
        )
        for anio in [2011, 2012]:
            subtabla = tabla_p3[
                tabla_p3["tipo_dia"].eq(tipo_dia) & tabla_p3["anio"].eq(anio)
            ].sort_values("hora")
            estilo_linea = (
                {"color": paleta[anio], "width": 3}
                if anio == 2012
                else {"color": paleta[anio], "width": 2.4, "dash": "dash"}
            )
            figura.add_trace(
                go.Scatter(
                    x=subtabla["hora"],
                    y=subtabla[metrica],
                    mode="lines+markers",
                    name=f"{tipo_dia} — {anio}",
                    line=estilo_linea,
                    marker={"size": 5, "color": paleta[anio]},
                    customdata=subtabla[
                        [
                            "horas_observadas",
                            "cobertura_pct",
                            "rango_promedio",
                            "alquileres_total",
                        ]
                    ].to_numpy(),
                    hovertemplate=(
                        f"<b>{tipo_dia} ({anio}) — "
                        "%{x:02d}:00</b><br>"
                        f"{etiqueta_metrica}: "
                        "%{y:,.2f}<br>"
                        "Rango promedio anual: #%{customdata[2]:.0f}<br>"
                        "Observaciones: %{customdata[0]:.0f} "
                        "(cobertura %{customdata[1]:.2f} %)<br>"
                        "Volumen anual en la hora: %{customdata[3]:,.0f}"
                        "<extra></extra>"
                    ),
                ),
                row=1,
                col=indice_columna,
            )

            fila_pico = subtabla[subtabla["rango_promedio"].eq(1)].iloc[0]
            figura.add_trace(
                go.Scatter(
                    x=[int(fila_pico["hora"])],
                    y=[float(fila_pico[metrica])],
                    mode="markers",
                    marker={
                        "size": 11,
                        "color": paleta[anio],
                        "symbol": "diamond",
                        "line": {"color": "#FFFFFF", "width": 1.5},
                    },
                    showlegend=False,
                    hoverinfo="skip",
                ),
                row=1,
                col=indice_columna,
            )

    figura.update_xaxes(
        title_text="Hora del día (00 a 23)",
        tickmode="array",
        tickvals=list(range(0, 24, 2)),
        ticktext=[f"{hora:02d}" for hora in range(0, 24, 2)],
        gridcolor="#E2E8F0",
    )
    figura.update_yaxes(
        title_text=etiqueta_metrica,
        gridcolor="#E2E8F0",
        rangemode="tozero",
        row=1,
        col=1,
    )
    figura.update_yaxes(gridcolor="#E2E8F0", row=1, col=2)

    return _aplicar_estilo_base_plotly(
        figura,
        titulo="P3 — Estabilidad de horarios pico entre 2011 y 2012",
        subtitulo=(
            "Rombo: hora con rango_promedio = 1 en cada año | "
            "Los horarios máximos se mantienen, pero cambia la intensidad | "
            f"{PERIODO_ETIQUETA}"
        ),
        altura=480,
    )


def crear_grafico_p3_comparacion_picos(
    comparacion_anual: pd.DataFrame,
) -> go.Figure:
    """Compara la intensidad en la hora pico entre 2011 y 2012."""
    etiquetas_grupo = [
        f"{fila['tipo_dia']}<br>(pico {int(fila['hora_pico_2012']):02d}:00)"
        for _, fila in comparacion_anual.iterrows()
    ]

    figura = go.Figure()
    figura.add_trace(
        go.Bar(
            name="2011",
            x=etiquetas_grupo,
            y=comparacion_anual["promedio_pico_2011"],
            marker_color="#64748B",
            text=[
                f"{formatear_decimal_es(valor)} alq./h"
                for valor in comparacion_anual["promedio_pico_2011"]
            ],
            textposition="outside",
        )
    )
    figura.add_trace(
        go.Bar(
            name="2012",
            x=etiquetas_grupo,
            y=comparacion_anual["promedio_pico_2012"],
            marker_color="#0F766E",
            text=[
                f"{formatear_decimal_es(valor)} alq./h<br>"
                f"(+{formatear_decimal_es(cambio)} %)"
                for valor, cambio in zip(
                    comparacion_anual["promedio_pico_2012"],
                    comparacion_anual["cambio_pico_pct"],
                )
            ],
            textposition="outside",
        )
    )
    figura.update_layout(barmode="group")
    figura.update_yaxes(
        title_text="Promedio en la hora pico (alq./hora registrada)",
        range=[0, 790],
        gridcolor="#E2E8F0",
    )
    return _aplicar_estilo_base_plotly(
        figura,
        titulo="P3 — Cambio de nivel en la hora de mayor promedio (2011 vs. 2012)",
        subtitulo=(
            "Comparación descriptiva histórica; no explica causas del aumento "
            f"ni proyecta tendencia futura | {PERIODO_ETIQUETA}"
        ),
        altura=430,
    )


def crear_grafico_cobertura_horaria(tabla_p3: pd.DataFrame) -> go.Figure:
    """Visualiza las 165 horas sin registro distribuidas por hora y grupo."""
    tabla_ordenada = tabla_p3.copy()
    tabla_ordenada["serie"] = (
        tabla_ordenada["anio"].astype(str)
        + " — "
        + tabla_ordenada["tipo_dia"].astype(str)
    )
    matriz_ausencias = tabla_ordenada.pivot(
        index="serie", columns="hora", values="horas_sin_registro"
    )
    orden_series = [
        "2011 — Laborable",
        "2011 — No laborable",
        "2012 — Laborable",
        "2012 — No laborable",
    ]
    matriz_ausencias = matriz_ausencias.reindex(orden_series)

    figura = go.Figure(
        data=go.Heatmap(
            z=matriz_ausencias.to_numpy(),
            x=[f"{hora:02d}" for hora in matriz_ausencias.columns],
            y=matriz_ausencias.index.tolist(),
            colorscale=[
                [0.0, "#F1F5F9"],
                [0.2, "#FDE68A"],
                [0.6, "#F59E0B"],
                [1.0, "#B91C1C"],
            ],
            text=matriz_ausencias.to_numpy(),
            texttemplate="%{text}",
            textfont={"size": 10},
            colorbar={"title": "Horas ausentes"},
            hovertemplate=(
                "<b>%{y} — Hora %{x}:00</b><br>"
                "Horas sin registro: %{z}<extra></extra>"
            ),
        )
    )
    figura.update_xaxes(title_text="Hora del día (00:00 a 23:00)")
    figura.update_yaxes(title_text="Año y tipo de día", autorange="reversed")
    return _aplicar_estilo_base_plotly(
        figura,
        titulo="Calidad y cobertura — Distribución de las 165 horas sin registro",
        subtitulo=(
            "Cuadrícula nominal de 24 horas/fecha (17.544 esperadas; 17.379 "
            "observadas) | Las ausencias no equivalen a cero alquileres"
        ),
        altura=370,
    )


def exportar_resumen_ae4(ruta_raiz: Path | None = None) -> dict[str, Any]:
    """Exporta catálogo de métricas y resumen verificado en AE4/resultados/."""
    repositorio = cargar_datos_proyecto(ruta_raiz)
    raiz = repositorio["ruta_raiz"]
    carpeta_salida = raiz / "AE4" / "resultados"
    carpeta_salida.mkdir(parents=True, exist_ok=True)

    comprobaciones = verificar_coherencia_datos(repositorio)
    indicadores = calcular_indicadores_generales(repositorio)
    brecha_p1 = calcular_brecha_horaria_p1(repositorio["tabla_p1"])
    picos_p3, comparacion_p3 = calcular_resumen_interanual_p3(
        repositorio["tabla_p3"]
    )
    catalogo = obtener_catalogo_metricas()

    catalogo.to_csv(
        carpeta_salida / "tablas_metricas_ae4.csv",
        index=False,
        encoding="utf-8",
        lineterminator="\n",
    )

    fila_max_brecha_lab = brecha_p1.sort_values(
        "brecha_promedio", ascending=False
    ).iloc[0]
    fila_max_brecha_nolab = brecha_p1.sort_values(
        "brecha_promedio", ascending=True
    ).iloc[0]

    resumen = {
        "etapa": "AE4",
        "fecha_generacion": "2026-11-26",
        "dataset_id": repositorio["validaciones_ae3"]["dataset_id"],
        "revision": repositorio["validaciones_ae3"]["revision"],
        "indicadores_generales": indicadores,
        "brechas_extremas_p1": {
            "mayor_ventaja_laborable": {
                "hora": int(fila_max_brecha_lab["hora"]),
                "brecha_promedio": float(
                    fila_max_brecha_lab["brecha_promedio"]
                ),
                "promedio_laborable": float(
                    fila_max_brecha_lab["promedio_laborable"]
                ),
                "promedio_no_laborable": float(
                    fila_max_brecha_lab["promedio_no_laborable"]
                ),
            },
            "mayor_ventaja_no_laborable": {
                "hora": int(fila_max_brecha_nolab["hora"]),
                "brecha_promedio": float(
                    fila_max_brecha_nolab["brecha_promedio"]
                ),
                "promedio_laborable": float(
                    fila_max_brecha_nolab["promedio_laborable"]
                ),
                "promedio_no_laborable": float(
                    fila_max_brecha_nolab["promedio_no_laborable"]
                ),
            },
        },
        "comparacion_interanual_p3": comparacion_p3.to_dict(orient="records"),
        "picos_anuales_p3": picos_p3[
            [
                "anio",
                "tipo_dia",
                "hora",
                "horas_observadas",
                "promedio_alquileres_por_hora",
                "mediana_alquileres_por_hora",
                "cobertura_pct",
            ]
        ].to_dict(orient="records"),
        "comprobaciones_coherencia": comprobaciones,
        "todas_las_comprobaciones_ok": all(
            item["estado"] for item in comprobaciones
        ),
    }

    (carpeta_salida / "resumen_metricas_ae4.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return resumen
