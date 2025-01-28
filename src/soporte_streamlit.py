import os
import pandas as pd
import streamlit as st
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

    return len(supabase_credential.table("reduced_playlists").select("*").in_("follower_id", lista_follower_ids).execute().data)

def obtener_top_artistas(supabase_credential, start = 0, end = 0, id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('artists_ranking').select('artist_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).execute().data

        return ranking_response
    
def obtener_resto_artistas(supabase_credential, start = 0, end = 0, id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('artists_ranking').select('artist_name','number_of_appearances').eq('brand_id', 1).range(start,end).execute().data
        # Ahora generamos el dataframe
        artists_names = []
        artists_appearances = []
        for dictio in ranking_response:
            artists_names.append(dictio["artist_name"])
            artists_appearances.append(dictio["number_of_appearances"])
        
        df = pd.DataFrame({
            "Artista": artists_names,
            "Cantidad de escuchas" : artists_appearances
        })
        # Iniciamos el index en start, para que empi
        df.index = df.index + start + 1
        df.reset_index(inplace=True)
        df.rename(columns = {'index':'Ranking'}, inplace = True)
        return df
    
def obtener_top_generos(supabase_credential, start = 0, end = 0, id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('main_genres').select('genre_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).execute().data
        
        return ranking_response
    
def obtener_resto_generos(supabase_credential, start = 0, end = 0, id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('main_genres').select('genre_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).execute().data
        # Ahora generamos el dataframe
        genre_names = []
        genre_appearances = []
        for dictio in ranking_response:
            genre_names.append(dictio["genre_name"])
            genre_appearances.append(dictio["number_of_appearances"])
        
        df = pd.DataFrame({
            "Género": genre_names,
            "Cantidad de escuchas" : genre_appearances
        })
        # Iniciamos el index en start, para que empi
        df.index = df.index + start + 1
        df.reset_index(inplace=True)
        df.rename(columns = {'index':'Ranking'}, inplace = True)
        return df
    
def obtener_top_subgeneros(supabase_credential, start = 0, end = 0, id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('subgenres').select('subgenre_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).execute().data

        return ranking_response
    
def obtener_resto_subgeneros(supabase_credential, start = 0, end = 0, id_brand = 0):
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('subgenres').select('subgenre_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).execute().data
        # Ahora generamos el dataframe
        subgenre_names = []
        subgenre_appearances = []
        for dictio in ranking_response:
            subgenre_names.append(dictio["subgenre_name"])
            subgenre_appearances.append(dictio["number_of_appearances"])
        
        df = pd.DataFrame({
            "Subgénero": subgenre_names,
            "Cantidad de escuchas" : subgenre_appearances
        })
        # Iniciamos el index en start, para que empi
        df.index = df.index + start + 1
        df.reset_index(inplace=True)
        df.rename(columns = {'index':'Ranking'}, inplace = True)
        return df