# BrandVibes: Tu música, tu estilo, tu marca. 🎧

## 💡 Descripción del Proyecto

BrandVibes es una plataforma innovadora que aprovecha el poder de la música para conectar usuarios y marcas de moda a través del análisis de sus preferencias en Spotify. Al utilizar tecnologías avanzadas de **data science, machine learning, web scraping y visualización interactiva**, el sistema genera recomendaciones personalizadas y ofrece herramientas de análisis de mercado que optimizan la toma de decisiones para empresas del sector moda.

El proyecto se basa en la premisa de que la música es un reflejo de la personalidad y las emociones de los individuos. Así como los géneros y artistas favoritos pueden indicar estados de ánimo y preferencias estéticas, también pueden revelar afinidades con determinadas marcas y estilos de moda. **BrandVibes aprovecha esta conexión entre la identidad musical y la identidad de marca** para ofrecer una experiencia de compra y marketing mucho más segmentada y efectiva.

El sistema se compone de dos aplicaciones:
1. **BrandVibes for Users**: Un servicio de recomendación que permite a los usuarios conectar su cuenta de Spotify y descubrir qué marcas encajan con su estilo musical.
2. **BrandVibes for Brands**: Un dashboard interactivo que permite a las marcas analizar el perfil musical de su audiencia y utilizar esos datos para estrategias de marketing, colaboraciones con artistas y optimización de experiencias en tienda.

## 🔥 Objetivo del Proyecto

El propósito de BrandVibes es **transformar la industria de la moda utilizando la música como un indicador clave de identidad y afinidad personal**. Nuestra hipótesis fundamental es que los consumidores eligen su vestimenta de manera similar a como eligen su música: según su identidad, estado de ánimo y percepción de la marca.

A través de este enfoque, BrandVibes ofrece valor tanto a los usuarios como a las marcas:

### 🌍 Para los Usuarios:
- Descubren qué marcas se alinean mejor con su identidad musical.
- Reciben recomendaciones basadas en datos reales de su actividad en Spotify.
- Exploran nuevas marcas y tendencias afines a su estilo.

### 📈 Para las Marcas:
- **Segmentación avanzada de audiencia**: Las marcas pueden definir perfiles de clientes basados en afinidades musicales, permitiendo estrategias de marketing más personalizadas.
- **Colaboraciones estratégicas con artistas**: Al identificar qué músicos escuchan sus seguidores, las marcas pueden seleccionar embajadores que representen auténticamente su identidad.
- **Optimización de experiencia en tienda**: Se pueden curar playlists específicas para generar una atmósfera en los espacios físicos alineada con el público objetivo.
- **Benchmarking y análisis de competencia**: Comparando su perfil de seguidores con otras marcas, pueden detectar oportunidades de mercado y ajustar su comunicación.

---

## 🏗️ Estructura del Sistema

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

1. **Buscamos los artistas comunes**
   - Dejando únicamente aquellos que coinciden con su posición en cada ranking.
2. **Asignamos pesos según su posición en el ranking**
   - Fórmula utilizada:
   $$
   peso = \frac{1}{\text{posición}}
   $$
   - No buscamos complejidad, buscamos que funcione de momento.
3. **Normalizamos los pesos**
   - Dado que la longitud y ranking es distinto, debemos normalizar los pesos a la misma escala.
   - De esta forma nos aseguramos de que el cálculo de la afinidad es justo.
   - Fórmula utilizada:
   $$
   peso\_normalizado = \frac{peso\_original}{\sum peso\_original}
   $$
   - Ahora los pesos están a la misma escala.
4. **Poner como index artista y peso se queda como columna**.
5. **Ordenamos los artistas para que los vectores estén alineados**.
6. **Creamos Matriz de Comparación**.
7. **Calculamos las distancias con `pdist` y `squareform`**.
8. **Extraemos distancias**.
9. **Obtenemos Porcentaje de Afinidad**.
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

### 🌐 Aplicaciones Web
BrandVibes cuenta con dos aplicaciones web desplegadas en Streamlit:
- **Para Usuarios** (descubre qué marcas se alinean con tu perfil musical): [BrandVibes User](https://brandvibes.streamlit.app/)
- **Para Marcas** (analiza a tu audiencia y mejora tu estrategia de branding): [BrandVibes Business](https://vibes4brands.streamlit.app/)

Ambas aplicaciones utilizan Supabase como base de datos para almacenar y consultar la información de usuarios y marcas, asegurando una experiencia fluida e interactiva para todos los participantes del ecosistema BrandVibes.

## 📁 Estructura del Proyecto

```bash
BrandVibes/
└── .devcontainer/
│  │
│  └── devcontainer.json # Archivos necesarios para la ejecución en streamlit
│
├── datos/                      # Archivos de datos CSV para el proyecto.
│   ├── 00_Spotify_Genres/      # Diccionario de Géneros, para posterior mapeo
│   ├── 01_Spotify/             # Estructura de carpetas usada para la extracción de datos de marcas
│   ├── 02_Base_de_Datos/       # Usado para generar la base de datos
│
├── jupyter-notebooks/          # Para extracción datos de marcas + generar funciones
│   ├── 01_obtener_ids_followers_spotify.ipynb 
│   ├── 02_obtener_listas_spotify.ipynb
│   ├── 03_obtener_id_artistas.ipynb
│   ├── 04_preparar_tabla_resumen.ipynb
│   ├── 05_obtener_generos_artistas.ipynb
│   ├── 06_base_de_datos.ipynb
│   ├── 07_tablas_generos_base_de_datos.ipynb
│   ├── 08_Como_Usar_Funciones_SQL.ipynb
│   ├── 09_obtener_resto_marcas.ipynb
│   ├── 10_subir_resto_marcas.ipynb
│   ├── 11_base_datos_usuario.ipynb
│   ├── 12_obtener_datos_ejemplo.ipynb
│   ├── 13_recomendacion_por_artista_1.ipynb
│   ├── 14_sistema_recomendacion_por_artista.ipynb # Aquí se explican las fórmulas utilizadas para el cálculo de afinidad
│   ├── 15_sistema_recomendacion_por_genero.ipynb
│   └── 16_sistema_recomendacion_por_subgenero.ipynb   
│   
├── src/
│   ├── soporte_extraccion_datos.py
│   ├── soporte_spotify.py
│   ├── soporte_sql.py
│   ├── soporte_streamlit_marcas.py
│   ├── soporte_streamlit_usuarios.py
│   └── soporte_subida_datos_sql.py 
│
├── streamlit/
│   ├── 00_solucion_problemas_autenticación.ipynb # Explicación sobre solución a problemas de auth de Spotify 
│   ├── marcas.py               # Streamlit de Marcas (BranVibes Business)
│   └── usuarios.py             # Streamlit del usuario (BrandVibes User)
│
│                  
├── .gitignore                  # Archivos y directorios ignorados por Git.
│
├── README.md                   # ¡Lo estás leyendo!
│
└── requirements.txt            # Archivo para instalar dependencias necesarias en streamlit    
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

