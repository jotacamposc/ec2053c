# Auditoría de calidad · matriz de reposición · EC2053C

- Filas: **585**  ·  Columnas: **14**
- Media de la etiqueta: **4.22 unidades**
- Duplicados por clave: **0**
- Columnas constantes: ['semana_corte']

## Alertas

1. La ausencia de «tendencia_4s_12s» separa la etiqueta en -4.62 unidades: use add_indicator=True.
2. La ausencia de «margen_pct» separa la etiqueta en -4.01 unidades: use add_indicator=True.
3. «unid_4s» correlaciona 0.96 con la etiqueta: descarte fuga antes de usarla.
4. «unid_26s» correlaciona 0.96 con la etiqueta: descarte fuga antes de usarla.
5. «unid_12s» correlaciona 0.96 con la etiqueta: descarte fuga antes de usarla.
6. «sd_unid_12s» correlaciona 0.85 con la etiqueta: descarte fuga antes de usarla.

## Faltantes

| variable         |   faltan |   pct |   brecha_etiqueta |
|:-----------------|---------:|------:|------------------:|
| tendencia_4s_12s |       88 | 0.15  |            -4.618 |
| margen_pct       |       79 | 0.135 |            -4.014 |

## Valores extremos

| variable              |   asimetria |   z3 |   iqr |   mad |
|:----------------------|------------:|-----:|------:|------:|
| unid_4s               |        9.68 |    8 |    68 |    71 |
| unid_26s              |        9.67 |    9 |    75 |    84 |
| unid_12s              |        9.45 |    9 |    65 |    75 |
| sd_unid_12s           |        8.5  |    7 |    56 |    69 |
| precio_medio          |        6.67 |   10 |    55 |    43 |
| recencia_semanas      |        1.58 |    9 |    52 |    76 |
| tendencia_4s_12s      |        0.9  |    0 |     0 |     0 |
| semanas_con_venta_12s |        0.8  |    0 |     0 |     0 |
| margen_pct            |       -2.3  |    9 |    56 |    40 |
| antiguedad_semanas    |       -2.58 |   21 |    76 |    85 |

## Correlación con la etiqueta (10 mayores)

|                       |     0 |
|:----------------------|------:|
| unid_4s               | 0.962 |
| unid_26s              | 0.96  |
| unid_12s              | 0.955 |
| sd_unid_12s           | 0.848 |
| semanas_con_venta_12s | 0.422 |
| recencia_semanas      | 0.174 |
| antiguedad_semanas    | 0.129 |
| margen_pct            | 0.057 |
| tendencia_4s_12s      | 0.014 |
| precio_medio          | 0.002 |

## Decisiones sobre las alertas

| alerta                        | decision   | justificacion                                                                                                                                           |
|:------------------------------|:-----------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Producto-semana repetido      | corrijo    | Son ventas del mismo producto a distinto precio en la semana. Se SUMAN las unidades por código y semana: para reponer importa el total vendido.         |
| Filas duplicadas exactas (22) | descarto   | Son dos ventas iguales (misma cantidad y precio) dentro de la semana, no un error de copia: el extracto es un resumen semanal por precio. Se conservan. |
| Costo unitario = 0            | corrijo    | No existe producto gratis: el costo no se registró. Se trata como faltante (NaN) al calcular el margen, y lo imputa el pipeline dentro del pliegue.     |
| Precio venta < costo          | descarto   | Son ofertas o liquidaciones, que sí ocurren en un minimarket. No afectan las unidades vendidas, que es lo que se predice.                               |
| Código = 'False'              | corrijo    | Excel convirtió un código a booleano y mezcla productos distintos (cintillos y otro). Se eliminan esas 5 filas.                                         |
| Semana 71 incompleta (3 días) | corrijo    | Si entrara en la etiqueta subestimaría la demanda. Por eso t0 = semana 66 y la ventana de predicción termina en la semana 70.                           |

| alerta                                                                          | decision   | justificacion                                                                                                                                                                                                         |
|:--------------------------------------------------------------------------------|:-----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Faltantes en margen_pct (la ausencia separa la etiqueta)                        | corrijo    | Vienen del costo = 0 del extracto (MAR: dependen de cómo se cargó el producto en el sistema). Se imputan por mediana dentro del pipeline; src/modelos.py agrega además el indicador de faltante (add_indicator=True). |
| Faltantes en tendencia_4s_12s (la ausencia separa la etiqueta)                  | corrijo    | Productos sin venta en 12 semanas: la razón no se puede calcular (división por cero). Mediana dentro del pipeline + indicador de faltante en src/modelos.py.                                                          |
| Extremos en unidades (asimetría alta)                                           | descarto   | Son productos de alta rotación reales (bolsas, huevos, bebidas). Eliminarlos sería sacar justo los productos que más importa reponer bien.                                                                            |
| Correlación > 0,80 de unid_4s, unid_12s, unid_26s y sd_unid_12s con la etiqueta | descarto   | No es fuga: se calculan con semanas 41-66, todas anteriores a t0. Que la venta pasada prediga la futura es esperable en reposición.                                                                                   |
