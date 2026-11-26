"""Generación de figuras estáticas de alta resolución (300 DPI) para el PDF AE4.

Todas las figuras se calculan directamente desde los archivos preparados de AE3
con la misma paleta cromática y definiciones usadas en la aplicación Streamlit.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from AE4.src.metricas_y_graficos import (
    COLORES_ANIO,
    COLORES_ANIO_NO_LABORABLE,
    COLORES_TIPO_DIA,
    ORDEN_TIPOS_DIA,
    calcular_brecha_horaria_p1,
    calcular_resumen_interanual_p3,
    cargar_datos_proyecto,
    formatear_decimal_es,
    formatear_entero_es,
    obtener_raiz_proyecto,
)

matplotlib.use("Agg")

NOTA_FUENTE = (
    "Fuente: elaboración propia a partir de AE3 "
    "(t22000t/bike-sharing-tabular, Capital Bikeshare UCI, 2011–2012)."
)


def _configurar_estilo_matplotlib() -> None:
    """Configura la tipografía y apariencia editorial de Matplotlib."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.titlesize": 11.5,
            "axes.titleweight": "bold",
            "axes.labelsize": 9.5,
            "axes.edgecolor": "#CBD5E1",
            "axes.facecolor": "#F8FAFC",
            "figure.facecolor": "#FFFFFF",
            "grid.color": "#E2E8F0",
            "grid.linestyle": "-",
            "grid.linewidth": 0.7,
            "xtick.color": "#334155",
            "ytick.color": "#334155",
        }
    )


def _guardar_figura(figura: plt.Figure, ruta_salida: Path) -> Path:
    """Guarda la figura a 300 DPI y libera la memoria asociada."""
    figura.savefig(ruta_salida, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(figura)
    return ruta_salida


def generar_todas_las_figuras(ruta_raiz: Path | None = None) -> list[Path]:
    """Genera las seis figuras de AE4 en AE4/resultados/figuras/."""
    _configurar_estilo_matplotlib()
    repositorio = cargar_datos_proyecto(ruta_raiz)
    raiz = repositorio["ruta_raiz"]
    carpeta_figuras = raiz / "AE4" / "resultados" / "figuras"
    carpeta_figuras.mkdir(parents=True, exist_ok=True)

    tabla_p1 = repositorio["tabla_p1"]
    tabla_p2 = repositorio["tabla_p2"]
    tabla_p3 = repositorio["tabla_p3"]
    tabla_brecha = calcular_brecha_horaria_p1(tabla_p1)
    _, comparacion_anual = calcular_resumen_interanual_p3(tabla_p3)

    rutas_generadas = [
        _figura_01_p1_perfil(tabla_p1, carpeta_figuras),
        _figura_02_p1_brecha_y_cobertura(tabla_brecha, carpeta_figuras),
        _figura_03_p2_franjas(tabla_p2, carpeta_figuras),
        _figura_04_p3_perfiles_anuales(tabla_p3, carpeta_figuras),
        _figura_05_p3_cambio_picos(comparacion_anual, carpeta_figuras),
        _figura_06_cobertura_ausencias(tabla_p3, carpeta_figuras),
    ]
    return rutas_generadas


def _figura_01_p1_perfil(tabla_p1, carpeta_figuras: Path) -> Path:
    """Figura 1: Perfil horario de promedio y mediana por tipo de día (P1)."""
    figura, eje = plt.subplots(figsize=(9.5, 4.6))

    for tipo_dia in ORDEN_TIPOS_DIA:
        subtabla = tabla_p1[tabla_p1["tipo_dia"].eq(tipo_dia)].sort_values(
            "hora"
        )
        color_serie = COLORES_TIPO_DIA[tipo_dia]
        eje.plot(
            subtabla["hora"],
            subtabla["promedio_alquileres_por_hora"],
            marker="o",
            markersize=4.5,
            linewidth=2.4,
            color=color_serie,
            label=f"{tipo_dia} — Promedio",
        )
        eje.plot(
            subtabla["hora"],
            subtabla["mediana_alquileres_por_hora"],
            linestyle=":",
            linewidth=1.8,
            color=color_serie,
            label=f"{tipo_dia} — Mediana",
        )

    pico_lab = tabla_p1[
        tabla_p1["tipo_dia"].eq("Laborable") & tabla_p1["hora"].eq(17)
    ].iloc[0]
    pico_manana = tabla_p1[
        tabla_p1["tipo_dia"].eq("Laborable") & tabla_p1["hora"].eq(8)
    ].iloc[0]
    pico_nolab = tabla_p1[
        tabla_p1["tipo_dia"].eq("No laborable") & tabla_p1["hora"].eq(13)
    ].iloc[0]

    texto_pico_lab = formatear_decimal_es(
        pico_lab["promedio_alquileres_por_hora"]
    )
    texto_pico_manana = formatear_decimal_es(
        pico_manana["promedio_alquileres_por_hora"]
    )
    texto_pico_nolab = formatear_decimal_es(
        pico_nolab["promedio_alquileres_por_hora"]
    )

    eje.annotate(
        f"Pico laborable 17:00\n{texto_pico_lab} alq./h",
        xy=(17, pico_lab["promedio_alquileres_por_hora"]),
        xytext=(18.4, 540),
        fontsize=8.3,
        fontweight="bold",
        color="#0F766E",
        bbox={"boxstyle": "round,pad=0.3", "fc": "#ECFDF5", "ec": "#0F766E"},
        arrowprops={"arrowstyle": "->", "color": "#0F766E", "lw": 1.1},
    )
    eje.annotate(
        f"Pico mañana 08:00\n{texto_pico_manana} alq./h",
        xy=(8, pico_manana["promedio_alquileres_por_hora"]),
        xytext=(2.2, 485),
        fontsize=8.3,
        fontweight="bold",
        color="#0F766E",
        bbox={"boxstyle": "round,pad=0.3", "fc": "#ECFDF5", "ec": "#0F766E"},
        arrowprops={"arrowstyle": "->", "color": "#0F766E", "lw": 1.1},
    )
    eje.annotate(
        f"Pico no laborable 13:00\n{texto_pico_nolab} alq./h",
        xy=(13, pico_nolab["promedio_alquileres_por_hora"]),
        xytext=(10.2, 430),
        fontsize=8.3,
        fontweight="bold",
        color="#B45309",
        bbox={"boxstyle": "round,pad=0.3", "fc": "#FFFBEB", "ec": "#D97706"},
        arrowprops={"arrowstyle": "->", "color": "#D97706", "lw": 1.1},
    )

    eje.set_title(
        "P1 — Perfil horario de alquileres registrados por tipo de día (2011–2012)",
        pad=22,
        loc="left",
    )
    eje.set_xlabel("Hora del día (00:00 a 23:00)")
    eje.set_ylabel("Alquileres por hora registrada")
    eje.set_xticks(range(24))
    eje.set_xticklabels([f"{hora:02d}" for hora in range(24)])
    eje.set_ylim(0, 610)
    eje.grid(True, axis="y")
    eje.spines["top"].set_visible(False)
    eje.spines["right"].set_visible(False)
    eje.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.10),
        ncol=4,
        frameon=False,
        fontsize=8.5,
    )
    figura.text(0.01, -0.02, NOTA_FUENTE, fontsize=7.8, color="#64748B")
    return _guardar_figura(
        figura, carpeta_figuras / "fig01_p1_perfil_horario_media_mediana.png"
    )


def _figura_02_p1_brecha_y_cobertura(
    tabla_brecha, carpeta_figuras: Path
) -> Path:
    """Figura 2: Brecha horaria Laborable − No laborable y cobertura."""
    figura, (eje_superior, eje_inferior) = plt.subplots(
        2,
        1,
        figsize=(9.5, 5.4),
        sharex=True,
        gridspec_kw={"height_ratios": [2.2, 1.0]},
    )

    colores = [
        COLORES_TIPO_DIA["Laborable"]
        if valor >= 0
        else COLORES_TIPO_DIA["No laborable"]
        for valor in tabla_brecha["brecha_promedio"]
    ]
    eje_superior.bar(
        tabla_brecha["hora"],
        tabla_brecha["brecha_promedio"],
        color=colores,
        width=0.72,
    )
    eje_superior.axhline(0, color="#334155", linewidth=1.1)
    eje_superior.set_title(
        "P1 — Brecha horaria (Laborable − No laborable) y cobertura nominal (2011–2012)",
        loc="left",
        pad=12,
    )
    eje_superior.set_ylabel("Diferencia de promedio\n(alq./hora registrada)")
    eje_superior.set_ylim(-245, 425)
    eje_superior.grid(True, axis="y")
    eje_superior.spines["top"].set_visible(False)
    eje_superior.spines["right"].set_visible(False)

    eje_superior.annotate(
        "+371,35 alq./h (08:00)",
        xy=(8, 371.35),
        xytext=(9.8, 345),
        fontsize=8.0,
        fontweight="bold",
        color="#0F766E",
        bbox={"boxstyle": "round,pad=0.25", "fc": "#ECFDF5", "ec": "#0F766E"},
        arrowprops={"arrowstyle": "->", "color": "#0F766E", "lw": 1.0},
    )
    eje_superior.annotate(
        "-181,07 alq./h (14:00)",
        xy=(14, -181.07),
        xytext=(15.8, -218),
        fontsize=8.0,
        fontweight="bold",
        color="#B45309",
        bbox={"boxstyle": "round,pad=0.25", "fc": "#FFFBEB", "ec": "#D97706"},
        arrowprops={"arrowstyle": "->", "color": "#D97706", "lw": 1.0},
    )

    eje_inferior.plot(
        tabla_brecha["hora"],
        tabla_brecha["cobertura_laborable_pct"],
        marker="o",
        markersize=3.8,
        linewidth=1.9,
        color=COLORES_TIPO_DIA["Laborable"],
        label="Cobertura Laborable (%)",
    )
    eje_inferior.plot(
        tabla_brecha["hora"],
        tabla_brecha["cobertura_no_laborable_pct"],
        marker="s",
        markersize=3.8,
        linewidth=1.9,
        color=COLORES_TIPO_DIA["No laborable"],
        label="Cobertura No laborable (%)",
    )
    eje_inferior.set_ylabel("Cobertura (%)")
    eje_inferior.set_xlabel("Hora del día (00:00 a 23:00)")
    eje_inferior.set_ylim(92, 101.2)
    eje_inferior.set_xticks(range(24))
    eje_inferior.set_xticklabels([f"{hora:02d}" for hora in range(24)])
    eje_inferior.grid(True, axis="y")
    eje_inferior.spines["top"].set_visible(False)
    eje_inferior.spines["right"].set_visible(False)
    eje_inferior.legend(loc="lower right", frameon=True, fontsize=8.0)

    figura.tight_layout()
    figura.text(0.01, -0.02, NOTA_FUENTE, fontsize=7.8, color="#64748B")
    return _guardar_figura(
        figura, carpeta_figuras / "fig02_p1_brecha_y_cobertura_horaria.png"
    )


def _figura_03_p2_franjas(tabla_p2, carpeta_figuras: Path) -> Path:
    """Figura 3: Participación (%) y volumen acumulado por franja (P2)."""
    figura, (eje_izq, eje_der) = plt.subplots(1, 2, figsize=(10.6, 4.6))
    posiciones = np.arange(4)
    ancho = 0.39

    for indice, tipo_dia in enumerate(ORDEN_TIPOS_DIA):
        subtabla = tabla_p2[tabla_p2["tipo_dia"].eq(tipo_dia)].sort_values(
            "orden_franja"
        )
        desplazamiento = -ancho / 2 if indice == 0 else ancho / 2
        color_serie = COLORES_TIPO_DIA[tipo_dia]

        barras_pct = eje_izq.bar(
            posiciones + desplazamiento,
            subtabla["participacion_alquileres_pct"],
            width=ancho * 0.92,
            color=color_serie,
            label=tipo_dia,
        )
        for barra, valor_pct in zip(
            barras_pct, subtabla["participacion_alquileres_pct"]
        ):
            eje_izq.text(
                barra.get_x() + barra.get_width() / 2,
                valor_pct + 1.1,
                f"{formatear_decimal_es(valor_pct)}%",
                ha="center",
                va="bottom",
                fontsize=7.3,
                fontweight="bold",
                color="#1E293B",
            )

        barras_vol = eje_der.bar(
            posiciones + desplazamiento,
            subtabla["alquileres_total"] / 1000.0,
            width=ancho * 0.92,
            color=color_serie,
            label=tipo_dia,
        )
        for barra, total_alq, media_hora in zip(
            barras_vol,
            subtabla["alquileres_total"],
            subtabla["promedio_alquileres_por_hora"],
        ):
            eje_der.text(
                barra.get_x() + barra.get_width() / 2,
                total_alq / 1000.0 + 14.0,
                f"{formatear_decimal_es(total_alq / 1000.0, 1)}k\n"
                f"({formatear_decimal_es(media_hora, 0)}/h)",
                ha="center",
                va="bottom",
                fontsize=7.1,
                color="#1E293B",
            )

    etiquetas_franja = ["00 a 05", "06 a 11", "12 a 17", "18 a 23"]
    eje_izq.set_title("Participación dentro de cada tipo de día (%)", pad=10)
    eje_izq.set_xticks(posiciones)
    eje_izq.set_xticklabels(etiquetas_franja)
    eje_izq.set_xlabel("Franja horaria (intervalos de 6 h)")
    eje_izq.set_ylabel("Participación (%)")
    eje_izq.set_ylim(0, 58)
    eje_izq.grid(True, axis="y")
    eje_izq.spines["top"].set_visible(False)
    eje_izq.spines["right"].set_visible(False)

    eje_der.set_title("Volumen acumulado (miles) y promedio/h", pad=10)
    eje_der.set_xticks(posiciones)
    eje_der.set_xticklabels(etiquetas_franja)
    eje_der.set_xlabel("Franja horaria (intervalos de 6 h)")
    eje_der.set_ylabel("Miles de alquileres (2011–2012)")
    eje_der.set_ylim(0, 960)
    eje_der.grid(True, axis="y")
    eje_der.spines["top"].set_visible(False)
    eje_der.spines["right"].set_visible(False)

    handles, labels = eje_izq.get_legend_handles_labels()
    figura.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.03),
        ncol=2,
        frameon=False,
        fontsize=9.2,
    )
    figura.suptitle(
        "P2 — Distribución de alquileres por franjas de seis horas (2011–2012)",
        x=0.01,
        y=1.08,
        ha="left",
        fontsize=11.8,
        fontweight="bold",
    )
    figura.tight_layout()
    figura.text(0.01, -0.03, NOTA_FUENTE, fontsize=7.8, color="#64748B")
    return _guardar_figura(
        figura, carpeta_figuras / "fig03_p2_participacion_y_volumen_franjas.png"
    )


def _figura_04_p3_perfiles_anuales(tabla_p3, carpeta_figuras: Path) -> Path:
    """Figura 4: Perfiles horarios comparados 2011 vs. 2012 por tipo (P3)."""
    figura, ejes = plt.subplots(1, 2, figsize=(10.0, 4.4), sharey=True)

    for indice, tipo_dia in enumerate(ORDEN_TIPOS_DIA):
        eje = ejes[indice]
        paleta = (
            COLORES_ANIO
            if tipo_dia == "Laborable"
            else COLORES_ANIO_NO_LABORABLE
        )
        for anio in [2011, 2012]:
            subtabla = tabla_p3[
                tabla_p3["tipo_dia"].eq(tipo_dia) & tabla_p3["anio"].eq(anio)
            ].sort_values("hora")
            estilo = "-" if anio == 2012 else "--"
            grosor = 2.4 if anio == 2012 else 1.9
            eje.plot(
                subtabla["hora"],
                subtabla["promedio_alquileres_por_hora"],
                linestyle=estilo,
                linewidth=grosor,
                marker="o",
                markersize=3.6,
                color=paleta[anio],
                label=f"Año {anio}",
            )
            pico = subtabla[subtabla["rango_promedio"].eq(1)].iloc[0]
            eje.scatter(
                [int(pico["hora"])],
                [float(pico["promedio_alquileres_por_hora"])],
                s=65,
                marker="D",
                color=paleta[anio],
                edgecolor="white",
                linewidth=1.1,
                zorder=5,
            )
            posiciones_nota = {
                ("Laborable", 2012): (9.5, 678),
                ("Laborable", 2011): (9.3, 445),
                ("No laborable", 2012): (7.2, 540),
                ("No laborable", 2011): (13.6, 118),
            }
            coordenada_texto = posiciones_nota[(tipo_dia, anio)]
            texto_pico = (
                f"{anio}: {int(pico['hora']):02d}:00 "
                f"({formatear_decimal_es(pico['promedio_alquileres_por_hora'])})"
            )
            eje.annotate(
                texto_pico,
                xy=(
                    int(pico["hora"]),
                    float(pico["promedio_alquileres_por_hora"]),
                ),
                xytext=coordenada_texto,
                fontsize=7.8,
                fontweight="bold",
                color=paleta[anio],
                bbox={
                    "boxstyle": "round,pad=0.25",
                    "fc": "#FFFFFF",
                    "ec": paleta[anio],
                    "alpha": 0.95,
                },
                arrowprops={"arrowstyle": "->", "color": paleta[anio], "lw": 1.0},
            )

        eje.set_title(f"Días {tipo_dia.lower()}s", pad=10)
        eje.set_xlabel("Hora del día (00 a 23)")
        eje.set_xticks(range(0, 24, 2))
        eje.set_xticklabels([f"{hora:02d}" for hora in range(0, 24, 2)])
        eje.set_ylim(0, 740)
        eje.grid(True, axis="y")
        eje.spines["top"].set_visible(False)
        eje.spines["right"].set_visible(False)
        eje.legend(loc="upper left", frameon=True, fontsize=8.3)

    ejes[0].set_ylabel("Promedio (alquileres / hora registrada)")
    figura.suptitle(
        "P3 — Comparación de perfiles horarios entre 2011 y 2012 por tipo de día",
        x=0.01,
        y=1.03,
        ha="left",
        fontsize=11.8,
        fontweight="bold",
    )
    figura.tight_layout()
    figura.text(0.01, -0.03, NOTA_FUENTE, fontsize=7.8, color="#64748B")
    return _guardar_figura(
        figura, carpeta_figuras / "fig04_p3_comparacion_anual_perfiles.png"
    )


def _figura_05_p3_cambio_picos(
    comparacion_anual, carpeta_figuras: Path
) -> Path:
    """Figura 5: Comparación de picos y volumen total anual (2011 vs. 2012)."""
    figura, (eje_izq, eje_der) = plt.subplots(1, 2, figsize=(9.6, 4.2))
    posiciones = np.arange(len(comparacion_anual))
    ancho = 0.34
    etiquetas_x = [
        f"{fila['tipo_dia']}\n(pico {int(fila['hora_pico_2012']):02d}:00)"
        for _, fila in comparacion_anual.iterrows()
    ]

    barras_11 = eje_izq.bar(
        posiciones - ancho / 2,
        comparacion_anual["promedio_pico_2011"],
        width=ancho,
        color="#64748B",
        label="2011",
    )
    barras_12 = eje_izq.bar(
        posiciones + ancho / 2,
        comparacion_anual["promedio_pico_2012"],
        width=ancho,
        color="#0F766E",
        label="2012",
    )
    for barra, valor in zip(barras_11, comparacion_anual["promedio_pico_2011"]):
        eje_izq.text(
            barra.get_x() + barra.get_width() / 2,
            valor + 12,
            f"{formatear_decimal_es(valor)}",
            ha="center",
            va="bottom",
            fontsize=8.2,
        )
    for barra, valor, cambio in zip(
        barras_12,
        comparacion_anual["promedio_pico_2012"],
        comparacion_anual["cambio_pico_pct"],
    ):
        eje_izq.text(
            barra.get_x() + barra.get_width() / 2,
            valor + 12,
            f"{formatear_decimal_es(valor)}\n(+{formatear_decimal_es(cambio)} %)",
            ha="center",
            va="bottom",
            fontsize=8.0,
            fontweight="bold",
            color="#0F766E",
        )

    eje_izq.set_title("Promedio en la hora de mayor volumen", pad=10)
    eje_izq.set_ylabel("Alquileres / hora registrada")
    eje_izq.set_xticks(posiciones)
    eje_izq.set_xticklabels(etiquetas_x)
    eje_izq.set_ylim(0, 790)
    eje_izq.grid(True, axis="y")
    eje_izq.spines["top"].set_visible(False)
    eje_izq.spines["right"].set_visible(False)

    etiquetas_tipo = comparacion_anual["tipo_dia"].tolist()
    vol_11 = comparacion_anual["total_anual_2011"] / 1_000_000.0
    vol_12 = comparacion_anual["total_anual_2012"] / 1_000_000.0
    barras_v11 = eje_der.bar(
        posiciones - ancho / 2, vol_11, width=ancho, color="#64748B", label="2011"
    )
    barras_v12 = eje_der.bar(
        posiciones + ancho / 2, vol_12, width=ancho, color="#D97706", label="2012"
    )
    for barra, total_real in zip(
        barras_v11, comparacion_anual["total_anual_2011"]
    ):
        eje_der.text(
            barra.get_x() + barra.get_width() / 2,
            total_real / 1_000_000.0 + 0.03,
            formatear_entero_es(total_real),
            ha="center",
            va="bottom",
            fontsize=7.8,
        )
    for barra, total_real, cambio in zip(
        barras_v12,
        comparacion_anual["total_anual_2012"],
        comparacion_anual["cambio_total_anual_pct"],
    ):
        eje_der.text(
            barra.get_x() + barra.get_width() / 2,
            total_real / 1_000_000.0 + 0.03,
            f"{formatear_entero_es(total_real)}\n(+{formatear_decimal_es(cambio)} %)",
            ha="center",
            va="bottom",
            fontsize=7.8,
            fontweight="bold",
            color="#B45309",
        )

    eje_der.set_title("Volumen anual acumulado por tipo de día", pad=10)
    eje_der.set_ylabel("Millones de alquileres")
    eje_der.set_xticks(posiciones)
    eje_der.set_xticklabels(etiquetas_tipo)
    eje_der.set_ylim(0, 1.72)
    eje_der.grid(True, axis="y")
    eje_der.spines["top"].set_visible(False)
    eje_der.spines["right"].set_visible(False)
    eje_izq.legend(loc="upper right", frameon=True, fontsize=8.3)
    eje_der.legend(loc="upper right", frameon=True, fontsize=8.3)

    figura.suptitle(
        "P3 — Variación interanual de intensidad pico y volumen total (2011 vs. 2012)",
        x=0.01,
        y=1.03,
        ha="left",
        fontsize=11.6,
        fontweight="bold",
    )
    figura.tight_layout()
    figura.text(0.01, -0.03, NOTA_FUENTE, fontsize=7.8, color="#64748B")
    return _guardar_figura(
        figura, carpeta_figuras / "fig05_p3_variacion_interanual_maximos.png"
    )


def _figura_06_cobertura_ausencias(tabla_p3, carpeta_figuras: Path) -> Path:
    """Figura 6: Mapa de calor de las 165 horas sin registro en la cuadrícula."""
    tabla_auxiliar = tabla_p3.copy()
    tabla_auxiliar["grupo"] = (
        tabla_auxiliar["anio"].astype(str)
        + " — "
        + tabla_auxiliar["tipo_dia"].astype(str)
    )
    orden_grupos = [
        "2011 — Laborable",
        "2011 — No laborable",
        "2012 — Laborable",
        "2012 — No laborable",
    ]
    matriz = tabla_auxiliar.pivot(
        index="grupo", columns="hora", values="horas_sin_registro"
    ).reindex(orden_grupos)

    figura, eje = plt.subplots(figsize=(9.8, 3.1))
    imagen = eje.imshow(
        matriz.to_numpy(), cmap="YlOrRd", aspect="auto", vmin=0, vmax=25
    )

    for indice_fila in range(matriz.shape[0]):
        for indice_col in range(matriz.shape[1]):
            valor_celda = int(matriz.iloc[indice_fila, indice_col])
            color_texto = "#FFFFFF" if valor_celda >= 14 else "#1E293B"
            eje.text(
                indice_col,
                indice_fila,
                str(valor_celda),
                ha="center",
                va="center",
                fontsize=7.6,
                color=color_texto,
                fontweight="bold" if valor_celda > 0 else "normal",
            )

    eje.set_title(
        "Calidad y cobertura — Distribución horaria de las 165 horas sin registro (2011–2012)",
        loc="left",
        pad=10,
    )
    eje.set_xticks(range(24))
    eje.set_xticklabels([f"{hora:02d}" for hora in range(24)])
    eje.set_yticks(range(len(orden_grupos)))
    eje.set_yticklabels(orden_grupos)
    eje.set_xlabel("Hora del día (00:00 a 23:00)")
    barra_color = figura.colorbar(imagen, ax=eje, pad=0.02, shrink=0.92)
    barra_color.set_label("Horas sin registro", fontsize=8.5)

    figura.tight_layout()
    figura.text(0.01, -0.05, NOTA_FUENTE, fontsize=7.8, color="#64748B")
    return _guardar_figura(
        figura, carpeta_figuras / "fig06_cobertura_calidad_registros.png"
    )


def main() -> None:
    """Punto de entrada para regenerar todas las figuras de AE4."""
    rutas = generar_todas_las_figuras(obtener_raiz_proyecto())
    print(f"Figuras AE4 generadas ({len(rutas)}):")
    for ruta_figura in rutas:
        print(f"  - {ruta_figura.name}")


if __name__ == "__main__":
    main()
