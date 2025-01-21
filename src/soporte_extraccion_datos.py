from tqdm import tqdm
import pandas as pd
import os
import ast
import json
import sys
sys.path.append("../")
import src.soporte_spotify as api


def obtener_id_artistas(brand_df,output_file = "../datos/01 Spotify/00_GuardadoTemporal.csv"):
    # Convertir a Diccionario
    brand_df["playlists"] = brand_df["playlists"].apply(ast.literal_eval)
    
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
        brand_df["playlist_ids_limited"] = brand_df["playlist_ids_limited"].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
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