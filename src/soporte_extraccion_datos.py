from tqdm import tqdm
import pandas as pd
import os
import ast
import json
import sys
sys.path.append("../")
import src.soporte_spotify as api

def str_a_diccionario(brand_df, columna):
    return brand_df[str(columna)].apply(ast.literal_eval)

def str_a_lista(brand_df, columna):
    return brand_df[str(columna)].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

def obtener_id_artistas(brand_df,output_file = "../datos/01 Spotify/00_GuardadoTemporal.csv"):
    # Convertir a Diccionario
    brand_df["playlists"] = str_a_diccionario(brand_df,"playlists")
    
    # Sacamos una lista de los ids de las playlists
    playlist_ids = []
    for ids in brand_df["playlists"]:
        playlist_ids.append(list(ids.values()))

    brand_df["playlist_ids"] = playlist_ids

    # Sacamos una lista de máximo 10 playlists por usuario
    brand_df["playlist_ids_limited"] = brand_df["playlist_ids"].apply(lambda x: x[:10] if isinstance(x,list) else x)

    # Ahora obtenemos los artistas
    lista_artistas = []
    
    # Ruta donde guardamos de forma temporal el progreso outputfile
    # Cargar progreso si existe un archivo previo en la ruta proporcionada
    if os.path.exists(output_file):
        brand_df = pd.read_csv(output_file)
        brand_df["playlist_ids_limited"] = str_a_lista(brand_df,"playlist_ids_limited")
        lista_artistas = brand_df["artistas"].tolist()
    else:
        brand_df["artistas"] = None

    # Procesar playlists limitadas
    for idx, id_playlist in enumerate(tqdm(brand_df["playlist_ids_limited"], desc="Obteniendo artistas")):
        # Primero realizamos la comprobación de si ya se obtuvieron, de ser así, saltamos al siguiente
        if pd.notna(brand_df.loc[idx, "artistas"]):
            continue
        id_playlist = list(id_playlist)

        # Solicitar token y obtener artistas
        token = api.request_token(silent=True)
        artistas = api.obtener_artistas(token, id_playlist)
        lista_artistas.append(artistas)
        
        # Guardar los artistas como JSON
        brand_df.loc[idx, "artistas"] = json.dumps(artistas)

        # Guardar el progreso después de cada iteración
        brand_df.to_csv(output_file, index=False)
    
    return brand_df

def obtener_artistas_unicos(brand_df):
    artistas_unicos = {}
    for dictio in brand_df["artistas"]:
        for id_artista, artista in dictio.items():
            if id_artista not in artistas_unicos:
                artistas_unicos[id_artista] = artista
    # Eliminar la Key "None"
    del artistas_unicos["None"]
    
    return artistas_unicos

def obtener_ranking_artistas(brand_df):
    conteo_artistas = {}
    for dictio in brand_df["artistas"]:
        for artista in dictio.values():
            if artista != None:
                conteo_artistas[artista] = conteo_artistas.get(artista,0) + 1
    
    return conteo_artistas

def tabla_resumen(brand_df, followers_path, resumen_path):
    # Eliminar aquellos users cuyas playlists no tenían artistas (no había canciones)
    brand_df = brand_df.loc[brand_df["artistas"] != "{}"]
    # Reemplazar los null por None para poder convertirlo a diccionarios
    brand_df.loc[:, "artistas"] = brand_df["artistas"].str.replace("null", "None")
    
    # Convertir:
        # playlists: de STR a dict
        # playlist_ids: de STR a list
        # playlist_ids_limited: de STR a list
        # artistas: de STR a dict
    if type(brand_df["playlists"][0]) == str:
        brand_df.loc[:,"playlists"] = str_a_diccionario(brand_df,"playlists")
    if type(brand_df["playlist_ids"][0]) == str:
        brand_df.loc[:,"playlist_ids"] = str_a_lista(brand_df,"playlist_ids")
    if type(brand_df["playlist_ids_limited"][0]) == str:
        brand_df.loc[:,"playlist_ids_limited"] = str_a_lista(brand_df,"playlist_ids_limited")
    if type(brand_df["artistas"][0]) == str:
        brand_df.loc[:, "artistas"] = str_a_diccionario(brand_df, "artistas")

    # Actualizar el CSV
    brand_df.to_csv(followers_path,index=False)
    
    # Obtener los artistas únicos
    artistas_unicos = obtener_artistas_unicos(brand_df)
    
    # Obtener el ranking de los artistas
    conteo_artistas = obtener_ranking_artistas(brand_df)
    # Ordenar los artistas de mayor a menor repetición
    conteo_artistas = sorted(conteo_artistas.items(), key=lambda x: x[1], reverse=True)

    # Generar df resumen
    resumen_df = pd.DataFrame({
    "brand" : [brand_df["brand"].unique()[0]] ,
    "followers" : brand_df.shape[0],
    "unique_artists": str(artistas_unicos), # Str para poder realizar el dataframe
    "artist_ranking" : str(conteo_artistas) # Str para poder realizar el dataframe
    })
    # Lo volvemos a convertir a diccionario
    resumen_df.loc[:,"unique_artists"] = str_a_diccionario(resumen_df,"unique_artists")
    # Lo volvemos a convertir en lista
    resumen_df.loc[:,"artist_ranking"] = str_a_lista(resumen_df,"artist_ranking")
    # Guardar esta otra tabla
    resumen_df.to_csv(resumen_path,index=False)

    return resumen_df

def obtener_generos_artistas(brand_df, resumen_path):
    # Cargar Dataframe
    brand_df = pd.read_csv(resumen_path)
    # Convertir a diccionario
    if type(brand_df["unique_artists"][0]) == str:
        brand_df.loc[:,"unique_artists"] = str_a_diccionario(brand_df,"unique_artists")
    # Convertir a lista
    if type(brand_df["artist_ranking"][0]) == str:
        brand_df.loc[:,"artist_ranking"] = str_a_lista(brand_df,"artist_ranking")

    # Solicitar token y obtener artistas
    token = api.request_token(silent=True)
    generos = api.obtener_generos(token,brand_df["unique_artists"])
    # Añadir tabla genres al dataframe
    brand_df["genres"] = str(list(generos.keys()))
    # Añadir el ranking de géneros
    brand_df["genres_ranking"] = str(sorted(generos.items(), key=lambda x: x[1], reverse=True))
    brand_df.to_csv(resumen_path,index=False)
    
    return brand_df