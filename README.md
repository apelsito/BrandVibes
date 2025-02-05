# BrandVibes - Proyecto Final: Conectando Música y Moda con Inteligencia de Datos 🎧

## Descripción del Proyecto 💡

BrandVibes es una plataforma innovadora que aprovecha el poder de la música para conectar usuarios y marcas de moda a través del análisis de sus preferencias en Spotify. El proyecto combina data science, machine learning, web scraping y visualización interactiva para ofrecer recomendaciones de marcas personalizadas y herramientas de análisis de mercado para empresas de moda.

## 🔥 Objetivo del Proyecto

El propósito de BrandVibes es transformar el consumo de moda utilizando la música como indicador de identidad y afinidad personal. Se basa en la idea de que los estilos musicales reflejan en gran medida la personalidad y las preferencias de los consumidores, lo que permite a las marcas crear estrategias de marketing más personalizadas, colaboraciones con artistas relevantes y experiencias inmersivas para sus clientes.

El sistema se divide en dos módulos principales:

### 🟢 1. BrandVibes for Users: Conecta tu Spotify y descubre tu afinidad con las marcas

Los usuarios pueden vincular su cuenta de Spotify para obtener un análisis detallado de su perfil musical y descubrir qué marcas encajan con su estilo.

#### 🚀 Proceso de Recomendación para Usuarios

1. **Conexión con Spotify mediante OAuth 2.0**, autenticando la cuenta sin comprometer credenciales.
2. **Extracción de datos personales de Spotify**, incluyendo:
   - Canciones guardadas
   - Artistas más escuchados
   - Géneros y subgéneros predominantes
3. **Cálculo de afinidad con marcas basado en**:
   - Ranking de artistas favoritos del usuario
   - Géneros musicales predominantes
   - BPM y otros atributos de audio
4. **Visualización en un Dashboard interactivo con**:
   - Top 3 artistas más escuchados
   - Ranking de géneros principales
   - Match musical con diferentes marcas

#### 📌 Algoritmo de Recomendación de Marcas

Se compara el perfil del usuario con las bases de datos de seguidores de marcas analizados previamente. Se calcula una distancia euclidiana entre los vectores de afinidad musical de cada usuario y el perfil musical agregado de cada marca. Se genera un porcentaje de afinidad que indica qué marcas tienen una audiencia similar a los gustos del usuario.

### 🔵 2. BrandVibes for Brands: Análisis de Seguidores y Estrategias de Marketing Musical

Este módulo está diseñado para marcas de ropa que buscan comprender el perfil musical de sus seguidores y mejorar su estrategia de branding mediante insights basados en datos.

#### 🔍 ¿Qué ofrece BrandVibes a las marcas?

1. **Perfil musical detallado de sus seguidores**
   - Análisis de artistas favoritos, géneros predominantes y BPMs más comunes entre sus seguidores en Spotify.
   - Identificación de patrones de consumo musical dentro de su audiencia.
2. **Recomendación de artistas para colaboraciones**
   - Identificación de artistas populares dentro de la base de seguidores de una marca.
   - Datos que permiten seleccionar embajadores musicales alineados con la identidad de la empresa.
3. **Optimización de playlists para tiendas y eventos**
   - Curación de listas de reproducción basadas en los gustos musicales de los clientes.
   - Aumento de la experiencia en tienda al adaptar la música al perfil de los consumidores.
4. **Comparación con marcas competidoras**
   - Análisis de afinidad cruzada para ver qué marcas comparten público similar.
   - Identificación de oportunidades para colaboraciones o diferenciación estratégica.

#### 📊 Visualización en Dashboards Empresariales

Cada marca tiene acceso a una plataforma en Streamlit donde puede:
- Ver en tiempo real el perfil musical agregado de sus seguidores.
- Explorar gráficos interactivos con rankings de artistas, géneros y BPMs.
- Comparar su perfil con otras marcas y encontrar insights estratégicos.

## 📁 Estructura del Proyecto

```bash
BrandVibes/
├── .env                        # Archivo de configuración de variables de entorno.
├── .gitignore                  # Archivos y directorios ignorados por Git.
├── conda-cheatsheet.txt        # Hoja de referencia rápida para comandos de conda.
├── datos/                      # Archivos de datos CSV y PKL para el proyecto.
│   ├── 00_Spotify_Genres/
│   ├── 01_Spotify/
│   ├── 02_Base_de_Datos/
│
├── jupyter-notebooks/          # Notebooks de Jupyter con los análisis y modelos.
│   ├── recomendacion_por_artista.ipynb
│   ├── sistema_recomendacion_por_genero.ipynb
│
├── src/                        # Archivos .py para funciones auxiliares del proyecto.
│   ├── soporte_spotify.py
│   ├── soporte_sql.py
│   ├── soporte_streamlit_usuarios.py
│   ├── soporte_streamlit_marcas.py
│
├── streamlit/                  # Aplicaciones de Streamlit para visualización de datos.
│   ├── usuarios.py
│   ├── marcas.py
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
    cd BrandVibes
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

- `recomendacion_por_artista.ipynb`: Implementa el sistema de afinidad basado en artistas.
- `sistema_recomendacion_por_genero.ipynb`: Implementa la recomendación basada en géneros musicales.

### Scripts

Los scripts en la carpeta [src](http://_vscodecontentref_/2) contienen funciones y utilidades para la manipulación de datos y la interacción con la base de datos:

- `soporte_spotify.py`: Módulo que maneja la autenticación y extracción de datos de Spotify.
- `soporte_sql.py`: Funciones para manejo de la base de datos en Supabase.
- `soporte_streamlit_usuarios.py`: Funciones específicas para el dashboard de usuarios.
- `soporte_streamlit_marcas.py`: Funciones específicas para el dashboard de marcas.

### Streamlit

La carpeta [streamlit](http://_vscodecontentref_/3) contiene aplicaciones de Streamlit para la visualización de datos:

- `usuarios.py`: Dashboard de usuarios donde pueden ver su perfil musical y afinidad con marcas.
- `marcas.py`: Dashboard de marcas donde las empresas pueden analizar a sus seguidores.

Para ejecutar la aplicación de Streamlit, usa el siguiente comando:
```bash
streamlit run streamlit/usuarios.py
```
## Contribuciones 🤝

Las contribuciones a este proyecto son muy bienvenidas. Si tienes alguna sugerencia, mejora o corrección, no dudes en ponerte en contacto o enviar tus ideas.

Cualquier tipo de contribución, ya sea en código, documentación o feedback, será valorada. ¡Gracias por tu ayuda y colaboración!

## Autores y Agradecimientos ✍️

### Autor ✒️
**Gonzalo Ruipérez Ojea** - [@apelsito](https://github.com/apelsito) en github

### Agradecimientos ❤️
Quiero expresar mi agradecimiento a mis profesores [@Ana_Garcia](https://github.com/AnaAGG) y [@Jean-Charles](https://github.com/yamadajc) no solo por las herramientas y conocimientos que me han enseñado, sino por haber sido un pilar fundamental para el desarrollo de este proyecto.

Gracias por su paciencia, por cada explicación, por cada guía cuando parecía que el camino se volvía más difícil. Gracias por el apoyo constante, por la confianza que depositaron en mí y por enseñarme que la excelencia no es solo un resultado, sino una mentalidad.

Gracias por todo, sin ellos, jamás habría creado esto. ❤️

