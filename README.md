# English:
# Mexico COVID-19 Open Data Analysis

Processing and visualization of the public COVID-19 datasets published by Mexico's Ministry of Health (Secretaría de Salud) from 2020 to 2025. The project cleans records with bad data, calculates different metrics (like cases, sex, age, state of residence, test type and deaths) and makes interactive charts with Plotly.

The processing is done with **Polars** in lazy mode. This lets us handle files with millions of rows without loading them fully into memory, and run several queries in parallel.


## What the project does

1. Asks the user for a year to process (2020–2025).
2. Reads the matching CSV file in lazy mode.
3. Detects the file format automatically by its number of columns (40 or 42).
4. Removes junk records (unclear nationality and unrealistic ages).
5. Calculates summary statistics and shows them in the console.
6. Makes interactive charts (pie, bar, line and an animated choropleth map).
7. Shows the total processing time.

## Input data

The files are downloaded from the Ministry of Health's open data portal and must be saved in the project root with this name: `COVID19MEXICO202X.csv`

> The files are not included in the repo because they weigh several GB.

You also need the **`mx.json`** file, a GeoJSON with the borders of Mexico's states, used for the map.

### Differences between formats

The dataset structure changed starting in 2023. The code handles this based on the number of columns.

| Format | Years | Classification column | Lab test column |
|---|---|---|---|
| 40 columns | 2020–2023 | `CLASIFICACION_FINAL` | `RESULTADO_LAB` |
| 42 columns | 2024–2025 | `CLASIFICACION_FINAL_COVID` | `RESULTADO_PCR` |

Also, the `PAIS_ORIGEN` column is forced to `String` type when reading the CSV. Otherwise, it would raise an error.

## Data cleaning

Records that meet any of these conditions are removed:

- `PAIS_NACIONALIDAD` equal to `Otro`, `SE DESCONOCE`, `Zona Neutral` or `99` (unclear nationality).
- `EDAD` (age) greater than **95** years (unrealistic ages).

## Calculated metrics

Rules used in the whole analysis:

- **Infected:** `CLASIFICACION_FINAL` (or `_COVID`) with values `1, 2, 3`.
- **Not infected:** values `4, 5, 6, 7`.
- **Sex:** `1` = female, `2` = male.
- **Alive:** `FECHA_DEF == '9999-99-99'`. Any other date means the person died.

| Metric | Description |
|---|---|
| Total infected | Count of infected vs. not infected people. |
| Split by sex | Number of people in each group: male/female × infected/not infected. |
| Average age | Average age for each group (`XX1`, `XY1`, `XX0`, `XY0`: sex by infection). |
| Top 10 states | The 10 states of residence with the most infected people. |
| Diagnosis combinations | Classification by test type (lab / antigen / none) and vital status (alive / dead), plus the not infected groups. |

## Visualizations

| Chart | Type | Description |
|---|---|---|
| Distribution by diagnosis | Pie | Share of each combination of test type and vital status. |
| Split by sex | Bar | People in each group (sex by infection). |
| Average age per year | Line | How the average age changes for each group, 2020–2025. |
| Infected per year | Line | Infected vs. not infected per year. |
| Infected Mexicans over time | Animated choropleth map | Number of cases per state, with one frame per year. It only includes people with Mexican nationality (`NACIONALIDAD == 1`). |

The map puts the six years into one DataFrame (renaming `CLASIFICACION_FINAL_COVID` to `CLASIFICACION_FINAL` in 2024 and 2025) and changes the numeric `ENTIDAD_RES` keys into state names, so they match `properties.name` in the GeoJSON.

## Requirements and installation

- Python 3.10 or higher
- Polars
- Plotly

## Usage

1. Put the CSV files and `mx.json` in the same folder as the script.
2. Run the script.
3. Enter the year to process when asked.
4. The result tables will be printed in the console and the charts will open in the browser.

> The **average age per year** chart, the **infected per year** chart and the **map** are always made, no matter which year you choose, because they summarize all the years.

## Data source

Secretaría de Salud, Gobierno de México: *Datos abiertos de COVID-19* (COVID-19 open data).

---
# Español: 
# Análisis de datos abiertos de COVID-19 en México

Procesamiento y visualización de los datasets públicos de Covid 19 publicados por la Secretaría de Salud de México (de los años 2020 a 2025). El proyecto limpia los registros con datos inconsistentes, calcula diferentes métricas (como contagios, sexo, edad, estado de residencia, tipo de prueba y defunción) y genera gráficos interactivos con Plotly.

El procesamiento se hace con **Polars** en modo lazy, lo que permite manejar archivos de varios millones de filas sin cargarlos completos en memoria y ejecutar varias consultas en paralelo.


## Qué hace el proyecto

1. Pide al usuario un año a procesar (2020–2025).
2. Lee el CSV correspondiente de forma lazy.
3. Detecta automáticamente el formato del archivo según su número de columnas (40 o 42).
4. Elimina registros basura (nacionalidad confusa y edades poco realistas).
5. Calcula estadísticas agregadas y las muestra en consola.
6. Genera gráficos interactivos (pastel, barras, líneas y un mapa coroplético animado).
7. Muestra el tiempo total de procesamiento.

## Datos de entrada

Los archivos se descargan desde el portal de datos abiertos de la Secretaría de Salud y deben guardarse en la raíz del proyecto con este nombre: `COVID19MEXICO202X.csv`

> Los archivos no se incluyen en el repo, ya que pesan varios GB

También se necesita el archivo **`mx.json`**, un GeoJSON con los límites de los estados de México, usado para el mapa.

### Diferencias entre formatos

La estructura del dataset cambió a partir del año 2023, el código lo maneja según el número de columnas

| Formato | Años | Columna de clasificación | Columna de prueba de laboratorio |
|---|---|---|---|
| 40 columnas | 2020–2023 | `CLASIFICACION_FINAL` | `RESULTADO_LAB` |
| 42 columnas | 2024–2025 | `CLASIFICACION_FINAL_COVID` | `RESULTADO_PCR` |

Además, se fuerza la columna `PAIS_ORIGEN` a tipo `String` al leer el CSV, de otra forma lanzaría un error.

## Limpieza de datos

Se descartan los registros que cumplan alguna de estas condiciones:

- `PAIS_NACIONALIDAD` igual a `Otro`, `SE DESCONOCE`, `Zona Neutral` o `99` (nacionalidad confusa).
- `EDAD` mayor a **95** años (edades poco realistas).

## Métricas calculadas

Criterios usados en todo el análisis:

- **Infectado:** `CLASIFICACION_FINAL` (o `_COVID`) con valores `1, 2, 3`.
- **No infectado:** valores `4, 5, 6, 7`.
- **Sexo:** `1` = mujer, `2` = hombre.
- **Vivo:** `FECHA_DEF == '9999-99-99'`; cualquier otra fecha se considera fallecido.

| Métrica | Descripción |
|---|---|
| Total de infectados | Conteo de infectados vs. no infectados. |
| Separación por sexo | Cantidad de personas en cada grupo: hombre/mujer × infectado/no infectado. |
| Edad promedio | Promedio de edad por grupo (`XX1`, `XY1`, `XX0`, `XY0`: sexo por infección). |
| Top 10 de estados | Los 10 estados de residencia con más infectados. |
| Combinaciones de diagnóstico | Clasificación según tipo de prueba (laboratorio / antígeno / ninguna) y estado vital (vivo / fallecido), más las categorías de no infectados. |

## Visualizaciones

| Gráfico | Tipo | Descripción |
|---|---|---|
| Distribución por diagnóstico | Pastel | Proporción de cada combinación de prueba y estado vital. |
| Separación por sexo | Barras | Personas por grupo (sexo por infección). |
| Promedio de edad por año | Líneas | Evolución de la edad promedio por grupo, 2020–2025. |
| Infectados por año | Líneas | Infectados vs no infectados por año. |
| Infectados mexicanos con el tiempo | Mapa coroplético animado | Número de contagios por estado, con un fotograma por año. Solo incluye personas de nacionalidad mexicana (`NACIONALIDAD == 1`). |

El mapa unifica los seis años en un solo DataFrame (renombrando `CLASIFICACION_FINAL_COVID` a `CLASIFICACION_FINAL` en 2024 y 2025) y convierte las claves numéricas de `ENTIDAD_RES` a nombres de estado para que coincidan con `properties.name` del GeoJSON.

## Requisitos e instalación

- Python 3.10 o superior
- Polars
- Plotly

## Uso

1. Coloca los CSV y `mx.json` en la misma carpeta que el script.
2. Ejecuta el script
3. Ingresa el año a procesar cuando se solicite
4. Se imprimirán las tablas de resultados en consola y se abrirán las gráficas en el navegador.

> Los gráficos de **promedio de edad por año**, **infectados por año** y el **mapa** se generan siempre, sin importar el año elegido, porque resumen todos los años.

## Fuente de los datos

Secretaría de Salud, Gobierno de México: *Datos abiertos de COVID-19*.
