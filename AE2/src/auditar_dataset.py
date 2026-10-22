"""Contrasta el CSV de Hugging Face con UCI sin guardar datos crudos.

Ejecutar desde la raíz: python AE2/src/auditar_dataset.py
Requiere Internet, pandas y la ficha generada por el notebook.
"""

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
from urllib.request import Request, urlopen
from zipfile import ZipFile

import pandas as pd


RAIZ = Path(__file__).resolve().parents[2]
RESULTADOS = RAIZ / "AE2" / "resultados"
FICHA = RESULTADOS / "ficha_tecnica.json"
SALIDA = RESULTADOS / "auditoria_calidad.json"
URL_UCI = "https://archive.ics.uci.edu/static/public/275/bike+sharing+dataset.zip"


def descargar(url: str) -> bytes:
    solicitud = Request(url, headers={"User-Agent": "AE2-auditoria-academica/1.0"})
    with urlopen(solicitud, timeout=60) as respuesta:
        return respuesta.read()


def huella_dataframe(df: pd.DataFrame) -> str:
    """Usa exactamente el algoritmo de huella del notebook."""
    esquema = json.dumps(
        [(str(nombre), str(tipo)) for nombre, tipo in df.dtypes.items()],
        ensure_ascii=False,
    ).encode("utf-8")
    contenido = pd.util.hash_pandas_object(df, index=True).to_numpy().tobytes()
    return sha256(contenido + esquema).hexdigest()


def main() -> None:
    ficha = json.loads(FICHA.read_text(encoding="utf-8"))
    url_hf = (
        "https://huggingface.co/datasets/"
        f"{ficha['dataset_id']}/resolve/{ficha['revision']}/hour.csv"
    )
    csv_hf = descargar(url_hf)
    zip_uci = descargar(URL_UCI)
    with ZipFile(BytesIO(zip_uci)) as archivo:
        csv_uci = archivo.read("hour.csv")
        readme_uci = archivo.read("Readme.txt")

    df = pd.read_csv(BytesIO(csv_hf))
    df_uci = pd.read_csv(BytesIO(csv_uci))
    misma_copia = csv_hf == csv_uci
    mismos_datos = df.equals(df_uci)
    huella = huella_dataframe(df)
    misma_huella_notebook = huella == ficha["sha256_dataframe_y_esquema"]
    assert misma_copia, "El CSV de Hugging Face difiere del CSV oficial de UCI."
    assert mismos_datos, "Los DataFrames de Hugging Face y UCI difieren."
    assert misma_huella_notebook, "El DataFrame no coincide con la ficha del notebook."
    assert df.shape == (ficha["filas"], ficha["columnas"])

    fechas = pd.to_datetime(df["dteday"], format="%Y-%m-%d", errors="coerce")
    instantes = pd.DatetimeIndex(fechas + pd.to_timedelta(df["hr"], unit="h"))
    calendario = pd.date_range(
        fechas.min(), fechas.max() + pd.Timedelta(hours=23), freq="h"
    )
    horas_ausentes = calendario.difference(instantes)
    dia_semana = fechas.dt.day_of_week
    controles = {
        "fechas_no_interpretables": int(fechas.isna().sum()),
        "duplicados_fecha_hora": int(df.duplicated(["dteday", "hr"]).sum()),
        "filas_con_cnt_distinto_de_casual_mas_registered": int(
            (df["cnt"] != df["casual"] + df["registered"]).sum()
        ),
        "filas_con_anio_inconsistente": int((df["yr"] != fechas.dt.year - 2011).sum()),
        "filas_con_mes_inconsistente": int((df["mnth"] != fechas.dt.month).sum()),
        "filas_con_dia_semana_inconsistente": int(
            (df["weekday"] != (dia_semana + 1) % 7).sum()
        ),
        "filas_con_workingday_inconsistente": int(
            (df["workingday"] != ((dia_semana < 5) & df["holiday"].eq(0)).astype(int)).sum()
        ),
        "filas_con_conteos_negativos": int(
            df[["casual", "registered", "cnt"]].lt(0).any(axis=1).sum()
        ),
    }
    ceros = {
        nombre: int(cantidad)
        for nombre, cantidad in df.select_dtypes(include="number").eq(0).sum().items()
    }
    estadisticas = {
        nombre: {
            "minimo": int(df[nombre].min()),
            "maximo": int(df[nombre].max()),
            "promedio": float(df[nombre].mean()),
            "mediana": float(df[nombre].median()),
            "suma": int(df[nombre].sum()),
        }
        for nombre in ("cnt", "casual", "registered")
    }
    reporte = {
        "fecha_auditoria": datetime.now(timezone(timedelta(hours=-5))).isoformat(timespec="seconds"),
        "zona_horaria": "America/Bogota",
        "metodo": "Descarga nueva en memoria mediante urllib; no guarda CSV ni ZIP.",
        "dataset_id": ficha["dataset_id"],
        "revision_hugging_face": ficha["revision"],
        "configuracion": ficha["configuracion"],
        "split": ficha["split"],
        "muestra": False,
        "fuentes": {
            "hugging_face": {
                "url": url_hf,
                "archivo": "hour.csv",
                "bytes": len(csv_hf),
                "sha256_csv": sha256(csv_hf).hexdigest(),
            },
            "uci": {
                "url": URL_UCI,
                "archivo_dentro_del_zip": "hour.csv",
                "bytes_csv": len(csv_uci),
                "sha256_csv": sha256(csv_uci).hexdigest(),
                "bytes_zip": len(zip_uci),
                "sha256_zip": sha256(zip_uci).hexdigest(),
                "diccionario_consultado": "Readme.txt del mismo ZIP",
                "sha256_readme": sha256(readme_uci).hexdigest(),
            },
        },
        "identidad": {
            "csv_identicos_byte_a_byte": misma_copia,
            "dataframes_identicos": mismos_datos,
            "sha256_dataframe_y_esquema": huella,
            "coincide_con_huella_del_notebook": misma_huella_notebook,
            "ficha_contrastada": FICHA.relative_to(RAIZ).as_posix(),
            "version_pandas": pd.__version__,
        },
        "filas": len(df),
        "columnas": len(df.columns),
        "nulos_por_variable": {nombre: int(n) for nombre, n in df.isna().sum().items()},
        "ceros_por_variable_numerica": ceros,
        "estadisticas_conteos": estadisticas,
        "coherencia": controles,
        "cobertura": {
            "fecha_inicial": fechas.min().strftime("%Y-%m-%d"),
            "fecha_final": fechas.max().strftime("%Y-%m-%d"),
            "horas_calendario": len(calendario),
            "horas_observadas_distintas": int(instantes.nunique()),
            "horas_sin_registro": len(horas_ausentes),
            "horas_sin_registro_por_anio": {
                str(int(anio)): int(n)
                for anio, n in horas_ausentes.year.value_counts().sort_index().items()
            },
            "tratamiento": "No se agregan filas ni se rellenan horas ausentes con cero.",
        },
        "humedad_cero_por_fecha": {
            str(fecha): int(n)
            for fecha, n in df.loc[df["hum"].eq(0), "dteday"].value_counts().sort_index().items()
        },
        "interpretacion_de_ceros": {
            "valores_nulos_y_controles": "Cero significa ausencia de incidencias en la comprobación, no cero alquileres.",
            "yr": "0 representa 2011, según el diccionario original.",
            "hr": "0 representa la hora 00, según el intervalo 0–23 documentado.",
            "holiday": "0 identifica un día no festivo.",
            "weekday": "0 corresponde a domingo; comprobado contra dteday en todas las filas. El README original no enumera los códigos.",
            "workingday": "0 corresponde a fin de semana o festivo, según el diccionario original.",
            "casual_y_registered": "Un grupo puede tener cero alquileres aunque el total cnt sea positivo.",
            "meteorologia": "atemp, hum y windspeed contienen ceros en la fuente original. El README no explica su causa ni los identifica como códigos de ausencia.",
        },
        "alcance_y_limitaciones": [
            "La identidad de los archivos verifica la fidelidad de la copia y de la carga, no la exactitud de cada medición original.",
            "Los 22 registros con humedad cero se concentran el 2011-03-10. Deben verificarse antes de usar humedad en un análisis meteorológico; no se imputan ni eliminan automáticamente.",
            "No se atribuyen los ceros meteorológicos a calma, sensores defectuosos o datos faltantes sin evidencia adicional.",
            "Cero valores nulos no significa cobertura completa: existen horas de calendario sin registro.",
            "La necesidad del proyecto utiliza hr, workingday y cnt; esta auditoría no añade un análisis causal o predictivo.",
        ],
    }
    RESULTADOS.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("CSV de Hugging Face y UCI idénticos; huella del notebook confirmada.")
    print(f"DataFrame: {len(df):,} filas y {len(df.columns)} columnas.")
    print(f"Nulos: {int(df.isna().sum().sum())}; incidencias de coherencia: {sum(controles.values())}.")
    print(f"cnt: mínimo {estadisticas['cnt']['minimo']}, máximo {estadisticas['cnt']['maximo']}, suma {estadisticas['cnt']['suma']:,}.")
    print(f"Horas sin registro: {len(horas_ausentes)}; humedad cero: {ceros['hum']} registros.")
    print("Reporte:", SALIDA.relative_to(RAIZ).as_posix())


if __name__ == "__main__":
    main()
