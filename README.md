# Análisis de Seguidores y Playlists en Spotify 🎵

## Descripción del Proyecto 💡

Este proyecto tiene como objetivo analizar los datos de seguidores y playlists de diferentes marcas en Spotify. Utilizando diversas herramientas y bibliotecas de Python, se busca proporcionar información valiosa para la toma de decisiones estratégicas en marketing y gestión de contenidos musicales.

El propósito principal es ofrecer una herramienta útil para marcas y artistas, que permita entender mejor a su audiencia y optimizar sus estrategias de contenido en Spotify.

## 🎯 Objetivos

1. **Carga y Exploración de Datos**:
   - Identificar patrones en los datos.
   - Detectar valores atípicos y posibles inconsistencias.

2. **Preprocesamiento**:
   - Limpieza y preparación de datos.
   - Codificación de variables categóricas.
   - Escalado de variables numéricas.
   - Gestión de valores nulos y outliers.

3. **Análisis y Visualización**:
   - Mostrar gráficamente la importancia de las variables.
   - Analizar los errores y predicciones del modelo.

4. **Integración con Supabase**:
   - Conexión y consulta de datos en una base de datos Supabase.
   - Subida y extracción de datos desde Supabase.

5. **Desarrollo de Dashboard con Streamlit**:
   - Creación de un dashboard interactivo para la visualización de datos.

## Estructura del Proyecto 🗂️

```bash
Spotify-Analysis/
├── .env                        # Archivo de configuración de variables de entorno.
├── .gitignore                  # Archivos y directorios ignorados por Git.
├── conda-cheatsheet.txt        # Hoja de referencia rápida para comandos de conda.
├── datos/                      # Archivos de datos CSV y PKL para el proyecto.
│   ├── 00_Spotify_Genres/
│   ├── 01_Spotify/
│   ├── 02_Base_de_Datos/
│
├── jupyter-notebooks/          # Notebooks de Jupyter con los análisis y modelos.
│   ├── 00_pruebas_supabase.ipynb
│   ├── 01_obtener_ids_followers_spotify.ipynb
│   ├── 02_obtener_listas_spotify.ipynb
│   ├── 03_obtener_id_artistas.ipynb
│   ├── 04_preparar_tabla_resumen.ipynb
│   ├── 05_obtener_generos_artistas.ipynb
│   ├── 06_base_de_datos.ipynb
│   ├── 07_tablas_generos_base_de_datos.ipynb
│
├── src/                        # Archivos .py para funciones auxiliares del proyecto.
│   ├── soporte_sql.py
│   ├── soporte_subida_datos_sql.py
│   ├── soporte_extraccion_datos.py
│   ├── soporte_streamlit_usuarios.py
│
├── streamlit/                  # Aplicaciones de Streamlit para visualización de datos.
│   ├── main.py
│   ├── marcas.py
│   ├── usuarios.py
│
└── README.md                   # Descripción del proyecto, instrucciones de instalación y uso.
```

## Instalación y Requisitos 🛠️

### Requisitos

Para ejecutar este proyecto, asegúrate de tener instalado lo siguiente:

- **Python 3.x** 🐍
- **Jupyter Notebook** 📓 para ejecutar y visualizar los análisis de datos
- **Bibliotecas de Python**:
    - [pandas](https://pandas.pydata.org/docs/) para manipulación y análisis de datos 🧹
    - [numpy](https://numpy.org/doc/stable/) para cálculos numéricos y manejo de matrices 🔢
    - [matplotlib](https://matplotlib.org/stable/index.html) para crear gráficos básicos 📊
    - [seaborn](https://seaborn.pydata.org/) para visualizaciones estadísticas avanzadas 📈
    - [tqdm](https://tqdm.github.io/) para mostrar barras de progreso en procesos largos ⏳
    - [supabase](https://supabase.io/docs) para la integración con la base de datos Supabase 🌟
    - [streamlit](https://streamlit.io/) para la creación de dashboards interactivos 🌐
    - [dotenv](https://pypi.org/project/python-dotenv/) para la gestión de variables de entorno 🛠️

### Instalación 🛠️

1. Clona este repositorio:
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd Spotify-Analysis
    ```

2. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

3. Configura las variables de entorno en el archivo [.env](http://_vscodecontentref_/0):
    ```env
    project_url=your_project_url
    browser_safe_key=your_browser_safe_key
    ```

## Uso

### Jupyter Notebooks

Los notebooks en la carpeta [jupyter-notebooks](http://_vscodecontentref_/1) contienen los pasos para la extracción, procesamiento y análisis de datos. Algunos de los notebooks más importantes son:

- `00_pruebas_supabase.ipynb`: Pruebas iniciales con Supabase.
- `01_obtener_ids_followers_spotify.ipynb`: Obtención de IDs de seguidores en Spotify.
- `02_obtener_listas_spotify.ipynb`: Obtención de listas de reproducción de Spotify.
- `03_obtener_id_artistas.ipynb`: Obtención de IDs de artistas.
- `04_preparar_tabla_resumen.ipynb`: Preparación de la tabla resumen.
- `05_obtener_generos_artistas.ipynb`: Obtención de géneros de artistas.
- `06_base_de_datos.ipynb`: Creación y manejo de la base de datos en Supabase.
- `07_tablas_generos_base_de_datos.ipynb`: Creación de tablas de géneros en la base de datos.

### Scripts

Los scripts en la carpeta [src](http://_vscodecontentref_/2) contienen funciones y utilidades para la manipulación de datos y la interacción con la base de datos:

- `soporte_sql.py`: Funciones para la conexión y consulta de la base de datos.
- `soporte_subida_datos_sql.py`: Funciones para la subida de datos a la base de datos.
- `soporte_extraccion_datos.py`: Funciones para la extracción de datos de Spotify.
- `soporte_streamlit_usuarios.py`: Funciones para la integración con Streamlit.

### Streamlit

La carpeta [streamlit](http://_vscodecontentref_/3) contiene aplicaciones de Streamlit para la visualización de datos:

- `main.py`: Configuración principal de la aplicación Streamlit.
- `marcas.py`: Dashboard para la visualización de datos de marcas.
- `usuarios.py`: Dashboard para la visualización de datos de usuarios.

Para ejecutar la aplicación de Streamlit, usa el siguiente comando:
```bash
streamlit run streamlit/main.py