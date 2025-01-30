import streamlit as st
from supabase import create_client, Client
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
import sys
sys.path.append("../")
import src.soporte_spotify_streamlit as spot
import os
from dotenv import load_dotenv  
load_dotenv()  

# Configuración de Supabase
url = os.getenv("project_url")
key = os.getenv("browser_safe_key")
supabase: Client = create_client(url, key)

# Configuración de Spotify
CLIENT_ID = os.getenv("client_ID")
CLIENT_SECRET = os.getenv("client_Secret")
REDIRECT_URI = "http://localhost:8501"  # Asegúrate de registrar esto en Spotify Developer
SCOPES = (
    "user-read-private user-read-email user-library-read "
    "playlist-read-private playlist-read-collaborative "
    "user-top-read user-read-recently-played "
    "user-read-currently-playing user-read-playback-state "
    "streaming user-follow-read"
)

# Crear instancia de SpotifyOAuth
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPES
)

# Inicializar session_state si no existe
if "spotify_token" not in st.session_state:
    st.session_state["spotify_token"] = None

if not st.session_state["spotify_token"]:
    st.title("🔗 Conectar Spotify")
    auth_url = sp_oauth.get_authorize_url()
    st.link_button("🎵 Vincular con Spotify", auth_url)
    auth_code = st.query_params.get("code")

    if auth_code:
        token_info = sp_oauth.get_access_token(auth_code, as_dict=False)
        st.session_state["spotify_token"] = token_info
        st.rerun()
else:
    sp = spotipy.Spotify(auth=st.session_state["spotify_token"])
    user_info = sp.current_user()
    user_id = user_info['id']
    user_name = user_info['display_name']

    user_check = supabase.table("users").select("user_id").eq("user_id", user_id).execute().data

    if not user_check:
        st.warning("⚠️ Usuario no encontrado en la BD. Preparando tu resumen")

        with st.spinner("⏳ Obteniendo información del usuario..."):
            spot.get_current_user(sp)
        st.success("✅ Información del usuario guardada.")

        with st.spinner("⏳ Extrayendo canciones guardadas..."):
            spot.get_all_saved_tracks(sp)
        st.success("✅ Canciones guardadas extraídas.")

        with st.spinner("⏳ Obteniendo canciones más escuchadas..."):
            spot.get_all_top_tracks(sp)
        st.success("✅ Canciones más escuchadas extraídas.")

        with st.spinner("⏳ Calculando ranking de artistas..."):
            spot.get_user_artist_ranking(sp, supabase)
        st.success("✅ Ranking de artistas generado.")

        with st.spinner("⏳ Calculando ranking de géneros y subgéneros..."):
            spot.get_user_genre_and_subgenre_ranking(sp, supabase)
        st.success("✅ Ranking de géneros y subgéneros generado.")
            
        time.sleep(1)
        st.session_state.clear()
        st.success("🎉 ¡Ya tenemos todo! Aquí está tu dashboard en...")
        for i in range(3, 0, -1):
            st.header(f"⏳ {i}...")
            st.session_state.clear()
            time.sleep(1)

        st.session_state.clear()
        st.rerun()

    st.title(f"Dashboard de {user_name} 🎵")

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

    option = st.selectbox(
        "📊 Selecciona una métrica para visualizar:",
        ["🎤 Top Artistas", "🎶 Top Géneros", "🔥 Top Subgéneros"]
    )

    rankings = {
        "🎤 Top Artistas": spot.obtener_top_artistas(supabase, user_id, start=0, end=3),
        "🎶 Top Géneros": spot.obtener_top_generos(supabase, user_id, start=0, end=3),
        "🔥 Top Subgéneros": spot.obtener_top_subgeneros(supabase, user_id, start=0, end=3)
    }

    ranking_data = rankings[option]

    st.subheader(option)
    col2, col1, col3 = st.columns(3)
    
    podium_structure = [
            {"title": "Top 1", "class": "top-1", "title_class": "title-top-1", "medal": "🥇"},
            {"title": "Top 2", "class": "top-2", "title_class": "title-top-2", "medal": "🥈"},
            {"title": "Top 3", "class": "top-3", "title_class": "title-top-3", "medal": "🥉"},
        ]
    
    if option == "🎤 Top Artistas":
        name_field = "artist_name"
    elif option == "🎶 Top Géneros":
        name_field = "genre_name"
    elif option == "🔥 Top Subgéneros":
        name_field = "subgenre_name"

    for col, ranking, podium in zip([col1, col2, col3], ranking_data, podium_structure):
        with col:
            st.markdown(f'<div class="ranking-title {podium["title_class"]}">{podium["title"]}</div>', unsafe_allow_html=True)
            st.markdown(f"""
                <div class="artist-card {podium['class']}">
                    <span class="medal">{podium['medal']}</span>
                    <div class="artist-name">{ranking[name_field]}</div>
                    <div class="score">Escuchas: {ranking['number_of_appearances']}</div>
                </div>
            """, unsafe_allow_html=True)
    
    df_data = spot.obtener_resto_artistas(supabase, user_id, start=0, end=999999) if option == "🎤 Top Artistas" else \
               spot.obtener_resto_generos(supabase, user_id, start=0, end=999999) if option == "🎶 Top Géneros" else \
               spot.obtener_resto_subgeneros(supabase, user_id, start=0, end=999999)
    
    st.divider()
    # Mostrar el DataFrame debajo del podio
    st.subheader("📊 Detalle del Ranking Seleccionado")
    st.dataframe(df_data, use_container_width=True)
