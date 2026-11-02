"""Ejecuta y guarda el notebook AE3 usando el mismo Python que invoca el script.

Uso desde la raíz: python AE3/src/ejecutar_notebook.py
Opcional: --desde-notebooks comprueba la detección de raíz al iniciar el kernel allí.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--desde-notebooks", action="store_true")
    args = parser.parse_args()
    raiz = Path(__file__).resolve().parents[2]
    ruta = raiz / "AE3" / "notebooks" / "02_transformacion_enriquecimiento.ipynb"
    notebook = nbformat.read(ruta, as_version=4)
    nbformat.validate(notebook)
    cwd_kernel = ruta.parent if args.desde_notebooks else raiz

    # Kernelspec temporal: evita depender de otro Python instalado o registrar
    # rutas locales permanentes en el notebook entregado.
    with tempfile.TemporaryDirectory(prefix="ae3-kernel-") as directorio:
        kernel = Path(directorio) / "python3"
        kernel.mkdir()
        (kernel / "kernel.json").write_text(json.dumps({
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "Python 3 (AE3)",
            "language": "python",
        }), encoding="utf-8")
        gestor = KernelManager(
            kernel_name="python3",
            kernel_spec_manager=KernelSpecManager(kernel_dirs=[directorio]),
        )
        cliente = NotebookClient(
            notebook,
            km=gestor,
            timeout=300,
            resources={"metadata": {"path": str(cwd_kernel)}},
            allow_errors=False,
        )
        try:
            cliente.execute()
        finally:
            if gestor.has_kernel:
                gestor.shutdown_kernel(now=True)

    nbformat.validate(notebook)
    errores = [salida for celda in notebook.cells if celda.cell_type == "code"
               for salida in celda.outputs if salida.output_type == "error"]
    if errores:
        raise RuntimeError("El notebook contiene errores de ejecución.")
    if not any("application/vnd.jupyter.widget-view+json" in salida.get("data", {})
               for celda in notebook.cells for salida in celda.get("outputs", [])):
        notebook.metadata.pop("widgets", None)
    ruta.write_text(nbformat.writes(notebook), encoding="utf-8", newline="\n")
    celdas = sum(celda.cell_type == "code" for celda in notebook.cells)
    print(f"Notebook ejecutado y guardado: {ruta.relative_to(raiz).as_posix()}")
    print(f"Celdas de código ejecutadas sin errores: {celdas}")
    print("Resumen: AE3/resultados/resumen_dataframe_transformado.txt")


if __name__ == "__main__":
    main()
