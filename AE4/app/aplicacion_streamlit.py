"""Aplicación interactiva en Streamlit para la entrega AE4.

Presenta la necesidad, las preguntas de negocio, la identificación del dataset,
las métricas y gráficos verificados de P1, P2 y P3, los controles de cobertura
y coherencia con AE3, y las conclusiones, recomendaciones y limitaciones.

Ejecución local desde la raíz del repositorio:
    .venv\\Scripts\\python.exe -m streamlit run AE4/app/aplicacion_streamlit.py
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

RUTA_RAIZ = Path(__file__).resolve().parents[2]
if str(RUTA_RAIZ) not in sys.path:
    sys.path.insert(0, str(RUTA_RAIZ))

MODULO_METRICAS: Any = importlib.import_module("AE4.src.metricas_y_graficos")

ORDEN_FRANJAS = MODULO_METRICAS.ORDEN_FRANJAS
ORDEN_TIPOS_DIA = MODULO_METRICAS.ORDEN_TIPOS_DIA
calcular_brecha_horaria_p1 = MODULO_METRICAS.calcular_brecha_horaria_p1
calcular_indicadores_generales = MODULO_METRICAS.calcular_indicadores_generales
calcular_resumen_interanual_p3 = MODULO_METRICAS.calcular_resumen_interanual_p3
cargar_datos_proyecto = MODULO_METRICAS.cargar_datos_proyecto
crear_grafico_cobertura_horaria = (
    MODULO_METRICAS.crear_grafico_cobertura_horaria
)
crear_grafico_p1_brecha_horaria = (
    MODULO_METRICAS.crear_grafico_p1_brecha_horaria
)
crear_grafico_p1_perfil_horario = (
    MODULO_METRICAS.crear_grafico_p1_perfil_horario
)
crear_grafico_p2_franjas = MODULO_METRICAS.crear_grafico_p2_franjas
crear_grafico_p3_comparacion_picos = (
    MODULO_METRICAS.crear_grafico_p3_comparacion_picos
)
crear_grafico_p3_perfiles_anuales = (
    MODULO_METRICAS.crear_grafico_p3_perfiles_anuales
)
formatear_decimal_es = MODULO_METRICAS.formatear_decimal_es
formatear_entero_es = MODULO_METRICAS.formatear_entero_es
obtener_catalogo_metricas = MODULO_METRICAS.obtener_catalogo_metricas
verificar_coherencia_datos = MODULO_METRICAS.verificar_coherencia_datos

SECCIONES_NAVEGACION = [
    "1. Contexto y dataset",
    "2. P1 — Perfil horario",
    "3. P2 — Franjas de seis horas",
    "4. P3 — Estabilidad 2011 vs. 2012",
    "5. Calidad, cobertura y verificación",
    "6. Conclusiones y limitaciones",
]


@st.cache_data(show_spinner=False)
def obtener_repositorio_en_cache() -> dict:
    """Carga y mantiene en caché los datos verificados del proyecto."""
    return cargar_datos_proyecto(RUTA_RAIZ)


def aplicar_estilos_aplicacion() -> None:
    """Inyecta estilos sobrios y legibles para presentación ejecutiva."""
    st.markdown(
        """
        <style>
        .bloque-encabezado {
            background: linear-gradient(135deg, #0F766E 0%, #115E59 100%);
            color: #FFFFFF;
            padding: 1.4rem 1.6rem;
            border-radius: 12px;
            margin-bottom: 1.2rem;
        }
        .bloque-encabezado h1 {
            color: #FFFFFF;
            font-size: 1.65rem;
            margin: 0 0 0.35rem 0;
        }
        .bloque-encabezado p {
            color: #CCFBF1;
            margin: 0;
            font-size: 0.96rem;
        }
        .tarjeta-nota {
            background-color: #FFFFFF;
            border-left: 4px solid #0F766E;
            padding: 0.9rem 1.1rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
            margin-bottom: 0.9rem;
        }
        .tarjeta-alerta {
            background-color: #FFFBEB;
            border-left: 4px solid #D97706;
            padding: 0.9rem 1.1rem;
            border-radius: 8px;
            margin-bottom: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def mostrar_encabezado_principal() -> None:
    """Renderiza el banner institucional superior."""
    st.markdown(
        """
        <div class="bloque-encabezado">
            <h1>Patrones horarios de alquiler de bicicletas según tipo de día</h1>
            <p>
                Proyecto Integrador (AE4 — Métricas y Visualización) ·
                Capital Bikeshare (2011–2012) · Grupo 17 · IU Digital de Antioquia
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_barra_lateral(indicadores: dict) -> str:
    """Construye la barra lateral con navegación e información del equipo."""
    st.sidebar.title("Navegación AE4")
    seccion_elegida = st.sidebar.radio(
        "Recorrido de presentación:",
        SECCIONES_NAVEGACION,
        index=0,
    )
    st.sidebar.divider()
    st.sidebar.markdown("**Equipo — Grupo 17**")
    st.sidebar.markdown(
        "- Juan Esteban Casadiego Benavides\n"
        "- Evelyn Cerro\n\n"
        "**Docente:** Andrés Felipe Callejas Jaramillo\n\n"
        "**Institución:** IU Digital de Antioquia"
    )
    st.sidebar.divider()
    st.sidebar.caption(
        "Datos verificados desde AE3:\n"
        f"- {formatear_entero_es(indicadores['horas_observadas'])} registros horarios\n"
        f"- {formatear_entero_es(indicadores['alquileres_total'])} alquileres totales\n"
        f"- Cobertura nominal: {formatear_decimal_es(indicadores['cobertura_total_pct'])} %"
    )
    return seccion_elegida


def renderizar_contexto_y_dataset(
    repositorio: dict, indicadores: dict
) -> None:
    """Sección 1: necesidad, preguntas de negocio e identificación del dataset."""
    st.header("1. Necesidad, preguntas de negocio y dataset")

    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
    col_kpi1.metric(
        "Alquileres registrados (2011–2012)",
        formatear_entero_es(indicadores["alquileres_total"]),
        "Conteos horarios acumulados",
    )
    col_kpi2.metric(
        "Registros horarios observados",
        formatear_entero_es(indicadores["horas_observadas"]),
        f"{formatear_entero_es(indicadores['fechas_distintas'])} fechas",
    )
    col_kpi3.metric(
        "Cobertura nominal",
        f"{formatear_decimal_es(indicadores['cobertura_total_pct'])} %",
        f"{indicadores['horas_ausentes']} horas sin registro",
    )
    col_kpi4.metric(
        "Horas de mayor promedio",
        f"{indicadores['pico_laborable_hora']:02d}:00 Lab | "
        f"{indicadores['pico_no_laborable_hora']:02d}:00 No lab",
        "Consistentes en 2011 y 2012",
    )

    col_izq, col_der = st.columns([1.15, 1.0])
    with col_izq:
        st.subheader("Escenario de uso y necesidad")
        st.markdown(
            """
            <div class="tarjeta-nota">
            <strong>Beneficiario (escenario hipotético de aprendizaje):</strong>
            una coordinación de planeación operativa de un sistema de bicicletas
            compartidas que analiza un caso histórico para orientar la revisión
            de horarios de atención y seguimiento operativo.
            <br><br>
            <strong>Necesidad propuesta:</strong> conocer cómo se distribuyen los
            alquileres registrados a lo largo del día y cómo varían sus niveles
            entre días laborables y no laborables. No se afirma que exista una
            falla operativa comprobada, escasez de bicicletas ni pérdidas
            económicas demostradas.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info(
            "**Pregunta central de análisis:** ¿Cómo varía el número de "
            "alquileres registrados por hora entre días laborables y no "
            "laborables en los registros de Capital Bikeshare de 2011 y 2012?"
        )

    with col_der:
        st.subheader("Identificación del dataset")
        ficha_dataset = pd.DataFrame(
            [
                ("Fuente / ID Hugging Face", "t22000t/bike-sharing-tabular"),
                ("Procedencia original", "Capital Bikeshare (Washington D. C.) — UCI"),
                ("Revisión fijada", "6b645e0cedbc5208fcca11ac94544b088478bf61"),
                ("Periodo observado", "2011-01-01 a 2012-12-31 (731 fechas)"),
                ("Unidad de análisis", "Una fecha y una hora agregada del sistema"),
                ("Base preparada AE3", "17.379 filas × 11 columnas (0 celdas nulas)"),
                ("Composición de conteos", "81,17 % registrados | 18,83 % ocasionales"),
                ("Licencia", "CC BY 4.0 (atribución y trazabilidad conservadas)"),
            ],
            columns=["Elemento", "Detalle verificado"],
        )
        st.dataframe(ficha_dataset, hide_index=True, width="stretch")

    st.subheader("Preguntas de negocio respondidas en esta aplicación")
    tabla_preguntas = pd.DataFrame(
        [
            (
                "P1",
                (
                    "¿Cómo varían el promedio y la mediana de alquileres por "
                    "hora entre días laborables y no laborables?"
                ),
                "Promedio, mediana, brecha horaria y cobertura (alq./hora registrada)",
                "AE3/resultados/p1_perfil_horario.csv (48 filas)",
            ),
            (
                "P2",
                (
                    "¿Qué franjas de seis horas concentran más alquileres "
                    "dentro de cada tipo de día?"
                ),
                "Participación (% del tipo de día), volumen acumulado y media/hora",
                "AE3/resultados/p2_franjas.csv (8 filas)",
            ),
            (
                "P3",
                (
                    "¿Se mantienen los horarios de mayor promedio al separar "
                    "2011 y 2012 para cada tipo de día?"
                ),
                "Rango promedio anual, picos por año y variación interanual (%)",
                "AE3/resultados/p3_perfil_anual.csv (96 filas)",
            ),
        ],
        columns=["ID", "Pregunta de negocio", "Métricas principales", "Tabla fuente"],
    )
    st.dataframe(tabla_preguntas, hide_index=True, width="stretch")


def renderizar_pregunta_p1(repositorio: dict, indicadores: dict) -> None:
    """Sección 2: métricas, gráficos e interpretación de P1."""
    tabla_p1 = repositorio["tabla_p1"]
    tabla_brecha = calcular_brecha_horaria_p1(tabla_p1)

    st.header("2. P1 — Perfil horario según tipo de día")
    st.markdown(
        "**Pregunta:** *¿Cómo varían el promedio y la mediana de alquileres "
        "por hora entre días laborables y no laborables?*"
    )

    with st.expander(
        "Definición de métricas, fórmulas y unidades (P1)", expanded=True
    ):
        st.markdown(
            """
            - **Promedio por hora registrada:** `suma(alquileres_total) / horas_observadas` ·
              Unidad: *alquileres por hora registrada*.
            - **Mediana por hora registrada:** percentil 50 de `alquileres_total` en cada
              grupo hora × tipo de día · Unidad: *alquileres por hora registrada*
              (controla valores extremos).
            - **Brecha horaria:** `promedio_laborable(hora) − promedio_no_laborable(hora)` ·
              Unidad: *diferencia en alquileres por hora registrada*.
            - **Cobertura nominal:** `(horas_observadas / horas_esperadas) × 100` ·
              Unidad: *porcentaje (%)*; evita confundir horas ausentes con cero alquileres.
            """
        )

    col_filtro1, col_filtro2, col_filtro3 = st.columns([1.4, 1.0, 1.2])
    with col_filtro1:
        tipos_elegidos = st.multiselect(
            "Tipos de día visibles:",
            ORDEN_TIPOS_DIA,
            default=ORDEN_TIPOS_DIA,
        )
    with col_filtro2:
        mostrar_mediana = st.checkbox("Superponer mediana", value=True)
    with col_filtro3:
        hora_detalle = st.slider("Inspeccionar hora específica:", 0, 23, 17)

    fila_hora = tabla_brecha[tabla_brecha["hora"].eq(hora_detalle)].iloc[0]
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric(
        f"Laborable ({hora_detalle:02d}:00)",
        f"{formatear_decimal_es(fila_hora['promedio_laborable'])} alq./h",
        f"Mediana: {formatear_decimal_es(fila_hora['mediana_laborable'], 1)}",
    )
    col_m2.metric(
        f"No laborable ({hora_detalle:02d}:00)",
        f"{formatear_decimal_es(fila_hora['promedio_no_laborable'])} alq./h",
        f"Mediana: {formatear_decimal_es(fila_hora['mediana_no_laborable'], 1)}",
    )
    col_m3.metric(
        "Brecha (Lab − No lab)",
        f"{fila_hora['brecha_promedio']:+.2f}".replace(".", ",") + " alq./h",
        str(fila_hora["tipo_dominante"]),
    )
    col_m4.metric(
        "Cobertura en la hora",
        f"{formatear_decimal_es(fila_hora['cobertura_laborable_pct'])} % Lab",
        f"{formatear_decimal_es(fila_hora['cobertura_no_laborable_pct'])} % No lab",
    )

    figura_p1 = crear_grafico_p1_perfil_horario(
        tabla_p1,
        mostrar_mediana=mostrar_mediana,
        tipos_seleccionados=tipos_elegidos or ORDEN_TIPOS_DIA,
    )
    st.plotly_chart(figura_p1, width="stretch")

    figura_brecha = crear_grafico_p1_brecha_horaria(tabla_brecha)
    st.plotly_chart(figura_brecha, width="stretch")

    col_texto1, col_texto2 = st.columns(2)
    with col_texto1:
        st.subheader("Qué muestran los datos y qué decisión apoyan")
        media_manana = formatear_decimal_es(
            indicadores["pico_manana_laborable_promedio"]
        )
        mediana_manana = formatear_decimal_es(
            indicadores["pico_manana_laborable_mediana"], 1
        )
        media_lab = formatear_decimal_es(
            indicadores["pico_laborable_promedio"]
        )
        mediana_lab = formatear_decimal_es(
            indicadores["pico_laborable_mediana"], 1
        )
        cobertura_lab = formatear_decimal_es(
            indicadores["pico_laborable_cobertura_pct"]
        )
        media_nolab = formatear_decimal_es(
            indicadores["pico_no_laborable_promedio"]
        )
        mediana_nolab = formatear_decimal_es(
            indicadores["pico_no_laborable_mediana"], 1
        )
        st.markdown(
            f"""
            - **Patrón bimodal en días laborables:** emergen dos picos bien
              definidos: uno en la mañana a las **08:00**
              (**{media_manana}** alquileres/hora, mediana {mediana_manana})
              y el máximo absoluto del día a las **17:00**
              (**{media_lab}** alquileres/hora, mediana {mediana_lab},
              cobertura {cobertura_lab} %),
              seguido muy de cerca por las 18:00 (492,23).
            - **Patrón unimodal en días no laborables:** el uso crece de forma
              continua desde las 08:00 hasta formar una meseta entre las 12:00
              y las 16:00, con máximo a las **13:00**
              (**{media_nolab}** alquileres/hora, mediana {mediana_nolab},
              cobertura 100,00 %).
            - **Cercanía entre media y mediana:** confirma que el patrón no
              depende de unos pocos días atípicos.
            - **Decisión operativa apoyada:** en el escenario hipotético,
              permite diferenciar los horarios de seguimiento y revisión de
              turnos según calendario (ventanas 07–09 y 17–19 en laborables vs.
              bloque central 11–17 en fines de semana y festivos).
            """
        )

    with col_texto2:
        st.subheader("Limitaciones y alcance de P1")
        st.markdown(
            """
            <div class="tarjeta-alerta">
            <strong>Volumen operativo ≠ ingresos ni rentabilidad:</strong>
            estos registros miden cantidad de alquileres iniciados, no tarifas,
            ingresos ni costos operativos (redistribución o mantenimiento). Una
            hora con mayor promedio no implica automáticamente mayor margen.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            - **Sin inferencia causal:** aunque los picos de 08:00 y 17:00 son
              compatibles con jornadas laborales, el dataset no registra el
              motivo del viaje.
            - **No mide demanda insatisfecha ni congestión:** las cifras
              corresponden solo a alquileres efectivamente concretados.
            - **Ausencias en madrugada:** las horas 03:00 y 04:00 en laborables
              tienen 30 ausencias cada una (cobertura 94,00 %), sin imputarse
              como cero.
            """
        )

    with st.expander("Ver tabla completa de P1 (48 filas verificadas)"):
        st.dataframe(tabla_p1, hide_index=True, width="stretch")


def renderizar_pregunta_p2(repositorio: dict, indicadores: dict) -> None:
    """Sección 3: métricas, gráficos e interpretación de P2."""
    tabla_p2 = repositorio["tabla_p2"]

    st.header("3. P2 — Concentración por franjas de seis horas")
    st.markdown(
        "**Pregunta:** *¿Qué franjas de seis horas concentran más alquileres "
        "dentro de cada tipo de día?*"
    )

    with st.expander(
        "Definición de métricas, fórmulas y unidades (P2)", expanded=True
    ):
        total_lab_texto = formatear_entero_es(
            indicadores["alquileres_laborable"]
        )
        total_nolab_texto = formatear_entero_es(
            indicadores["alquileres_no_laborable"]
        )
        st.markdown(
            f"""
            - **Participación porcentual por franja:**
              `(alquileres_franja / total_alquileres_tipo_dia) × 100` ·
              Unidad: *porcentaje (%)*. Denominadores independientes:
              **{total_lab_texto}** alquileres en días laborables y
              **{total_nolab_texto}** en no laborables (cada tipo suma
              100,00 % antes de redondear).
            - **Volumen acumulado:** suma de `alquileres_total` por franja ·
              Unidad: *alquileres acumulados (2011–2012)*.
            - **Intensidad media horaria:** `alquileres_total / horas_observadas` ·
              Unidad: *alquileres por hora registrada* (clave porque hay 500
              días laborables frente a 231 no laborables).
            """
        )

    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    col_k1.metric(
        "Franja líder Laborable",
        indicadores["franja_lider_laborable"],
        f"{formatear_decimal_es(indicadores['franja_lider_laborable_pct'])} % de su tipo",
    )
    col_k2.metric(
        "Volumen 12 a 17 (Lab)",
        formatear_entero_es(indicadores["franja_lider_laborable_total"]),
        f"Media: {formatear_decimal_es(indicadores['franja_lider_laborable_promedio'])} alq./h",
    )
    col_k3.metric(
        "Franja líder No laborable",
        indicadores["franja_lider_no_laborable"],
        f"{formatear_decimal_es(indicadores['franja_lider_no_laborable_pct'])} % de su tipo",
    )
    col_k4.metric(
        "Volumen 12 a 17 (No lab)",
        formatear_entero_es(indicadores["franja_lider_no_laborable_total"]),
        f"Media: {formatear_decimal_es(indicadores['franja_lider_no_laborable_promedio'])} alq./h",
    )

    figura_p2 = crear_grafico_p2_franjas(tabla_p2)
    st.plotly_chart(figura_p2, width="stretch")

    col_texto1, col_texto2 = st.columns(2)
    with col_texto1:
        st.subheader("Qué muestran los datos y qué decisión apoyan")
        st.markdown(
            """
            - **Predominio de la franja 12 a 17 en ambos tipos de día:**
              concentra **34,84 %** de los alquileres en días laborables
              (798.696 alquileres) y casi la mitad (**49,39 %**) en días no
              laborables (494.046 alquileres).
            - **Distribución más repartida en días laborables:** las tres
              franjas diurnas y nocturnas (`06 a 11`: 30,40 %, `12 a 17`:
              34,84 % y `18 a 23`: 32,67 %) tienen pesos muy cercanos entre sí,
              mientras que en no laborables el uso se concentra fuertemente en
              `12 a 17`.
            - **Contraste clave volumen vs. intensidad:** en `12 a 17`, los
              días laborables suman más alquileres totales (por haber 500 días
              frente a 231), pero los días no laborables registran **mayor
              intensidad media por hora** (**356,45** vs. **267,21** alq./h).
            - **Decisión operativa apoyada:** asignar bloques de supervisión y
              revisión de flota por turnos de seis horas: cobertura sostenida
              entre 06:00 y 23:00 en laborables y foco especial en el bloque
              12:00–17:00 durante fines de semana y festivos.
            """
        )

    with col_texto2:
        st.subheader("Limitaciones y alcance de P2")
        st.markdown(
            """
            <div class="tarjeta-alerta">
            <strong>Por qué se requieren tres medidas juntas:</strong> analizar
            solo totales favorece a días laborables por tener más fechas;
            analizar solo porcentajes oculta la escala real; y ninguna de las
            dos medidas expresa ingresos ni rentabilidad neta por franja.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            - **Regla de agrupación del proyecto:** los cortes `00 a 05`,
              `06 a 11`, `12 a 17` y `18 a 23` provienen de `hora // 6`, no de
              turnos oficiales de Capital Bikeshare.
            - **Pérdida de resolución interna:** la franja `12 a 17` en días
              laborables mezcla horas de actividad moderada (12:00–15:00) con el
              pico máximo de las 17:00; por eso debe leerse junto con P1.
            - **Conteos ≠ usuarios únicos:** una persona puede efectuar varios
              alquileres en la misma franja.
            """
        )

    st.subheader("Tabla verificada de P2 (8 combinaciones)")
    vista_p2 = tabla_p2[
        [
            "tipo_dia",
            "franja_horaria",
            "horas_observadas",
            "alquileres_total",
            "promedio_alquileres_por_hora",
            "mediana_alquileres_por_hora",
            "participacion_alquileres_pct",
            "cobertura_pct",
        ]
    ].copy()
    vista_p2.columns = [
        "Tipo de día",
        "Franja horaria",
        "Horas observadas",
        "Alquileres totales",
        "Promedio / hora",
        "Mediana / hora",
        "Participación (%)",
        "Cobertura (%)",
    ]
    st.dataframe(vista_p2, hide_index=True, width="stretch")


def renderizar_pregunta_p3(repositorio: dict, indicadores: dict) -> None:
    """Sección 4: métricas, gráficos e interpretación de P3."""
    tabla_p3 = repositorio["tabla_p3"]
    picos_anuales, comparacion_anual = calcular_resumen_interanual_p3(tabla_p3)

    st.header("4. P3 — Estabilidad de horarios pico entre 2011 y 2012")
    st.markdown(
        "**Pregunta:** *¿Se mantienen los horarios de mayor promedio al "
        "separar 2011 y 2012 para cada tipo de día?*"
    )

    with st.expander(
        "Definición de métricas, fórmulas y unidades (P3)", expanded=True
    ):
        st.markdown(
            """
            - **Rango promedio anual (`rango_promedio`):** posición ordinal
              descendente del promedio horario dentro de cada año × tipo de día
              (1 = máximo; conserva empates).
            - **Promedio y mediana anuales por hora:**
              `alquileres_total / horas_observadas` y percentil 50 ·
              Unidad: *alquileres por hora registrada*.
            - **Variación interanual del pico:** cambio absoluto
              (`media_2012 − media_2011`) y relativo
              (`(media_2012 − media_2011) / media_2011 × 100`) ·
              Unidad: *alq./hora* y *porcentaje (%)*.
            """
        )

    fila_lab = comparacion_anual[
        comparacion_anual["tipo_dia"].eq("Laborable")
    ].iloc[0]
    fila_nolab = comparacion_anual[
        comparacion_anual["tipo_dia"].eq("No laborable")
    ].iloc[0]

    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    col_c1.metric(
        "Pico Laborable (2011 → 2012)",
        f"{int(fila_lab['hora_pico_2011']):02d}:00 → "
        f"{int(fila_lab['hora_pico_2012']):02d}:00",
        "Hora máxima idéntica",
    )
    col_c2.metric(
        "Nivel pico Laborable (17:00)",
        f"{formatear_decimal_es(fila_lab['promedio_pico_2012'])} alq./h",
        f"+{formatear_decimal_es(fila_lab['cambio_pico_pct'])} % vs. 2011",
    )
    col_c3.metric(
        "Pico No laborable (2011 → 2012)",
        f"{int(fila_nolab['hora_pico_2011']):02d}:00 → "
        f"{int(fila_nolab['hora_pico_2012']):02d}:00",
        "Hora máxima idéntica",
    )
    col_c4.metric(
        "Nivel pico No laborable (13:00)",
        f"{formatear_decimal_es(fila_nolab['promedio_pico_2012'])} alq./h",
        f"+{formatear_decimal_es(fila_nolab['cambio_pico_pct'])} % vs. 2011",
    )

    selector_metrica = st.radio(
        "Medida de posición a visualizar en el perfil anual:",
        options=["Promedio por hora registrada", "Mediana por hora registrada"],
        horizontal=True,
    )
    columna_metrica = (
        "promedio_alquileres_por_hora"
        if selector_metrica.startswith("Promedio")
        else "mediana_alquileres_por_hora"
    )

    figura_perfiles = crear_grafico_p3_perfiles_anuales(
        tabla_p3, metrica=columna_metrica
    )
    st.plotly_chart(figura_perfiles, width="stretch")

    figura_picos = crear_grafico_p3_comparacion_picos(comparacion_anual)
    st.plotly_chart(figura_picos, width="stretch")

    col_texto1, col_texto2 = st.columns(2)
    with col_texto1:
        st.subheader("Qué muestran los datos y qué decisión apoyan")
        st.markdown(
            f"""
            - **Respuesta directa a P3 — Sí, las horas máximas se mantienen:**
              en ambos años el máximo promedio ocurre a las **17:00** en días
              laborables y a las **13:00** en no laborables. Esto descarta que
              los picos de P1 sean un artefacto de mezclar 2011 y 2012.
            - **Aumento generalizado de intensidad en 2012:** en días
              laborables, el pico de las 17:00 sube de **394,92** a **656,19**
              alq./h (**+66,16 %**); en no laborables, el pico de las 13:00
              pasa de **285,80** a **458,91** alq./h (**+60,57 %**). El total
              anual crece de **{formatear_entero_es(indicadores['alquileres_2011'])}**
              a **{formatear_entero_es(indicadores['alquileres_2012'])}**
              alquileres (+{formatear_decimal_es(indicadores['variacion_total_anual_pct'])} %).
            - **Decisión operativa apoyada:** confirma que los horarios pico
              son estables como referencia para planear revisiones operativas,
              pero obliga a actualizar periódicamente la capacidad porque el
              nivel de uso puede escalar sustancialmente de un año a otro.
            """
        )

    with col_texto2:
        st.subheader("Limitaciones y alcance de P3")
        st.markdown(
            """
            <div class="tarjeta-alerta">
            <strong>Dos años históricos no demuestran tendencia futura ni
            explican causas:</strong> el aumento entre 2011 y 2012 pudo estar
            asociado a expansión de estaciones, más bicicletas, clima o mayor
            adopción, variables que no se modelan ni se controlan aquí.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            - **Sin información financiera:** un incremento de +64,88 % en
              volumen total de alquileres no permite afirmar que la
              rentabilidad haya crecido en la misma proporción, pues se
              desconocen tarifas, subsidios y costos de expansión.
            - **Diferencias de cobertura:** 2011 presenta 115 horas ausentes
              (89 laborables y 26 no laborables), mientras que 2012 registra 50
              (46 laborables y 4 no laborables).
            """
        )

    st.subheader("Resumen de horas máximas anuales (rango_promedio = 1)")
    st.dataframe(
        picos_anuales[
            [
                "anio",
                "tipo_dia",
                "hora",
                "horas_observadas",
                "promedio_alquileres_por_hora",
                "mediana_alquileres_por_hora",
                "cobertura_pct",
            ]
        ],
        hide_index=True,
        width="stretch",
    )

    with st.expander("Ver tabla completa de P3 (96 filas verificadas)"):
        st.dataframe(tabla_p3, hide_index=True, width="stretch")


def renderizar_calidad_y_verificacion(repositorio: dict) -> None:
    """Sección 5: calidad, cobertura, explorador base y verificación viva."""
    st.header("5. Calidad, cobertura y verificación de coherencia")

    comprobaciones = verificar_coherencia_datos(repositorio)
    todas_ok = all(item["estado"] for item in comprobaciones)
    if todas_ok:
        st.success(
            "Verificación automática aprobada: todas las cifras de esta "
            "aplicación coinciden exactamente con dataset_preparado.csv, "
            "las tablas de AE3 y validaciones.json."
        )
    else:
        st.error("Se detectó una discrepancia en la verificación de datos.")

    tabla_comprobaciones = pd.DataFrame(
        [
            {
                "Control de coherencia": item["control"],
                "Estado": "Aprobado" if item["estado"] else "Revisar",
                "Detalle verificado": item["detalle"],
            }
            for item in comprobaciones
        ]
    )
    st.dataframe(tabla_comprobaciones, hide_index=True, width="stretch")

    st.subheader("Distribución de las 165 horas sin registro")
    figura_cobertura = crear_grafico_cobertura_horaria(repositorio["tabla_p3"])
    st.plotly_chart(figura_cobertura, width="stretch")

    col_cob1, col_cob2 = st.columns(2)
    with col_cob1:
        st.markdown("**Cobertura nominal por año y tipo de día**")
        st.dataframe(
            repositorio["cobertura_anual"],
            hide_index=True,
            width="stretch",
        )
    with col_cob2:
        st.markdown("**Comparación antes (AE2) y después (AE3)**")
        st.dataframe(
            repositorio["comparacion_bases"],
            hide_index=True,
            width="stretch",
        )

    st.subheader("Explorador interactivo de dataset_preparado.csv (17.379 filas)")
    datos_preparados = repositorio["datos_preparados"]
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        anios_sel = st.multiselect(
            "Año:", options=[2011, 2012], default=[2011, 2012]
        )
    with col_f2:
        tipos_sel = st.multiselect(
            "Tipo de día:", options=ORDEN_TIPOS_DIA, default=ORDEN_TIPOS_DIA
        )
    with col_f3:
        franjas_sel = st.multiselect(
            "Franja horaria:", options=ORDEN_FRANJAS, default=ORDEN_FRANJAS
        )

    filtrado = datos_preparados[
        datos_preparados["anio"].isin(anios_sel)
        & datos_preparados["tipo_dia"].isin(tipos_sel)
        & datos_preparados["franja_horaria"].isin(franjas_sel)
    ]

    col_e1, col_e2, col_e3, col_e4 = st.columns(4)
    col_e1.metric("Registros filtrados", formatear_entero_es(len(filtrado)))
    col_e2.metric(
        "Alquileres filtrados",
        formatear_entero_es(filtrado["alquileres_total"].sum()),
    )
    media_filtrada = (
        float(filtrado["alquileres_total"].mean()) if len(filtrado) > 0 else 0.0
    )
    mediana_filtrada = (
        float(filtrado["alquileres_total"].median())
        if len(filtrado) > 0
        else 0.0
    )
    col_e3.metric(
        "Promedio filtrado",
        f"{formatear_decimal_es(media_filtrada)} alq./h",
    )
    col_e4.metric(
        "Mediana filtrada",
        f"{formatear_decimal_es(mediana_filtrada, 1)} alq./h",
    )

    with st.expander("Ver bitácora de transformaciones y diccionario de variables"):
        st.markdown("**Bitácora de transformaciones AE3**")
        st.dataframe(
            repositorio["bitacora_transformaciones"],
            hide_index=True,
            width="stretch",
        )
        st.markdown("**Diccionario de variables del dataset preparado**")
        st.dataframe(
            repositorio["diccionario_variables"],
            hide_index=True,
            width="stretch",
        )


def renderizar_conclusiones_y_limitaciones(indicadores: dict) -> None:
    """Sección 6: síntesis final, recomendaciones, limitaciones y catálogo."""
    st.header("6. Conclusiones, recomendaciones y limitaciones")

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.subheader("Conclusiones principales")
        st.markdown(
            f"""
            1. **Diferencia estructural entre calendarios (P1):** los días
               laborables exhiben un perfil bimodal con picos a las **08:00**
               (477,01 alq./h) y **17:00**
               (**{formatear_decimal_es(indicadores['pico_laborable_promedio'])}**
               alq./h, mediana 539,0), mientras que los días no laborables
               presentan una curva unimodal centrada en las **13:00**
               (**{formatear_decimal_es(indicadores['pico_no_laborable_promedio'])}**
               alq./h, mediana 367,0).
            2. **Concentración por franjas (P2):** la franja **12 a 17** lidera
               en ambos tipos de día (**34,84 %** en laborables; **49,39 %** en
               no laborables). Aunque el volumen acumulado es mayor en
               laborables (798.696 vs. 494.046), la intensidad media horaria de
               `12 a 17` es superior en no laborables (**356,45** vs.
               **267,21** alq./h).
            3. **Estabilidad horaria interanual (P3):** las horas pico (17:00
               laborable y 13:00 no laborable) se mantienen exactamente iguales
               en 2011 y 2012, pese a un incremento interanual de +66,16 % y
               +60,57 % en sus respectivos promedios máximos.
            4. **Trazabilidad completa:** los **3.292.679** alquileres y
               **17.379** registros se conservan intactos entre el dataset
               preparado, los notebooks, los CSV, el informe PDF y esta app.
            """
        )

    with col_res2:
        st.subheader("Recomendaciones operativas (escenario hipotético)")
        st.markdown(
            """
            - **Diferenciar revisiones por tipo de día:** planificar esquemas
              de seguimiento distintos para jornadas laborables (énfasis en
              07:00–09:00 y 17:00–19:00) y no laborables (énfasis sostenido en
              11:00–17:00).
            - **Monitorear el nivel por periodo:** dado el salto de intensidad
              entre 2011 y 2012 con horarios pico estables, cualquier revisión
              de capacidad debe actualizarse periódicamente con datos recientes.
            - **Información adicional necesaria antes de decidir inversiones:**
              1. Datos desagregados por **estación** (retiros, devoluciones y
                 tiempos con estación vacía o llena) para medir demanda no
                 atendida.
              2. **Tarifas, estructura de membresías y costos operativos** para
                 evaluar ingresos y rentabilidad real por franja.
              3. **Variables meteorológicas verificadas** (tras auditar los 22
                 registros de humedad igual a cero del 10 de marzo de 2011) y
                 registros actuales de la ciudad objetivo.
            """
        )

    st.subheader("Limitaciones metodológicas y distinción económica")
    st.markdown(
        """
        <div class="tarjeta-alerta">
        <strong>Distinción entre volumen, ingresos y rentabilidad:</strong>
        este análisis cuantifica <em>alquileres registrados</em> (volumen
        físico). No contiene tarifas ni ingresos monetarios; además, incluso si
        se conocieran los ingresos, estos no equivalen a rentabilidad porque no
        se dispone de costos de operación, mantenimiento, personal ni logística
        de redistribución en horas pico.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        - **Alcance descriptivo, no causal:** los resultados describen patrones
          observados, pero no demuestran causas de las diferencias horarias ni
          del crecimiento de 2012 frente a 2011.
        - **165 horas sin registro (0,94 % de la cuadrícula nominal):**
          concentradas en madrugada (02:00–05:00) y en 2011. No se imputan como
          cero alquileres; informar cobertura transparenta el límite, pero no
          elimina el posible sesgo.
        - **Agregación del sistema y antigüedad:** los datos resumen todo
          Washington D. C. entre 2011 y 2012, por lo que no permiten
          extrapolar directamente a estaciones concretas, a la operación actual
          ni a ciudades de Colombia.
        """
    )

    st.subheader("Catálogo consolidado de métricas AE4")
    st.dataframe(obtener_catalogo_metricas(), hide_index=True, width="stretch")


def main() -> None:
    """Configura y ejecuta la aplicación de Streamlit."""
    st.set_page_config(
        page_title="AE4 — Analítica de Bicicletas (Capital Bikeshare)",
        page_icon="🚲",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    aplicar_estilos_aplicacion()
    repositorio = obtener_repositorio_en_cache()
    indicadores = calcular_indicadores_generales(repositorio)

    mostrar_encabezado_principal()
    seccion_elegida = renderizar_barra_lateral(indicadores)

    if seccion_elegida == SECCIONES_NAVEGACION[0]:
        renderizar_contexto_y_dataset(repositorio, indicadores)
    elif seccion_elegida == SECCIONES_NAVEGACION[1]:
        renderizar_pregunta_p1(repositorio, indicadores)
    elif seccion_elegida == SECCIONES_NAVEGACION[2]:
        renderizar_pregunta_p2(repositorio, indicadores)
    elif seccion_elegida == SECCIONES_NAVEGACION[3]:
        renderizar_pregunta_p3(repositorio, indicadores)
    elif seccion_elegida == SECCIONES_NAVEGACION[4]:
        renderizar_calidad_y_verificacion(repositorio)
    else:
        renderizar_conclusiones_y_limitaciones(indicadores)


if __name__ == "__main__":
    main()
