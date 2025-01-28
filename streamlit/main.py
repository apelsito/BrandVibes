import streamlit as st
import os
import sys
sys.path.append("../")
import src.soporte_streamlit as sp
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
url = os.getenv("project_url")
key = os.getenv("browser_safe_key")
supabase: Client = create_client(url, key)

# Inicializar session_state si no existe
if "data_cargada" not in st.session_state:
    st.session_state["data_cargada"] = {}

# Título general del dashboard
st.title("Dashboard de Seguidores 🎵")

# Crear pestañas para las marcas
# marcas = [
#     {"id": 1, "name": "Zara"},
#     {"id": 2, "name": "Primark"},
#     {"id": 3, "name": "Nike"},
#     {"id": 4, "name": "Adidas"},
#     {"id": 5, "name": "H&M"},
#     {"id": 6, "name": "Pull & Bear"},
#     {"id": 7, "name": "Bershka"},
#     {"id": 8, "name": "Stradivarius"},
#     {"id": 9, "name": "Mango"},
#     {"id": 10, "name": "Desigual"}
# ]

marcas = [
    {"id": 1, "name": "Zara"},
    {"id": 2, "name": "Primark"}
]

# Crear las pestañas
tabs = st.tabs([marca["name"] for marca in marcas])

# ---- CSS para el diseño ----
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


# Iterar por cada pestaña para mostrar el dashboard de la marca correspondiente
for i, marca in enumerate(marcas):
    with tabs[i]:
        st.header(f"Estadísticas de {marca['name']}")
        brand_id = marca["id"]

        # 🚀 Cargar datos una sola vez y almacenarlos en `st.session_state`
        if brand_id not in st.session_state["data_cargada"]:
            st.session_state["data_cargada"][brand_id] = {
                "numero_seguidores": sp.obtener_numero_seguidores(supabase, brand_id),
                "numero_playlists": sp.obtener_numero_playlists(supabase, brand_id),
                "numero_playlists_reducido": sp.obtener_numero_playlists_reducido(supabase, brand_id),
                "rankings": {
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
                    f"🎤 Top Artistas 🔥 - {marca['name']}": sp.obtener_resto_artistas(supabase,start=3, end=999999,id_brand=brand_id),
                    f"🎶 Top Géneros más escuchados 🎶 - {marca['name']}": sp.obtener_resto_generos(supabase,start=3, end=999999,id_brand=brand_id),
                    f"🔥 Top Subgéneros más escuchados 🔥 - {marca['name']}": sp.obtener_resto_subgeneros(supabase,start=3, end=999999,id_brand=brand_id),
                }
            }

        # Cargar datos desde session_state
        datos = st.session_state["data_cargada"][brand_id]

        # Mostrar métricas en columnas
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Total de Seguidores", value=datos["numero_seguidores"])
        col2.metric(label="Total de Playlists Recopiladas", value=datos["numero_playlists"])
        col3.metric(label="Playlists usadas para el análisis", value=datos["numero_playlists_reducido"])

        # 🔽 Selectbox para cambiar ranking sin hacer nuevas consultas
        selected_ranking = st.selectbox(
            "📊 **Selecciona un Ranking:**", list(datos["rankings"].keys()), key=f"ranking_{brand_id}"
        )

        # Obtener datos del ranking seleccionado
        top_ranking = datos["rankings"][selected_ranking]

        # Determinar el campo correcto (artist_name, genre_name, subgenre_name)
        ranking_type = selected_ranking.split(" ")[2]


        # ---- Mantener diseño del podio ----
        podium_structure = [
            {"title": "Top 1", "class": "top-1", "title_class": "title-top-1", "medal": "🥇"},
            {"title": "Top 2", "class": "top-2", "title_class": "title-top-2", "medal": "🥈"},
            {"title": "Top 3", "class": "top-3", "title_class": "title-top-3", "medal": "🥉"},
        ]

        name_field = {
            "Artistas": "artist_name",
            "Géneros": "genre_name",
            "Subgéneros": "subgenre_name"
        }.get(ranking_type, "artist_name")  # Por defecto, usar "artist_name"
        
        # ---- Contenedor en fila con columnas de Streamlit ----
        col2, col1, col3 = st.columns([1, 1, 1])  # 💡 Asegurar Top 1 en el centro más grande

        for col, ranking, podium in zip([col1, col2, col3], top_ranking, podium_structure):
            with col:
                st.markdown(f'<div class="ranking-title {podium["title_class"]}">{podium["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f"""
                    <div class="artist-card {podium['class']}">
                        <span class="medal">{podium['medal']}</span>
                        <div class="artist-name">{ranking[name_field]}</div>
                        <div class="score">Escuchas: {ranking['number_of_appearances']}</div>
                    </div>
                """, unsafe_allow_html=True)
        st.divider()
        # Mostrar el DataFrame debajo del podio
        st.subheader("📊 Detalle del Ranking Seleccionado")
        st.dataframe(datos["dataframes"][selected_ranking],height=320, use_container_width=True,hide_index=True)

