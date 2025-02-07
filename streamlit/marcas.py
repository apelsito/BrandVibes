#######################################################################################
##            Librerías para la creación de la interfaz de usuario en Streamlit     ##
#######################################################################################
# Librería para crear la interfaz de usuario en Streamlit
import streamlit as st  

#######################################################################################
##            Manejo del sistema y rutas de archivos                              ##
#######################################################################################
# Para interactuar con el sistema operativo (rutas, variables de entorno, etc.)
import os  
# Para modificar las rutas de búsqueda de módulos
import sys  
# Agrega el directorio padre ("../") al sistema de rutas de búsqueda de módulos, permitiendo importar módulos desde ahí
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#######################################################################################
##            Funciones personalizadas para la interfaz de usuario de Streamlit     ##
#######################################################################################
# Funciones personalizadas para manejar la interfaz de marcas en Streamlit
import src.soporte_streamlit_marcas as sp  

#######################################################################################
##            Conexión con la base de datos Supabase                               ##
#######################################################################################
# Para crear un cliente y manejar la conexión con Supabase
from supabase import create_client, Client  

#######################################################################################
##            Manejo de variables de entorno                                      ##
#######################################################################################
# Para cargar las variables de entorno desde un archivo .env
from dotenv import load_dotenv  

#######################################################################################
##            Fin de los Imports                                                   ##
#######################################################################################


# ============================================================================
# 1. CONFIGURACIÓN INICIAL
# ============================================================================

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase: Recupera URL y Key desde las variables de entorno
url = os.getenv("project_url")
key = os.getenv("browser_safe_key")
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Vibes 4 Brands - La información que necesitas", page_icon="🎧")


# Inicializar session_state para almacenar datos cargados y evitar múltiples consultas
if "data_cargada" not in st.session_state:
    st.session_state["data_cargada"] = {}

# Título general del dashboard
st.title("Dashboard de Seguidores 🎵")

# ============================================================================
# 2. DEFINICIÓN DE LAS MARCAS Y CREACIÓN DE PESTAÑAS
# ============================================================================

# Definir las marcas (puedes agregar o quitar marcas según sea necesario)
marcas = [
    {"id": 1, "name": "Zara"},
    {"id": 2, "name": "Primark"},
    {"id": 3, "name": "Nike"}
    # Puedes descomentar o agregar más marcas si lo deseas:
    # {"id": 4, "name": "Adidas"},
    # {"id": 5, "name": "H&M"},
    # {"id": 6, "name": "Pull & Bear"},
    # {"id": 7, "name": "Bershka"},
    # {"id": 8, "name": "Stradivarius"},
    # {"id": 9, "name": "Mango"},
    # {"id": 10, "name": "Desigual"}
]

# Crear pestañas utilizando el nombre de cada marca
tabs = st.tabs([marca["name"] for marca in marcas])

# ============================================================================
# 3. CSS PARA EL DISEÑO
# ============================================================================

st.markdown("""
    <style>
    .top-3-container {
        display: flex;
        justify-content: center;
        gap: 40px;
    }
    .artist-card {
        background-color: #222;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        width: 220px;
        color: white;
        font-weight: bold;
        box-shadow: 3px 3px 10px rgba(255,255,255,0.1);
        font-size: 20px;
    }
    .ranking-title {
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
        position: relative;
    }
    .medal {
        font-size: 40px;
        display: block;
    }
    .artist-name {
        font-size: 24px;
        font-weight: bold;
        margin-top: 10px;
    }
    .score {
        font-size: 20px;
        margin-top: 5px;
    }
    /* Ajustes para el podio */
    .top-1 {
        height: 270px;
        transform: translateY(0px);
    }
    .top-2 {
        height: 230px;
        transform: translateY(40px);
    }
    .top-3 {
        transform: translateY(60px);
    }
    /* Ajuste de la posición del título */
    .title-top-1 {
        transform: translateY(0px);
    }
    .title-top-2 {
        transform: translateY(40px);
    }
    .title-top-3 {
        transform: translateY(60px);
    }
    
    .stDataFrame {
        margin: auto; /* Centrar horizontalmente */
        width: 80% !important; /* Ajusta el ancho */
        height: 400px !important; /* Ajusta la altura */
    }
    /* Ajuste de la fuente y alineación del texto en el DataFrame */
    .stDataFrame div {
        font-size: 50px !important; /* Tamaño de letra */
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# 4. CONTENIDO DE CADA PESTAÑA (Dashboard de cada marca)
# ============================================================================

# Iterar por cada pestaña para mostrar el dashboard de la marca correspondiente
for i, marca in enumerate(marcas):
    with tabs[i]:
        # ------------------------------------------------------------------------
        # 4.1 TÍTULO Y DATOS GENERALES DE LA MARCA
        # ------------------------------------------------------------------------
        st.header(f"Estadísticas de {marca['name']}")
        brand_id = marca["id"]

        # Cargar datos de la marca una sola vez y almacenarlos en session_state
        if brand_id not in st.session_state["data_cargada"]:
            st.session_state["data_cargada"][brand_id] = {
                "numero_seguidores": sp.obtener_numero_seguidores(supabase, brand_id),
                "numero_playlists": sp.obtener_numero_playlists(supabase, brand_id),
                "numero_playlists_reducido": sp.obtener_numero_playlists_reducido(supabase, brand_id),
                "rankings": {
                    # Se crean tres rankings: Artistas, Géneros y Subgéneros
                    f"🎤 Top Artistas 🔥 - {marca['name']}": [
                        sp.obtener_top_artistas(supabase, start=j, end=j, id_brand=brand_id)[0] for j in range(3)
                    ],
                    f"🎶 Top Géneros más escuchados 🎶 - {marca['name']}": [
                        sp.obtener_top_generos(supabase, start=j, end=j, id_brand=brand_id)[0] for j in range(3)
                    ],
                    f"🔥 Top Subgéneros más escuchados 🔥 - {marca['name']}": [
                        sp.obtener_top_subgeneros(supabase, start=j, end=j, id_brand=brand_id)[0] for j in range(3)
                    ],
                },
                "dataframes": {
                    # Se obtienen los dataframes con el resto de los datos para cada ranking
                    f"🎤 Top Artistas 🔥 - {marca['name']}": sp.obtener_resto_artistas(supabase, start=0, end=999999, id_brand=brand_id),
                    f"🎶 Top Géneros más escuchados 🎶 - {marca['name']}": sp.obtener_resto_generos(supabase, start=0, end=999999, id_brand=brand_id),
                    f"🔥 Top Subgéneros más escuchados 🔥 - {marca['name']}": sp.obtener_resto_subgeneros(supabase, start=0, end=999999, id_brand=brand_id),
                }
            }

        # Recuperar los datos almacenados para la marca actual
        datos = st.session_state["data_cargada"][brand_id]

        # Mostrar métricas generales en tres columnas
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Total de Seguidores", value=datos["numero_seguidores"])
        col2.metric(label="Total de Playlists Recopiladas", value=datos["numero_playlists"])
        col3.metric(label="Playlists usadas para el análisis", value=datos["numero_playlists_reducido"])

        # ------------------------------------------------------------------------
        # 4.2 SELECCIÓN Y VISUALIZACIÓN DE RANKINGS
        # ------------------------------------------------------------------------

        # Selectbox para elegir qué ranking visualizar sin realizar nuevas consultas
        selected_ranking = st.selectbox(
            "📊 **Selecciona un Ranking:**", list(datos["rankings"].keys()), key=f"ranking_{brand_id}"
        )

        # Obtener los datos del ranking seleccionado
        top_ranking = datos["rankings"][selected_ranking]

        # Determinar el tipo de ranking a partir del título para saber qué campo utilizar
        # Se asume que el título tiene un formato consistente, por ejemplo: "🎤 Top Artistas 🔥 - Zara"
        ranking_type = selected_ranking.split(" ")[2]  # Se extrae "Artistas", "Géneros" o "Subgéneros"

        # Definir la estructura del podio (Top 1, Top 2 y Top 3) con sus estilos y medallas
        podium_structure = [
            {"title": "Top 1", "class": "top-1", "title_class": "title-top-1", "medal": "🥇"},
            {"title": "Top 2", "class": "top-2", "title_class": "title-top-2", "medal": "🥈"},
            {"title": "Top 3", "class": "top-3", "title_class": "title-top-3", "medal": "🥉"},
        ]

        # Mapear el tipo de ranking a la propiedad que se usará para extraer el nombre de cada registro
        name_field = {
            "Artistas": "artist_name",
            "Géneros": "genre_name",
            "Subgéneros": "subgenre_name"
        }.get(ranking_type, "artist_name")  # Por defecto se usa "artist_name"

        # Mostrar el podio: Utilizamos tres columnas para disponer los puestos
        col2, col1, col3 = st.columns([1, 1, 1])
        for col, ranking, podium in zip([col1, col2, col3], top_ranking, podium_structure):
            with col:
                st.markdown(f'<div class="ranking-title">{podium["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="artist-card {podium['class']}">
                        <span class="medal">{podium['medal']}</span>
                        <div class="artist-name">{ranking[name_field]}</div>
                        <div class="score">Escuchas: {ranking['number_of_appearances']}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.divider()

        # ------------------------------------------------------------------------
        # 4.3 DETALLE DEL RANKING: DataFrame con información adicional
        # ------------------------------------------------------------------------
        st.subheader("📊 Detalle del Ranking Seleccionado")
        st.dataframe(
            datos["dataframes"][selected_ranking],
            height=320,
            use_container_width=True,
            hide_index=True
        )
