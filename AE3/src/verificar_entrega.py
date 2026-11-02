"""Verifica los CSV publicados, sus cálculos y las salidas del notebook AE3."""
from pathlib import Path
import hashlib
import json

import nbformat
import pandas as pd


def main():
    raiz = Path(__file__).resolve().parents[2]
    base = raiz / "AE3"
    informe = json.loads((base / "resultados/validaciones.json").read_text(encoding="utf-8"))
    for archivo in informe["archivos"]:
        path = raiz / archivo["ruta"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == archivo["sha256"], path
    df = pd.read_csv(base / "datos/dataset_preparado.csv", parse_dates=["fecha", "fecha_hora"])
    assert df.shape == (17379, 11)
    assert not df.isna().any().any()
    assert df["fecha_hora"].is_unique
    assert df["fecha_hora"].eq(df["fecha"] + pd.to_timedelta(df["hora"], unit="h")).all()
    assert df["alquileres_total"].eq(df["alquileres_ocasionales"] + df["alquileres_registrados"]).all()
    assert df["alquileres_total"].sum() == informe["alquileres_total"]
    for nombre, claves in [
        ("p1_perfil_horario", ["tipo_dia", "hora"]),
        ("p2_franjas", ["tipo_dia", "franja_horaria"]),
        ("p3_perfil_anual", ["anio", "tipo_dia", "hora"]),
    ]:
        tabla = pd.read_csv(base / "resultados" / (nombre + ".csv"))
        assert not tabla.duplicated(claves).any()
        assert tabla["alquileres_total"].sum() == df["alquileres_total"].sum()
        assert tabla["horas_observadas"].sum() == len(df)
        assert tabla["horas_sin_registro"].sum() == informe["horas_sin_registro"]
        for _, fila in tabla.iterrows():
            mascara = pd.Series(True, index=df.index)
            for clave in claves:
                mascara &= df[clave].eq(fila[clave])
            grupo = df.loc[mascara, "alquileres_total"]
            assert len(grupo) == fila["horas_observadas"]
            assert int(grupo.sum()) == fila["alquileres_total"]
            assert abs(grupo.mean() - fila["promedio_alquileres_por_hora"]) < 1e-9
            assert abs(grupo.median() - fila["mediana_alquileres_por_hora"]) < 1e-9
            assert abs(fila["cobertura_pct"] - fila["horas_observadas"] / fila["horas_esperadas"] * 100) < 1e-9
        if nombre == "p2_franjas":
            totales = df.groupby("tipo_dia")["alquileres_total"].sum()
            for _, fila in tabla.iterrows():
                assert abs(fila["participacion_alquileres_pct"] - fila["alquileres_total"] / totales[fila["tipo_dia"]] * 100) < 1e-9
            assert tabla.groupby("tipo_dia")["participacion_alquileres_pct"].sum().sub(100).abs().lt(1e-9).all()
    texto = (base / "resultados/resumen_dataframe_transformado.txt").read_text(encoding="utf-8")
    assert f"Filas: {len(df)}" in texto and f"Columnas: {len(df.columns)}" in texto
    assert f"Total alquileres: {df['alquileres_total'].sum()}" in texto
    nb = nbformat.read(base / "notebooks/02_transformacion_enriquecimiento.ipynb", as_version=4)
    nbformat.validate(nb)
    celdas = [c for c in nb.cells if c.cell_type == "code"]
    assert [c.execution_count for c in celdas] == list(range(1, len(celdas) + 1))
    assert all(c.outputs for c in celdas)
    assert not [o for c in celdas for o in c.outputs if o.output_type == "error"]
    print(f"AE3 verificado: {len(celdas)} celdas ejecutadas sin errores, CSV y TXT consistentes.")
    print("Medias, medianas, conteos, sumas, cobertura y participaciones comprobados desde el CSV preparado.")


if __name__ == "__main__":
    main()
