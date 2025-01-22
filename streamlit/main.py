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

# Título general del dashboard
st.title("Dashboard de Seguidores 🎵")

# Crear pestañas para las marcas
marcas = [
    {"id": 1, "name": "Zara"},
    {"id": 2, "name": "Primark"},
    {"id": 3, "name": "Nike"},
    {"id": 4, "name": "Adidas"},
    {"id": 5, "name": "H&M"},
    {"id": 6, "name": "Pull & Bear"},
    {"id": 7, "name": "Bershka"},
    {"id": 8, "name": "Stradivarius"},
    {"id": 9, "name": "Mango"},
    {"id": 10, "name": "Desigual"}
]

# Crear las pestañas
tabs = st.tabs([marca["name"] for marca in marcas])

# Iterar por cada pestaña para mostrar el dashboard de la marca correspondiente
for i, marca in enumerate(marcas):
    with tabs[i]:
        # Título de la pestaña
        st.header(f"Estadísticas de {marca['name']}")

        # Obtener las métricas de la marca
        brand_id = marca["id"]
        numero_seguidores = sp.obtener_numero_seguidores(supabase,brand_id)
        numero_playlists = sp.obtener_numero_playlists(supabase,brand_id)
        numero_playlists_reducido = sp.obtener_numero_playlists_reducido(supabase,brand_id)

        # Mostrar métricas en columnas
        col1, col2, col3 = st.columns(3)

        with col1:
            if numero_seguidores is not None:
                st.metric(label="Total de Seguidores", value=numero_seguidores)

        with col2:
            if numero_playlists is not None:
                st.metric(label="Total de Playlists Recopiladas", value=numero_playlists)

        with col3:
            if numero_playlists_reducido is not None:
                st.metric(label="Playlists usadas para el análisis", value=numero_playlists_reducido)

        # Separador para mejorar diseño
        st.divider()
