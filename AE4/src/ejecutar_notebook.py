"""Ejecuta y guarda el notebook AE4 usando el mismo Python que invoca el script.

Uso desde la raíz del repositorio:
    .venv\\Scripts\\python.exe AE4/src/ejecutar_notebook.py
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

import nbformat
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
from nbclient import NotebookClient


def ejecutar_notebook_ae4(desde_notebooks: bool = False) -> Path:
    """Ejecuta el notebook de métricas y visualizaciones AE4 y valida salidas."""
    ruta_raiz = Path(__file__).resolve().parents[2]
    ruta_notebook = (
        ruta_raiz / "AE4" / "notebooks" / "03_metricas_y_visualizaciones.ipynb"
    )
    notebook = nbformat.read(ruta_notebook, as_version=4)
    nbformat.validate(notebook)
    directorio_trabajo = ruta_notebook.parent if desde_notebooks else ruta_raiz

    with tempfile.TemporaryDirectory(prefix="ae4-kernel-") as directorio_tmp:
        carpeta_kernel = Path(directorio_tmp) / "python3"
        carpeta_kernel.mkdir()
        especificacion_kernel = {
            "argv": [
                sys.executable,
                "-m",
                "ipykernel_launcher",
                "-f",
                "{connection_file}",
            ],
            "display_name": "Python 3 (AE4)",
            "language": "python",
        }
        (carpeta_kernel / "kernel.json").write_text(
            json.dumps(especificacion_kernel),
            encoding="utf-8",
        )
        gestor_kernel = KernelManager(
            kernel_name="python3",
            kernel_spec_manager=KernelSpecManager(
                kernel_dirs=[directorio_tmp]
            ),
        )
        cliente = NotebookClient(
            notebook,
            km=gestor_kernel,
            timeout=300,
            resources={"metadata": {"path": str(directorio_trabajo)}},
            allow_errors=False,
        )
        try:
            cliente.execute()
        finally:
            if gestor_kernel.has_kernel:
                gestor_kernel.shutdown_kernel(now=True)

    nbformat.validate(notebook)
    errores = [
        salida
        for celda in notebook.cells
        if celda.cell_type == "code"
        for salida in celda.outputs
        if salida.output_type == "error"
    ]
    if errores:
        raise RuntimeError("El notebook AE4 contiene errores de ejecución.")

    ruta_notebook.write_text(
        nbformat.writes(notebook), encoding="utf-8", newline="\n"
    )
    cantidad_celdas = sum(
        celda.cell_type == "code" for celda in notebook.cells
    )
    print(
        "Notebook ejecutado y guardado: "
        f"{ruta_notebook.relative_to(ruta_raiz).as_posix()}"
    )
    print(f"Celdas de código ejecutadas sin errores: {cantidad_celdas}")
    return ruta_notebook


def main() -> None:
    """Procesa argumentos de consola y ejecuta el notebook AE4."""
    analizador = argparse.ArgumentParser(description=__doc__)
    analizador.add_argument("--desde-notebooks", action="store_true")
    argumentos = analizador.parse_args()
    ejecutar_notebook_ae4(desde_notebooks=argumentos.desde_notebooks)


if __name__ == "__main__":
    main()
