import os
import sys
sys.path.append("../")
from supabase import create_client, Client

# Consulta a la base de datos para contar seguidores
def obtener_numero_seguidores(supabase_credential, id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        number_of_followers = len(supabase_credential.table("followers").select("*").eq("brand_id", id_brand).execute().data)
        return number_of_followers
    
def obtener_numero_playlists(supabase_credential, id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        followers_response = supabase_credential.table("followers").select("id").eq("brand_id", id_brand).execute().data
        # Pasamos los ids a una lista
        lista_follower_ids = [follower['id'] for follower in followers_response]

        all_playlists = []
        limit = 1000
        # Set the limit for each query
        offset = 0
        while True:
            playlists_response = supabase_credential.table("playlists").select("*").in_("follower_id", lista_follower_ids).range(offset, offset + limit - 1).execute()
            if playlists_response.data:
                all_playlists.extend(playlists_response.data)  
                # Add the retrieved playlists to the list
                offset += limit  
                # Move to the next set of results
            else:
                break
    return len(all_playlists)

def obtener_numero_playlists_reducido(supabase_credential, id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        followers_response = supabase_credential.table("followers").select("id").eq("brand_id", id_brand).execute().data
        # Pasamos los ids a una lista
        lista_follower_ids = [follower['id'] for follower in followers_response]

        all_playlists = []
        limit = 1000
        # Set the limit for each query
        offset = 0
        while True:
            playlists_response = supabase_credential.table("reduced_playlists").select("*").in_("follower_id", lista_follower_ids).range(offset, offset + limit - 1).execute()
            if playlists_response.data:
                all_playlists.extend(playlists_response.data)  
                # Add the retrieved playlists to the list
                offset += limit  
                # Move to the next set of results
            else:
                break
    return len(all_playlists)
