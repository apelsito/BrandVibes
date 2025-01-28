import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv  
load_dotenv()  

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

# Mostrar el botón para conectar con Spotify
st.title("🔗 Conectar Spotify")
# Redirigir a la ventana de autorización de Spotify
auth_url = sp_oauth.get_authorize_url()
if not st.session_state["spotify_token"]:
    st.link_button("🎵 Vincular con Spotify",auth_url)

    # Extraer el código de autorización de la URL
    auth_code = st.query_params.get("code")

    if auth_code:
        # Intercambiar el código por un token
        
        token_info = sp_oauth.get_access_token(auth_code,as_dict=False)

        st.session_state["spotify_token"] = token_info
        st.success("✅ Conexión exitosa con Spotify")

# Mostrar información del usuario si ya está autenticado
if st.session_state["spotify_token"]:
    sp = spotipy.Spotify(auth=st.session_state["spotify_token"])
    user_info = sp.current_user()
    st.write("✅ Conectado como:")
    st.write(f"Nombre: 🎧 {user_info['display_name']}")
    st.write(f"Email: {user_info['email']}")
    st.write(f"URL 🔗: {user_info['external_urls']['spotify']}")
    st.write(f"id_usuario: {user_info['id']}")
    st.write(f"Version_producto: {user_info['product']}")
