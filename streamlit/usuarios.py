import streamlit as st
from supabase import create_client, Client
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
import sys
sys.path.append("../")
import src.soporte_streamlit_usuarios as spot
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
    scope=SCOPES,
    cache_path=".spotify_cache",
    show_dialog=True
)

# Inicializar session_state si no existe
if "spotify_token" not in st.session_state:
    st.session_state["spotify_token"] = None

if "afinidad_calculada" not in st.session_state:
    st.session_state["afinidad_calculada"] = {}


# Configurar la pestaña con un nombre atractivo y un icono
st.set_page_config(page_title="BrandVibes - Tu identidad musical", page_icon="🎧")

# Si el usuario no está autenticado, mostrar pantalla de bienvenida
if not st.session_state["spotify_token"]:
    st.title("🎧 ¡Bienvenido a BrandVibes! 🔥")

    # Descripción con más gancho
    st.markdown("""
    ### 🎶 **Descubre qué marcas vibran con tu rollo.**  
    ¿Tu música define quién eres? Entonces **tu estilo también debería hacerlo.**  
    **BrandVibes** analiza lo que escuchas y te dice qué marcas encajan contigo.  

    ### 🚀 **Cómo funciona (fácil y rápido):**  
    1️⃣ **Conéctate a Spotify** en un clic.  
    2️⃣ **Analizamos tu estilo** y sacamos tu **ADN** musical.  
    3️⃣ **Te mostramos tu afinidad** con las marcas en nuestra base de datos.  
    4️⃣ **De paso, te damos tu perfil musical completo.**  

    ### 🔥 **¿Listo para saber qué marcas te representan?**  
    Conéctate y descubre tu **match** musical con el mundo de la moda. 🎧👕  
    """, unsafe_allow_html=True)


    # Botón de conexión a Spotify
    auth_url = sp_oauth.get_authorize_url()
    st.link_button("🎵 Conectar con Spotify", auth_url)
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
        st.warning("⚠️ ¡Es tu Primera Vez! Vamos a analizar tu música y prepararte algo épico... 🎧🔥")

        with st.spinner("🎧 Analizando tu perfil musical... 🔍"):
            spot.generate_current_user(sp)
        st.success("✅ ¡Listo! Tu identidad sonora está en marcha. 🚀")

        with st.spinner("🎼 Recorriendo tu biblioteca musical... 📀"):
            spot.generate_all_saved_tracks(sp)
        st.success("✅ Tus canciones guardadas están listas. 🎶")

        with st.spinner("📊 Identificando los temazos más escuchados... 🔥"):
            spot.generate_all_top_tracks(sp)
        st.success("✅ ¡Top tracks detectados! Estos son tus esenciales. 🎵")

        with st.spinner("🏆 Construyendo tu ranking de artistas... 🎤"):
            spot.generate_user_artist_ranking(sp,supabase)
        st.success("✅ Tus artistas favoritos ya tienen su podio. 🏅")

        with st.spinner("🎙️ Afinando géneros y subgéneros... 🎚️"):
            spot.generate_user_genre_and_subgenre_ranking(sp,supabase)
        st.success("✅ ¡Todo listo! Tu ADN musical está completo. ⚡")
  
        time.sleep(1)
        st.session_state.clear()
        st.success("🎉 ¡Todo listo! Tu música ha hablado, y ahora llega el momento clave...")

        countdown_text = ["🔥 Cargando tu BrandVibe...", "⚡ Ajustando las frecuencias...", "🚀 Todo listo, dale caña..."]
        for i in range(3, 0, -1):
            st.header(f"⏳ {i}... {countdown_text[3 - i]}")
            st.session_state.clear()
            time.sleep(1)

        st.session_state.clear()
        st.rerun()

    st.title(f"🎵 Tu universo musical - {user_name}!")

    # 🔥 **Nueva sección de afinidad**
    st.subheader("🔍 Descubre tu conexión con las marcas")

    # Tabs para cambiar entre Zara y Primark dinámicamente
    tab1, tab2 = st.tabs(["Zara", "Primark"])
    
    # Diccionario de marcas con su ID en Supabase
    marcas = {"Zara": 1, "Primark": 2}

    def calcular_afinidad(brand_name, brand_id):
        """
        Calcula afinidades y las almacena en session_state si aún no han sido calculadas.
        """
        clave = f"{user_id}_{brand_name}"
        if clave not in st.session_state["afinidad_calculada"]:
            st.session_state["afinidad_calculada"][clave] = {
                "artistas": spot.obtener_afinidad_por_artista(supabase, brand_id, user_id),
                "generos": spot.obtener_afinidad_por_genero(supabase, brand_id, user_id),
                "subgeneros": spot.obtener_afinidad_por_subgenero(supabase, brand_id, user_id)
            }

    # Función para mostrar métricas según la marca seleccionada
    def mostrar_afinidad(brand_name, brand_id):
        calcular_afinidad(brand_name, brand_id)
        datos = st.session_state["afinidad_calculada"][f"{user_id}_{brand_name}"]
        col1, col2, col3 = st.columns(3)
        col1.metric(label=f"Afinidad según Artistas", value=f"{datos['artistas']:.2f}%")
        col2.metric(label=f"Afinidad según Géneros", value=f"{datos['generos']:.2f}%")
        col3.metric(label=f"Afinidad según Subgéneros", value=f"{datos['subgeneros']:.2f}%")


    # Configurar cada tab con su respectiva marca
    with tab1:
        mostrar_afinidad("Zara", marcas["Zara"])
    with tab2:
        mostrar_afinidad("Primark", marcas["Primark"])

    st.divider()

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

    # Almacenar rankings en session_state para evitar recargas
    if "rankings" not in st.session_state:
        st.session_state["rankings"] = {
            "🎤 Top Artistas": spot.obtener_top_artistas(supabase, user_id, start=0, end=3),
            "🎶 Top Géneros": spot.obtener_top_generos(supabase, user_id, start=0, end=3),
            "🔥 Top Subgéneros": spot.obtener_top_subgeneros(supabase, user_id, start=0, end=3)
        }

    option = st.selectbox(
        "📊 Selecciona una métrica para visualizar:",
        ["🎤 Top Artistas", "🎶 Top Géneros", "🔥 Top Subgéneros"]
    )

    # Recuperar ranking desde session_state
    ranking_data = st.session_state["rankings"][option]

    st.subheader(option)
    col2, col1, col3 = st.columns(3)

    podium_structure = [
        {"title": "Top 1", "class": "top-1", "title_class": "title-top-1", "medal": "🥇"},
        {"title": "Top 2", "class": "top-2", "title_class": "title-top-2", "medal": "🥈"},
        {"title": "Top 3", "class": "top-3", "title_class": "title-top-3", "medal": "🥉"},
    ]

    # Determinar qué campo usar en función de la selección
    name_field = {
        "🎤 Top Artistas": "artist_name",
        "🎶 Top Géneros": "genre_name",
        "🔥 Top Subgéneros": "subgenre_name"
    }[option]

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

    # Almacenar DataFrame en session_state para evitar recargas
    if "rankings_df" not in st.session_state:
        st.session_state["rankings_df"] = {
            "🎤 Top Artistas": spot.obtener_resto_artistas(supabase, user_id, start=0, end=999999),
            "🎶 Top Géneros": spot.obtener_resto_generos(supabase, user_id, start=0, end=999999),
            "🔥 Top Subgéneros": spot.obtener_resto_subgeneros(supabase, user_id, start=0, end=999999)
        }

    df_data = st.session_state["rankings_df"][option]

    st.divider()
    st.subheader("📊 Detalle del Ranking Seleccionado")
    st.dataframe(df_data, use_container_width=True)
