# streamlit run main.py
# pip install supabase
import streamlit as st
import os
import sys
sys.path.append("../")
from supabase import create_client, Client
from dotenv import load_dotenv  
# Carga las variables de entorno definidas en un archivo `.env` para configuraciones sensibles como credenciales.
load_dotenv()  

url = os.getenv("project_url")        
key = os.getenv("browser_safe_key")
supabase: Client = create_client(url, key)

# Título del Dashboard
st.title("Dashboard de Seguidores - Zara")

# Consulta a la base de datos para contar seguidores
def obtener_numero_seguidores(id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        number_of_followers = len(supabase.table("followers").select("*").eq("brand_id", 1).execute().data)
        return number_of_followers
    
def obtener_numero_playlists(id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        followers_response = supabase.table("followers").select("id").eq("brand_id", id_brand).execute().data
        # Pasamos los ids a una lista
        lista_follower_ids = [follower['id'] for follower in followers_response]

        all_playlists = []
        limit = 1000
        # Set the limit for each query
        offset = 0
        while True:
            playlists_response = supabase.table("playlists").select("*").in_("follower_id", lista_follower_ids).range(offset, offset + limit - 1).execute()
            if playlists_response.data:
                all_playlists.extend(playlists_response.data)  
                # Add the retrieved playlists to the list
                offset += limit  
                # Move to the next set of results
            else:
                break
    return len(all_playlists)

def obtener_numero_playlists_reducido(id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        followers_response = supabase.table("followers").select("id").eq("brand_id", id_brand).execute().data
        # Pasamos los ids a una lista
        lista_follower_ids = [follower['id'] for follower in followers_response]

        all_playlists = []
        limit = 1000
        # Set the limit for each query
        offset = 0
        while True:
            playlists_response = supabase.table("reduced_playlists").select("*").in_("follower_id", lista_follower_ids).range(offset, offset + limit - 1).execute()
            if playlists_response.data:
                all_playlists.extend(playlists_response.data)  
                # Add the retrieved playlists to the list
                offset += limit  
                # Move to the next set of results
            else:
                break
    return len(all_playlists)

# Mostrar las métricas principales en el dashboard
st.header("Estadísticas de Zara")

# Obtener las métricas
numero_seguidores = obtener_numero_seguidores(1)  # ID de Zara
numero_playlists = obtener_numero_playlists(1)    # Total de playlists
numero_playlists_reducido = obtener_numero_playlists_reducido(1)  # Playlists reducidas

# Mostrar métricas en columnas para un diseño más limpio
col1, col2, col3 = st.columns(3)

# Métrica: Número de Seguidores
with col1:
    if numero_seguidores is not None:
        st.metric(label="Total de Seguidores", value=numero_seguidores)

# Métrica: Número de Playlists
with col2:
    if numero_playlists is not None:
        st.metric(label="Total de Playlists Recopiladas", value=numero_playlists)

# Métrica: Número de Playlists Reducidas
with col3:
    if numero_playlists_reducido is not None:
        st.metric(label="Playlists usadas para el análisis", value=numero_playlists_reducido)



