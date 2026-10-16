# -*- coding: utf-8 -*-
"""Auditoría de calidad y de fuga para matrices de diseño · EC2053C.

Adaptada de la ayudantía 3 a una etiqueta CONTINUA (unidades): la brecha de
faltantes se mide en unidades de la etiqueta y no como prevalencia.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

SOSPECHOSAS = ("final", "recuperado", "post", "cierre", "resultado",
               "definitivo", "real", "efectivo", "pagado")


def _extremos(s: pd.Series) -> dict:
    q1, q3 = s.quantile([0.25, 0.75]); ric = q3 - q1
    z = ((s - s.mean()) / s.std(ddof=0)).abs()
    med = s.median(); mad = (s - med).abs().median()
    z_rob = (0.6745 * (s - med) / mad).abs() if mad > 0 else pd.Series(0.0, index=s.index)
    return {"asimetria": float(s.skew()),
            "z3": int((z > 3).sum()),
            "iqr": int(((s < q1 - 1.5 * ric) | (s > q3 + 1.5 * ric)).sum()),
            "mad": int((z_rob > 3.5).sum())}


def auditar_matriz(df: pd.DataFrame, etiqueta: str, claves: list[str],
                   umbral_corr: float = 0.60) -> dict:
    """Devuelve un diccionario con las cuatro auditorías y una lista de alertas."""
    alertas: list[str] = []
    n = len(df)

    # --- estructura -----------------------------------------------------
    dup = int(df.duplicated(subset=claves).sum())
    if dup:
        alertas.append(f"{dup} filas duplicadas por la clave {claves}.")
    constantes = [c for c in df.columns if df[c].nunique(dropna=False) <= 1]

    # --- faltantes ------------------------------------------------------
    falt = []
    for c in df.columns:
        if c == etiqueta:
            continue
        na = int(df[c].isna().sum())
        if na == 0:
            continue
        tiene = df[c].notna()
        brecha = float(df.loc[~tiene, etiqueta].mean() - df.loc[tiene, etiqueta].mean())
        falt.append({"variable": c, "faltan": na, "pct": na / n, "brecha_etiqueta": brecha})
        if abs(brecha) > 0.5:      # media unidad de diferencia en la etiqueta
            alertas.append(
                f"La ausencia de «{c}» separa la etiqueta en {brecha:+.2f} unidades: "
                f"use add_indicator=True.")
    faltantes = pd.DataFrame(falt)

    # --- extremos -------------------------------------------------------
    ext = []
    for c in df.select_dtypes("number").columns:
        if c == etiqueta:
            continue
        s = df[c].dropna()
        if s.nunique() <= 2:
            continue
        d = _extremos(s); d["variable"] = c
        ext.append(d)
    extremos = pd.DataFrame(ext)
    if len(extremos):
        extremos = extremos[["variable", "asimetria", "z3", "iqr", "mad"]]
        extremos = extremos.sort_values("asimetria", ascending=False)

    # --- sospechas de fuga ----------------------------------------------
    por_nombre = [c for c in df.columns
                  if c != etiqueta and any(p in c.lower() for p in SOSPECHOSAS)]
    for c in por_nombre:
        alertas.append(f"El nombre de «{c}» sugiere información posterior a la decisión.")

    num = df.select_dtypes("number").drop(columns=[etiqueta], errors="ignore")
    num = num.loc[:, num.nunique() > 1]
    corr = num.corrwith(df[etiqueta]).abs().sort_values(ascending=False)
    altas = corr[corr > umbral_corr]
    for c, v in altas.items():
        alertas.append(f"«{c}» correlaciona {v:.2f} con la etiqueta: descarte fuga antes de usarla.")

    return {"n_filas": n, "n_columnas": df.shape[1],
            "media_etiqueta": float(df[etiqueta].mean()),
            "duplicados_clave": dup, "constantes": constantes,
            "faltantes": faltantes, "extremos": extremos,
            "correlaciones": corr, "sospechosas_por_nombre": por_nombre,
            "alertas": alertas}


def informe_markdown(rep: dict, titulo: str = "Informe de auditoría") -> str:
    """Convierte el resultado de auditar_matriz() en un informe legible."""
    L = [f"# {titulo}", ""]
    L += [f"- Filas: **{rep['n_filas']:,}**  ·  Columnas: **{rep['n_columnas']}**",
          f"- Media de la etiqueta: **{rep['media_etiqueta']:.2f} unidades**",
          f"- Duplicados por clave: **{rep['duplicados_clave']}**",
          f"- Columnas constantes: {rep['constantes'] or 'ninguna'}", ""]

    L += ["## Alertas", ""]
    if rep["alertas"]:
        L += [f"{i}. {a}" for i, a in enumerate(rep["alertas"], 1)]
    else:
        L += ["Ninguna alerta automática. Esto no reemplaza la revisión manual del "
              "diccionario de variables."]
    L += [""]

    if len(rep["faltantes"]):
        L += ["## Faltantes", "", rep["faltantes"].round(3).to_markdown(index=False), ""]
    if len(rep["extremos"]):
        L += ["## Valores extremos", "",
              rep["extremos"].round(2).head(12).to_markdown(index=False), ""]

    L += ["## Correlación con la etiqueta (10 mayores)", "",
          rep["correlaciones"].head(10).round(3).to_markdown(), ""]
    return chr(10).join(L)
