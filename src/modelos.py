# -*- coding: utf-8 -*-
"""Comparación de modelos bajo protocolo único · EC2053C."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_validate, KFold
from sklearn.dummy import DummyRegressor

SEMILLA = 2053


def preprocesador(cols_num, cols_cat, grado: int = 1) -> ColumnTransformer:
    pasos = [("imp", SimpleImputer(strategy="median", add_indicator=True)),
             ("esc", StandardScaler())]
    if grado > 1:
        pasos.insert(1, ("poly", PolynomialFeatures(degree=grado, include_bias=False)))
    return ColumnTransformer([
        ("num", Pipeline(pasos), cols_num),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), cols_cat),
    ])


def vif(matriz_num: pd.DataFrame) -> pd.Series:
    """Factor de inflación de varianza por variable."""
    Z = pd.DataFrame(
        StandardScaler().fit_transform(
            SimpleImputer(strategy="median").fit_transform(matriz_num)),
        columns=matriz_num.columns)
    salida = {}
    for c in Z.columns:
        otras = Z.drop(columns=c)
        r2 = LinearRegression().fit(otras, Z[c]).score(otras, Z[c])
        salida[c] = np.inf if r2 >= 1 - 1e-12 else 1.0 / (1.0 - r2)
    return pd.Series(salida).sort_values(ascending=False)


def comparar_modelos(X, y, modelos: dict, cols_num, cols_cat,
                     grado: int = 1, escala: float = 1.0,
                     n_pliegues: int = 5, incluir_trivial: bool = True) -> pd.DataFrame:
    """Evalúa varios estimadores sobre el mismo protocolo y devuelve una tabla.

    modelos: {"nombre": estimador}. Se agrega siempre el modelo trivial como
    referencia, salvo que se pida lo contrario.
    """
    cv = KFold(n_splits=n_pliegues, shuffle=True, random_state=SEMILLA)
    candidatos = dict(modelos)
    if incluir_trivial:
        candidatos = {"Media (línea cero)": DummyRegressor(strategy="mean"), **candidatos}

    filas = []
    for nombre, est in candidatos.items():
        pipe = Pipeline([("pre", preprocesador(cols_num, cols_cat, grado)), ("reg", est)])
        r = cross_validate(pipe, X, y, cv=cv, return_train_score=True,
                           scoring=["neg_root_mean_squared_error",
                                    "neg_mean_absolute_error", "r2"])
        filas.append({
            "modelo": nombre,
            "RMSE": -r["test_neg_root_mean_squared_error"].mean() / escala,
            "MAE": -r["test_neg_mean_absolute_error"].mean() / escala,
            "R2_prueba": r["test_r2"].mean(),
            "R2_entrenamiento": r["train_r2"].mean(),
            "sd_R2": r["test_r2"].std(),
        })
    out = pd.DataFrame(filas)
    out["brecha"] = out["R2_entrenamiento"] - out["R2_prueba"]
    return out


def filas_por_variable(X, cols_num, cols_cat, grado: int = 1) -> dict:
    """Diagnóstico de dimensionalidad: cuántas filas hay por variable efectiva."""
    pre = preprocesador(cols_num, cols_cat, grado).fit(X)
    p = len(pre.get_feature_names_out())
    n = len(X)
    if n / p < 10:
        veredicto = "regularizar no es opcional"
    elif n / p < 25:
        veredicto = "comparar con y sin regularizacion"
    else:
        veredicto = "zona comoda"
    return {"filas": n, "variables": p, "razon": round(n / p, 1), "veredicto": veredicto}
