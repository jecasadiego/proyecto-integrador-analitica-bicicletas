"""Verificación integral de la entrega AE4 y su coherencia con AE3.

Comprueba los datos preparados, las tablas de AE3, las métricas exportadas,
las seis figuras PNG, el notebook ejecutado, la aplicación Streamlit y el
informe final completo en PDF.

Uso desde la raíz del repositorio:
    .venv\\Scripts\\python.exe AE4/src/verificar_ae4.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import nbformat
from pypdf import PdfReader
from streamlit.testing.v1 import AppTest

RUTA_RAIZ = Path(__file__).resolve().parents[2]
if str(RUTA_RAIZ) not in sys.path:
    sys.path.insert(0, str(RUTA_RAIZ))


def verificar_figuras(ruta_raiz: Path) -> int:
    """Verifica que las seis figuras PNG de AE4 existan y no estén vacías."""
    carpeta_figuras = ruta_raiz / "AE4" / "resultados" / "figuras"
    esperadas = [
        "fig01_p1_perfil_horario_media_mediana.png",
        "fig02_p1_brecha_y_cobertura_horaria.png",
        "fig03_p2_participacion_y_volumen_franjas.png",
        "fig04_p3_comparacion_anual_perfiles.png",
        "fig05_p3_variacion_interanual_maximos.png",
        "fig06_cobertura_calidad_registros.png",
    ]
    for nombre_archivo in esperadas:
        ruta_archivo = carpeta_figuras / nombre_archivo
        assert ruta_archivo.exists(), f"Falta figura: {ruta_archivo}"
        assert ruta_archivo.stat().st_size > 10_000, (
            f"Figura demasiado pequeña: {ruta_archivo}"
        )
    return len(esperadas)


def verificar_notebook_ae4(ruta_raiz: Path) -> int:
    """Comprueba que el notebook AE4 esté ejecutado secuencialmente sin errores."""
    ruta_notebook = (
        ruta_raiz / "AE4" / "notebooks" / "03_metricas_y_visualizaciones.ipynb"
    )
    notebook = nbformat.read(ruta_notebook, as_version=4)
    nbformat.validate(notebook)
    celdas_codigo = [
        celda for celda in notebook.cells if celda.cell_type == "code"
    ]
    assert [celda.execution_count for celda in celdas_codigo] == list(
        range(1, len(celdas_codigo) + 1)
    ), "Las celdas del notebook AE4 no están ejecutadas en orden."
    assert all(
        celda.outputs for celda in celdas_codigo
    ), "Hay celdas de código sin salida en el notebook AE4."
    errores = [
        salida
        for celda in celdas_codigo
        for salida in celda.outputs
        if salida.output_type == "error"
    ]
    assert not errores, "Se encontraron errores en salidas del notebook AE4."
    return len(celdas_codigo)


def verificar_aplicacion_streamlit(ruta_raiz: Path) -> int:
    """Recorre todas las secciones de la aplicación Streamlit con AppTest."""
    secciones = [
        "1. Contexto y dataset",
        "2. P1 — Perfil horario",
        "3. P2 — Franjas de seis horas",
        "4. P3 — Estabilidad 2011 vs. 2012",
        "5. Calidad, cobertura y verificación",
        "6. Conclusiones y limitaciones",
    ]
    prueba = AppTest.from_file(
        str(ruta_raiz / "AE4" / "app" / "aplicacion_streamlit.py"),
        default_timeout=30,
    )
    prueba.run()
    assert not prueba.exception, prueba.exception
    for seccion in secciones:
        prueba.sidebar.radio[0].set_value(seccion).run()
        assert not prueba.exception, (
            f"Excepción en sección '{seccion}': {prueba.exception}"
        )
    return len(secciones)


def verificar_informe_pdf(ruta_raiz: Path) -> int:
    """Comprueba estructura, cifras clave y ausencia de marcadores vacíos en PDF."""
    ruta_pdf = ruta_raiz / "AE4" / "documento" / "informe_final_AE4.pdf"
    assert ruta_pdf.exists(), f"Falta informe PDF: {ruta_pdf}"
    lector = PdfReader(str(ruta_pdf))
    texto_completo = "\n".join(
        pagina.extract_text() or "" for pagina in lector.pages
    )
    assert len(lector.pages) >= 10, "El PDF tiene menos páginas de lo esperado."
    claves_obligatorias = [
        "3.292.679",
        "17.379",
        "525,29",
        "372,73",
        "34,84",
        "49,39",
        "656,19",
        "458,91",
        "Tabla de contenido",
        "Índice de tablas",
        "Índice de figuras",
        "rentabilidad",
        "Streamlit",
        "11 Referencias",
    ]
    for clave in claves_obligatorias:
        assert clave in texto_completo, (
            f"No se encontró el contenido esperado '{clave}' en el PDF."
        )
    paginas_indices = "\n".join(
        (pagina.extract_text() or "") for pagina in lector.pages[1:3]
    )
    lineas_sin_pagina = [
        linea.strip()
        for linea in paginas_indices.splitlines()
        if linea.strip().endswith("—")
    ]
    assert not lineas_sin_pagina, (
        f"Hay entradas de índice sin número de página: {lineas_sin_pagina}"
    )
    return len(lector.pages)


def main() -> None:
    """Ejecuta toda la batería de controles de AE4."""
    from AE4.src.metricas_y_graficos import (
        cargar_datos_proyecto,
        verificar_coherencia_datos,
    )

    repositorio = cargar_datos_proyecto(RUTA_RAIZ)
    comprobaciones = verificar_coherencia_datos(repositorio)
    assert all(
        item["estado"] for item in comprobaciones
    ), "Falló un control de coherencia AE3 ↔ AE4."

    ruta_resumen = RUTA_RAIZ / "AE4" / "resultados" / "resumen_metricas_ae4.json"
    resumen = json.loads(ruta_resumen.read_text(encoding="utf-8"))
    assert resumen["todas_las_comprobaciones_ok"] is True

    total_figuras = verificar_figuras(RUTA_RAIZ)
    total_celdas = verificar_notebook_ae4(RUTA_RAIZ)
    total_secciones = verificar_aplicacion_streamlit(RUTA_RAIZ)
    total_paginas = verificar_informe_pdf(RUTA_RAIZ)

    print("AE4 verificado correctamente:")
    print(f"  - Controles de coherencia AE3 ↔ AE4: {len(comprobaciones)} aprobados")
    print(f"  - Figuras de alta resolución: {total_figuras} PNG verificados")
    print(f"  - Notebook AE4: {total_celdas} celdas de código ejecutadas sin errores")
    print(f"  - Aplicación Streamlit: {total_secciones} secciones probadas sin excepciones")
    print(f"  - Informe final PDF: {total_paginas} páginas con índices y cifras coherentes")


if __name__ == "__main__":
    main()
