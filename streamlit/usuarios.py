import streamlit as st
from supabase import create_client, Client
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
import sys
import os
#sys.path.append("../")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import src.soporte_streamlit_usuarios as spot

from dotenv import load_dotenv  
load_dotenv()  

# Configuración de Supabase
url = os.getenv("project_url")
key = os.getenv("browser_safe_key")
supabase: Client = create_client(url, key)

# Configuración de Spotify
CLIENT_ID = os.getenv("client_ID")
CLIENT_SECRET = os.getenv("client_Secret")
REDIRECT_URI = os.getenv("redirect_url")  # Asegúrate de registrarlo en Spotify Developer
SCOPES = (
    "user-read-private user-read-email user-library-read "
    "playlist-read-private playlist-read-collaborative "
    "user-top-read user-read-recently-played "
    "user-read-currently-playing user-read-playback-state "
    "streaming user-follow-read"
)

# Inicializar la sesión en Streamlit
if "token_info" not in st.session_state:
    st.session_state["token_info"] = None
if "spotify_token" not in st.session_state:
    st.session_state["spotify_token"] = None
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "afinidad_calculada" not in st.session_state:
    st.session_state["afinidad_calculada"] = {}
if "data_cargada" not in st.session_state:
    st.session_state["data_cargada"] = {}

# Variable de control de la pantalla actual.
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "welcome"  # Pantalla inicial: Bienvenida

# Crear instancia de SpotifyOAuth
sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPES,
    cache_path=None,
    show_dialog=True
)

st.set_page_config(page_title="BrandVibes - Tu identidad musical", page_icon="🎧")

# ============================================================================
# PANTALLA 1: Bienvenida e inicio de sesión
# ============================================================================
def pantalla_bienvenida():
    st.title("🎧 ¡Bienvenido a BrandVibes! 🔥")
    st.markdown(
        """
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
        """, 
        unsafe_allow_html=True
    )
    auth_url = sp_oauth.get_authorize_url()
    st.link_button("🎵 Conectar con Spotify", auth_url)

    # Capturamos el parámetro "code" de la URL, si existe.
    query_params = st.query_params
    auth_code = query_params.get("code")
    if auth_code:
        # auth_code puede ser una lista; tomamos el primer valor.
        if isinstance(auth_code, list):
            auth_code = auth_code[0]
        token_info = sp_oauth.get_access_token(auth_code, as_dict=False, check_cache=False)
        st.session_state["token_info"] = token_info
        st.session_state["spotify_token"] = token_info

        # Obtener y almacenar la información del usuario.
        sp = spotipy.Spotify(auth=st.session_state["spotify_token"])
        user_info = sp.current_user()
        st.session_state["user_id"] = user_info["id"]

        # Limpiar los parámetros de la URL para evitar reprocesos.
        st.query_params.clear()
        # Cambiar a la pantalla de "primera vez" y forzar el rerun de la app.
        st.session_state["current_page"] = "first_time"
        st.rerun()

# ============================================================================
# PANTALLA 2: Primera vez (registro y subida de datos a la BD)
# ============================================================================
def pantalla_primera_vez():
    sp = spotipy.Spotify(auth=st.session_state["spotify_token"])
    user_id = st.session_state["user_id"]

    # Comprobamos si el usuario ya existe en la BD.
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
            spot.generate_user_artist_ranking(sp, supabase)
        st.success("✅ Tus artistas favoritos ya tienen su podio. 🏅")

        with st.spinner("🎙️ Afinando géneros y subgéneros... 🎚️"):
            spot.generate_user_genre_and_subgenre_ranking(sp, supabase)
        st.success("✅ ¡Todo listo! Tu ADN musical está completo. ⚡")

        st.success("🎉 ¡Todo listo! Tu música ha hablado, y ahora llega el momento clave...")

        countdown_text = [
            "🔥 Cargando tu BrandVibe...", 
            "⚡ Ajustando las frecuencias...", 
            "🚀 Todo listo, dale caña..."
        ]
        for i in range(3, 0, -1):
            st.header(f"⏳ {i}... {countdown_text[3 - i]}")
            time.sleep(1)

        # Volvemos a consultar si el usuario fue agregado a la BD.
        user_check = supabase.table("users").select("user_id").eq("user_id", user_id).execute().data
        if user_check:
            st.success("✅ ¡Usuario creado exitosamente!")
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        else:
            st.error("❌ Hubo un error al crear tu usuario. Por favor, intenta nuevamente.")
    else:
        # Si el usuario ya existe, pasamos directamente al dashboard.
        st.session_state["current_page"] = "dashboard"
        st.rerun()

# ============================================================================
# PANTALLA 3: Dashboard (vista principal)
# ============================================================================
def pantalla_dashboard():
        # ---- CSS para el diseño del dashboard (Página 3) ----
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
    sp = spotipy.Spotify(auth=st.session_state["spotify_token"])
    user_info = sp.current_user()
    user_id = user_info["id"]
    st.session_state["user_id"] = user_id
    user_name = user_info.get("display_name", "Usuario")

    st.title(f"🎵 Tu universo musical - {user_name}!")

    # Sección de afinidad con marcas.
    st.subheader("🔍 Descubre tu conexión con las marcas")
    
    
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

    def calcular_afinidad(brand_name, brand_id):
        clave = f"{user_id}_{brand_name}"
        if clave not in st.session_state["afinidad_calculada"]:
            st.session_state["afinidad_calculada"][clave] = {
                "artistas": spot.obtener_afinidad_por_artista(supabase, brand_id, user_id),
                "generos": spot.obtener_afinidad_por_genero(supabase, brand_id, user_id),
                "subgeneros": spot.obtener_afinidad_por_subgenero(supabase, brand_id, user_id)
            }

    def mostrar_afinidad(brand_name, brand_id):
        calcular_afinidad(brand_name, brand_id)
        datos = st.session_state["afinidad_calculada"][f"{user_id}_{brand_name}"]
        col1, col2, col3 = st.columns(3)
        col1.metric(label=f"Afinidad según Artistas", value=f"{datos['artistas']:.2f}%")
        col2.metric(label=f"Afinidad según Géneros", value=f"{datos['generos']:.2f}%")
        col3.metric(label=f"Afinidad según Subgéneros", value=f"{datos['subgeneros']:.2f}%")

    for i, marca in enumerate(marcas):
        # Configurar cada tab con su respectiva marca
        with tabs[i]:
            mostrar_afinidad(marca, marca["id"])


    st.divider()

    # Ejemplo de sección de ranking en el dashboard.
    if "rankings" not in st.session_state["data_cargada"]:
        st.session_state["data_cargada"]["rankings"] = {
            "top_rankings": {
                "🎤 Top Artistas": [
                    spot.obtener_top_artistas(supabase, user_id, start=j, end=j)[0] for j in range(3)
                ],
                "🎶 Top Géneros": [
                    spot.obtener_top_generos(supabase, user_id, start=j, end=j)[0] for j in range(3)
                ],
                "🔥 Top Subgéneros": [
                    spot.obtener_top_subgeneros(supabase, user_id, start=j, end=j)[0] for j in range(3)
                ]
            },
            "dataframes": {
                "🎤 Top Artistas": spot.obtener_resto_artistas(supabase, user_id, start=0, end=999999),
                "🎶 Top Géneros": spot.obtener_resto_generos(supabase, user_id, start=0, end=999999),
                "🔥 Top Subgéneros": spot.obtener_resto_subgeneros(supabase, user_id, start=0, end=999999)
            }
        }
    datos = st.session_state["data_cargada"]["rankings"]

    selected_ranking = st.selectbox(
        "📊 **Selecciona un Ranking:**", list(datos["top_rankings"].keys()), key="ranking_selector"
    )

    st.subheader(selected_ranking)
    col2, col1, col3 = st.columns(3)
    podium_structure = [
        {"title": "Top 1", "class": "top-1", "title_class": "title-top-1", "medal": "🥇"},
        {"title": "Top 2", "class": "top-2", "title_class": "title-top-2", "medal": "🥈"},
        {"title": "Top 3", "class": "top-3", "title_class": "title-top-3", "medal": "🥉"},
    ]
    name_field = {
        "🎤 Top Artistas": "artist_name",
        "🎶 Top Géneros": "genre_name",
        "🔥 Top Subgéneros": "subgenre_name"
    }[selected_ranking]
    ranking_data = datos["top_rankings"][selected_ranking]
    for col, ranking, podium in zip([col1, col2, col3], ranking_data, podium_structure):
        with col:
            st.markdown(
                f'<div class="ranking-title {podium["title_class"]}">{podium["title"]}</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"""
                <div class="artist-card {podium['class']}">
                    <span class="medal">{podium['medal']}</span>
                    <div class="artist-name">{ranking[name_field]}</div>
                    <div class="score">Escuchas: {ranking['number_of_appearances']}</div>
                </div>
            """, unsafe_allow_html=True)
    st.divider()
    st.subheader("📊 Detalle del Ranking Seleccionado")
    st.dataframe(datos["dataframes"][selected_ranking], use_container_width=True)

# ============================================================================
# Control de pantallas según el estado en st.session_state
# ============================================================================
if st.session_state["current_page"] == "welcome":
    pantalla_bienvenida()
elif st.session_state["current_page"] == "first_time":
    pantalla_primera_vez()
elif st.session_state["current_page"] == "dashboard":
    pantalla_dashboard()
