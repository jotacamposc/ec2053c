# EC2053C - Análisis de Datos II

**Universidad Católica de la Santísima Concepción**  
**FACEA · Ingeniería en Información y Control de Gestión**

---

## Ayudantía 01: Verificación del Entorno de Trabajo

Este repositorio contiene la estructura base y la comprobación del entorno `ec2053c` para los trabajos prácticos de la asignatura.

### Integrantes del Equipo
* **José Campos** - jcampos@iicg.ucsc.cl
* **Tomás Ganga** - tganga@iicg.ucsc.cl
* **Vicente Guzmán** - vguzman@iicg.ucsc.cl
* 
### Estructura del Proyecto
* `data/`: Carpetas para almacenamiento de datos (raw, interim, processed).
* `notebooks/`: Cuadernos Jupyter del curso (incluye `verificacion.ipynb`).
* `reports/`: Informes e impresiones de salida (incluye `entorno_verificado.txt`).
* `src/`: Funciones y módulos auxiliares.

---

## Proyecto Capstone · Hito 1: Reposición de inventario

**Decisión:** cada semana el encargado de compras de un minimarket decide cuántas unidades reponer de cada producto.
**Modelo:** regresión Ridge que predice las unidades vendidas en las próximas 4 semanas.

### Cómo reproducir

1. `conda activate ec2053c`
2. Copiar el extracto en `data/raw/HISTORICO VENTAS.xlsx` (no se sube al repositorio, Ley 21.719).
3. Abrir `notebooks/01_hito1_reposicion_inventario.ipynb` y ejecutar `Kernel → Restart & Run All`.

### Archivos que genera el cuaderno

* `data/processed/matriz_hito1.parquet`: matriz de diseño del Hito 1 (585 productos × 14 columnas).
* `src/auditoria.py` y `src/modelos.py`: funciones de auditoría y comparación de modelos.
* `reports/diccionario_variables.csv`, `reports/auditoria_calidad.md`, `reports/h1_resumen.csv`.
* `reports/figuras/`: gráficos del informe y la presentación.

Semilla del curso: 2053 · Partición 70% entrenamiento / 30% prueba · Validación cruzada de 5 pliegues.
