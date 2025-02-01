import sys
sys.path.append("../")
import pandas as pd
import src.soporte_spotify as api
import src.soporte_sql as sql
import json
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from scipy.spatial.distance import pdist, squareform

#######################################################################################
##            Obtener Datos Iniciales User y subir a la Base de datos                ##
#######################################################################################
def generate_current_user(sp):
    user_data = sp.current_user()
    user = pd.DataFrame({
        "user_id" : [user_data["id"]],
        "name" : user_data["display_name"],
        "url" : user_data["external_urls"]["spotify"],
        "email" : user_data["email"],
        "product_version" : user_data["product"]
    })
    conexion = sql.conectar_bd()
    query = '''INSERT INTO users(user_id,name,url,email,product_version) VALUES (%s,%s,%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(user))

#######################################################################################
##             Obtener Canciones Guardadas y subir a la Base de datos                ##
#######################################################################################
def generate_all_saved_tracks(sp, limit=50):

    all_tracks = []  # Lista para almacenar todas las canciones
    results = sp.current_user_saved_tracks(limit=limit)  # Primera página

    while results:
        # Añadir las canciones de la página actual a la lista
        all_tracks.extend(results['items'])

        # Seguir al siguiente enlace, si existe
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    users_ids = []
    songs_names = []
    songs_ids = []
    popularities_list = []
    songs_urls = []
    artists_names = []
    artists_ids = []
    artists_urls = []
    added_at_list = []
    user_id = sp.current_user()["id"]
    for track in all_tracks:
        # User id
        users_ids.append(user_id)
        #Nombre Cancion
        songs_names.append(track["track"]["name"])
        #Id Cancion
        songs_ids.append(track["track"]["id"])
        # Popularidad
        popularities_list.append(track["track"]["popularity"])
        # Url Cancion
        songs_urls.append(track["track"]["external_urls"]["spotify"])
        # Nombre del Artista
        artists_names.append(track["track"]["artists"][0]["name"])
        # Id del Artista
        artists_ids.append(track["track"]["artists"][0]["id"])
        # Url de Spotify del Artista
        artists_urls.append(track["track"]["artists"][0]["external_urls"]["spotify"])
        # Fecha en la que el usuario la añadio a su lista
        added_at_list.append(track["added_at"].split("T")[0])

    user_liked_songs = pd.DataFrame({
    "user_id" : users_ids,
    "song_name" : songs_names,
    "song_id" : songs_ids,
    "popularity" : popularities_list,
    "song_url" : songs_urls,
    "artist_name" : artists_names,
    "artist_id" : artists_ids,
    "artist_url" : artists_urls,
    "user_added_at" : added_at_list
    })

    conexion = sql.conectar_bd()
    query = '''INSERT INTO tracks_user_likes(user_id,song_name,song_id,popularity,song_url,artist_name,artist_id,artist_url,user_added_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(user_liked_songs))

#######################################################################################
##         Obtener Canciones más escuchadas y subir a la Base de datos               ##
#######################################################################################
def generate_all_top_tracks(sp, limit=20):

    all_tracks = []  # Lista para almacenar todas las canciones
    results = sp.current_user_top_tracks(limit=limit,time_range="long_term")  # Primera página

    while results:
        # Añadir las canciones de la página actual a la lista
        all_tracks.extend(results['items'])

        # Seguir al siguiente enlace, si existe
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    users_ids = []
    songs_names = []
    songs_ids = []
    popularities_list = []
    songs_urls = []
    artists_names = []
    artists_ids = []
    artists_urls = []
    user_id = sp.current_user()["id"]
    for track in all_tracks:
        # User id
        users_ids.append(user_id)
        #Nombre Cancion
        songs_names.append(track["name"])
        #Id Cancion
        songs_ids.append(track["id"])
        # Popularidad
        popularities_list.append(track["popularity"])
        # Url Cancion
        songs_urls.append(track["external_urls"]["spotify"])
        # Nombre del Artista
        artists_names.append(track["artists"][0]["name"])
        # Id del Artista
        artists_ids.append(track["artists"][0]["id"])
        # Url de Spotify del Artista
        artists_urls.append(track["artists"][0]["external_urls"]["spotify"])
        

    user_top_songs = pd.DataFrame({
    "user_id" : users_ids,
    "song_name" : songs_names,
    "song_id" : songs_ids,
    "popularity" : popularities_list,
    "song_url" : songs_urls,
    "artist_name" : artists_names,
    "artist_id" : artists_ids,
    "artist_url" : artists_urls
    })
    user_top_songs.index = user_top_songs.index + 1
    user_top_songs.reset_index(inplace=True)
    user_top_songs.rename(columns={"index":"ranking"},inplace=True)
    user_top_songs = user_top_songs[["user_id","ranking","song_name","song_id","popularity","song_url","artist_name","artist_id","artist_url"]]
    
    conexion = sql.conectar_bd()
    query = '''INSERT INTO top_tracks(user_id,ranking,song_name,song_id,popularity,song_url,artist_name,artist_id,artist_url) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(user_top_songs))


#######################################################################################
##                Generar Ranking Artistas y subir a la Base de Datos                ##
#######################################################################################
def generate_user_artist_ranking(sp, supabase_credential):
    user_id = sp.current_user()["id"]
    top_tracks = supabase_credential.table('top_tracks').select('user_id','artist_name').eq('user_id', user_id).execute().data
    saved_tracks = supabase_credential.table('tracks_user_likes').select('user_id','artist_name').eq('user_id', user_id).execute().data
    
    artists_names = []
    for artist in top_tracks:
        artists_names.append(artist["artist_name"])

    for artist in saved_tracks:
        artists_names.append(artist["artist_name"])
    
    df = pd.DataFrame({
        "artist_name" : artists_names
    })

    df = df["artist_name"].value_counts().reset_index()
    df.columns = ["artist_name", "number_of_appearances"]

    df["user_id"] = user_id
    artist_ranking = df[["user_id","artist_name","number_of_appearances"]]

    conexion = sql.conectar_bd()
    query = '''INSERT INTO user_artists_ranking(user_id,artist_name,number_of_appearances) VALUES (%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(artist_ranking))


#######################################################################################
##                    Mapear subgéneros a géneros principales                        ##
#######################################################################################
def mapeo_genres():
    """
    Crea un diccionario de mapeo entre subgéneros y géneros principales a partir de un archivo JSON.

    El archivo JSON debe contener una estructura donde los géneros principales están mapeados
    a listas de subgéneros.

    Retorna:
    --------
    dictio_genres : dict
        Un diccionario donde las claves son los subgéneros y los valores son los géneros principales
        a los que pertenecen.

    Proceso:
    --------
    1. Abre y carga el archivo JSON ubicado en "../datos/00_Spotify_Genres/genres_dict.json".
    2. Itera sobre los géneros principales y sus subgéneros dentro del campo "genres_map".
    3. Construye un diccionario donde cada subgénero apunta a su género principal.

    Notas:
    ------
    - El archivo JSON debe tener una clave llamada "genres_map" que contenga el mapeo entre géneros 
    principales y subgéneros.
    """

    with open("../datos/00_Spotify_Genres/genres_dict.json", "r") as file:
        genres_mapping = json.load(file)
    
    dictio_genres = {}
    for main_genre, subgenres in genres_mapping["genres_map"].items():
        for subgenre in subgenres:
            dictio_genres[subgenre] = main_genre
    return dictio_genres

#######################################################################################
##              Obtener Géneros y Subgéneros y subir a la Base de Datos              ##
#######################################################################################
def generate_user_genre_and_subgenre_ranking(sp, supabase_credential):   
    user_id = sp.current_user()["id"]
    top_tracks = supabase_credential.table('top_tracks').select('artist_name','artist_id').eq('user_id', user_id).execute().data
    saved_tracks = supabase_credential.table('tracks_user_likes').select('artist_name','artist_id').eq('user_id', user_id).execute().data
    
    artists_names = []
    artists_ids = []
    for artist in top_tracks:
        artists_names.append(artist["artist_name"])
        artists_ids.append(artist["artist_id"])
    for artist in saved_tracks:
        artists_names.append(artist["artist_name"])
        artists_ids.append(artist["artist_id"])
    
    df = pd.DataFrame({
        "artist_name" : artists_names,
        "artist_id" : artists_ids
    })
    
    dictio = {}
    for row in df.itertuples():
        if row.artist_id not in dictio:
            dictio[row.artist_id] = row.artist_name

    # Solicitar token y obtener artistas
    token = api.request_token(silent=True)
    subgeneros = api.obtener_generos(token,dictio)
    nombres_subgenero = list(subgeneros.keys())
    apariciones = list(subgeneros.values())

    print("Subiendo ranking subgéneros")
    subgenres = pd.DataFrame({
        "subgenre_name" : nombres_subgenero,
        "number_of_appearances" : apariciones
    })

    subgenres["user_id"] = user_id
    subgenres = subgenres[["user_id","subgenre_name","number_of_appearances"]]
    subgenres = subgenres.sort_values(by="number_of_appearances", ascending=False)

    conexion = sql.conectar_bd()
    query = '''INSERT INTO user_subgenres(user_id,subgenre_name,number_of_appearances) VALUES (%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(subgenres))

    print("Subiendo ranking géneros")
    # LLamamos al JSON y generamos el diccionario de Mapeo de subgeneros a generos principales
    mapping_dict = mapeo_genres()
    # Mapeamos los subgeneros a los generos principales
    subgenres["genre_name"] = subgenres["subgenre_name"].map(mapping_dict)

    genre = subgenres[["user_id","genre_name"]]
    genre = genre["genre_name"].value_counts().reset_index()
    genre.columns = ["genre_name","number_of_appearances"]
    genre["user_id"] = user_id
    genres = genre[["user_id","genre_name","number_of_appearances"]]

    conexion = sql.conectar_bd()
    query = '''INSERT INTO user_main_genres(user_id,genre_name,number_of_appearances) VALUES (%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(genres))

#######################################################################################
##                            Obtener Ranking Artistas                               ##
#######################################################################################
def obtener_top_artistas(supabase_credential, user_id, start = 0, end = 0):
    # Primero obtenemos el id de los seguidores de la marca 
    ranking_response = supabase_credential.table("user_artists_ranking").select("artist_name", "number_of_appearances").eq("user_id", user_id).range(start,end).order('number_of_appearances',desc=True).execute().data

    return ranking_response
    
def obtener_resto_artistas(supabase_credential, user_id, start = 0, end = 0):
    # Primero obtenemos el id de los seguidores de la marca 
    ranking_response = supabase_credential.table("user_artists_ranking").select("artist_name", "number_of_appearances").eq("user_id", user_id).range(start,end).order('number_of_appearances',desc=True).execute().data
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

#######################################################################################
##                             Obtener Ranking Géneros                               ##
#######################################################################################    
def obtener_top_generos(supabase_credential, user_id, start = 0, end = 0):
    # Primero obtenemos el id de los seguidores de la marca
    ranking_response = supabase_credential.table("user_main_genres").select("genre_name", "number_of_appearances").eq("user_id", user_id).range(start,end).order('number_of_appearances',desc=True).execute().data
        
    return ranking_response
    
def obtener_resto_generos(supabase_credential, user_id, start = 0, end = 0):
    # Primero obtenemos el id de los seguidores de la marca 
    ranking_response = supabase_credential.table("user_main_genres").select("genre_name", "number_of_appearances").eq("user_id", user_id).range(start,end).order('number_of_appearances',desc=True).execute().data
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

#######################################################################################
##                          Obtener Ranking Subgéneros                               ##
#######################################################################################    
def obtener_top_subgeneros(supabase_credential, user_id, start = 0, end = 0):
    # Primero obtenemos el id de los seguidores de la marca 
    ranking_response = supabase_credential.table("user_subgenres").select("subgenre_name", "number_of_appearances").eq("user_id", user_id).range(start,end).order('number_of_appearances',desc=True).execute().data
    return ranking_response
    
def obtener_resto_subgeneros(supabase_credential, user_id, start = 0, end = 0):
    # Primero obtenemos el id de los seguidores de la marca 
    ranking_response = supabase_credential.table("user_subgenres").select("subgenre_name", "number_of_appearances").eq("user_id", user_id).range(start,end).order('number_of_appearances',desc=True).execute().data
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

#######################################################################################
##                        Sistema Recomendación por Artista                          ##
#######################################################################################
def get_brand_artist_ranking(supabase_credential,brand_id):
    brand_ranking = supabase_credential.table("artists_ranking").select("artist_name","number_of_appearances").eq("brand_id",brand_id).order("number_of_appearances",desc=True).execute().data
    artistas = []
    apariciones = []
    for ranking in brand_ranking:
        artistas.append(ranking["artist_name"])
        apariciones.append(ranking["number_of_appearances"])

    brand_df = pd.DataFrame({
        "artista" : artistas,
        "apariciones" : apariciones
    })

    brand_df.index = brand_df.index + 1
    brand_df.reset_index(inplace=True)
    brand_df.columns = ["ranking","artista","apariciones"]
    brand_df.drop(columns="apariciones",inplace=True)
    brand_df["artista"] = brand_df["artista"].astype(str)
    return brand_df

def get_user_artist_ranking(supabase_credential,user_id):
    user_ranking = supabase_credential.table("user_artists_ranking").select("artist_name","number_of_appearances").eq("user_id",user_id).order("number_of_appearances",desc=True).execute().data
    artistas = []
    apariciones = []
    for ranking in user_ranking:
        artistas.append(ranking["artist_name"])
        apariciones.append(ranking["number_of_appearances"])

    user_df = pd.DataFrame({
        "artista" : artistas,
        "apariciones" : apariciones
    })

    user_df.index = user_df.index + 1
    user_df.reset_index(inplace=True)
    user_df.columns = ["ranking","artista","apariciones"]
    user_df.drop(columns="apariciones",inplace=True)
    user_df["artista"] = user_df["artista"].astype(str)
    return user_df

def obtener_afinidad_por_artista(supabase_credential,brand_id,user_id):
    # Obtener los rankings de la marca y el usuario
    brand_df = get_brand_artist_ranking(supabase_credential, brand_id)
    user_df = get_user_artist_ranking(supabase_credential, user_id)
    
    # Obtener los artistas en común
    artistas_comunes = set(user_df['artista']).intersection(set(brand_df['artista']))
    
    # Si no hay artistas en común la afinidad es del 0%
    if len(artistas_comunes) == 0:
        return 0.0  
    
    user_df_filtrado = user_df[user_df['artista'].isin(artistas_comunes)]
    brand_df_filtrado = brand_df[brand_df['artista'].isin(artistas_comunes)]

    # Reseteamos el Index
    user_df_filtrado.reset_index(drop=True, inplace=True)
    brand_df_filtrado.reset_index(drop=True, inplace=True)

    # Asignar pesos en base a la posición en el ranking
    user_df_filtrado["peso"] = 1 / user_df_filtrado["ranking"]
    brand_df_filtrado["peso"] = 1 / brand_df_filtrado["ranking"]

    # Normalizar los pesos para evitar sesgos por diferencias de tamaño
    user_df_filtrado["peso"] /= user_df_filtrado["peso"].sum()
    brand_df_filtrado["peso"] /= brand_df_filtrado["peso"].sum()

    # Poner como index artista y peso se queda como columna
    pesos_user = user_df_filtrado.set_index("artista")["peso"]
    pesos_brand = brand_df_filtrado.set_index("artista")["peso"]

    # Ordenamos los artistas por orden alfabético para que los vectores estén alineados
    sorted_pesos = sorted(set(pesos_user.index).intersection(set(pesos_brand.index)))

    # Si solo hay un artista en común, asumimos 100% de afinidad
    if len(sorted_pesos) == 1:
        return 100.0 

    # Generamos los vectores
    user_vector = np.array([pesos_user.get(a, 0) for a in sorted_pesos])
    brand_vector = np.array([pesos_brand.get(a, 0) for a in sorted_pesos])

    # Crear matriz de comparación
    matriz_pesos = np.vstack([user_vector, brand_vector])

    # Calcular la matriz de distancias con pdist
    matriz_distancias = squareform(pdist(matriz_pesos, metric="euclidean"))

    # Extraer la distancia entre usuario y marca
    distancia = matriz_distancias[0, 1]

    # Convertimos la distancia en afinidad (invirtiendo la escala)
    afinidad = max(0, (1 - distancia) * 100)

    return float(round(afinidad,2))

#######################################################################################
##                        Sistema Recomendación por Género                           ##
#######################################################################################
def get_brand_genre_ranking(supabase_credential,brand_id):
    brand_ranking = supabase_credential.table("main_genres").select("genre_name","number_of_appearances").eq("brand_id",brand_id).order("number_of_appearances",desc=True).execute().data
    generos = []
    apariciones = []
    for ranking in brand_ranking:
        generos.append(ranking["genre_name"])
        apariciones.append(ranking["number_of_appearances"])

    brand_df = pd.DataFrame({
        "genero" : generos,
        "apariciones" : apariciones
    })

    brand_df.index = brand_df.index + 1
    brand_df.reset_index(inplace=True)
    brand_df.columns = ["ranking","genero","apariciones"]
    brand_df.drop(columns="apariciones",inplace=True)
    brand_df["genero"] = brand_df["genero"].astype(str)
    return brand_df

def get_user_genre_ranking(supabase_credential,user_id):
    user_ranking = supabase_credential.table("user_main_genres").select("genre_name","number_of_appearances").eq("user_id",user_id).order("number_of_appearances",desc=True).execute().data
    generos = []
    apariciones = []
    for ranking in user_ranking:
        generos.append(ranking["genre_name"])
        apariciones.append(ranking["number_of_appearances"])

    user_df = pd.DataFrame({
        "genero" : generos,
        "apariciones" : apariciones
    })

    user_df.index = user_df.index + 1
    user_df.reset_index(inplace=True)
    user_df.columns = ["ranking","genero","apariciones"]
    user_df.drop(columns="apariciones",inplace=True)
    user_df["genero"] = user_df["genero"].astype(str)
    return user_df

def obtener_afinidad_por_genero(supabase_credential,brand_id,user_id):
    # Obtener los rankings de la marca y el usuario
    brand_df = get_brand_genre_ranking(supabase_credential, brand_id)
    user_df = get_user_genre_ranking(supabase_credential, user_id)
    
    # Obtener los generos en común
    generos_comunes = set(user_df['genero']).intersection(set(brand_df['genero']))
    
    # Si no hay generos en común la afinidad es del 0%
    if len(generos_comunes) == 0:
        return 0.0  
    
    user_df_filtrado = user_df[user_df['genero'].isin(generos_comunes)]
    brand_df_filtrado = brand_df[brand_df['genero'].isin(generos_comunes)]

    # Reseteamos el Index
    user_df_filtrado.reset_index(drop=True, inplace=True)
    brand_df_filtrado.reset_index(drop=True, inplace=True)

    # Asignar pesos en base a la posición en el ranking
    user_df_filtrado["peso"] = 1 / user_df_filtrado["ranking"]
    brand_df_filtrado["peso"] = 1 / brand_df_filtrado["ranking"]

    # Normalizar los pesos para evitar sesgos por diferencias de tamaño
    user_df_filtrado["peso"] /= user_df_filtrado["peso"].sum()
    brand_df_filtrado["peso"] /= brand_df_filtrado["peso"].sum()

    # Poner como index genero y peso se queda como columna
    pesos_user = user_df_filtrado.set_index("genero")["peso"]
    pesos_brand = brand_df_filtrado.set_index("genero")["peso"]

    # Ordenamos los generos por orden alfabético para que los vectores estén alineados
    sorted_pesos = sorted(set(pesos_user.index).intersection(set(pesos_brand.index)))

    # Si solo hay un genero en común, asumimos 100% de afinidad
    if len(sorted_pesos) == 1:
        return 100.0 

    # Generamos los vectores
    user_vector = np.array([pesos_user.get(a, 0) for a in sorted_pesos])
    brand_vector = np.array([pesos_brand.get(a, 0) for a in sorted_pesos])

    # Crear matriz de comparación
    matriz_pesos = np.vstack([user_vector, brand_vector])

    # Calcular la matriz de distancias con pdist
    matriz_distancias = squareform(pdist(matriz_pesos, metric="euclidean"))

    # Extraer la distancia entre usuario y marca
    distancia = matriz_distancias[0, 1]

    # Convertimos la distancia en afinidad (invirtiendo la escala)
    afinidad = max(0, (1 - distancia) * 100)

    return float(round(afinidad,2))

#######################################################################################
##                        Sistema Recomendación por Subgénero                        ##
#######################################################################################
def get_brand_subgenre_ranking(supabase_credential,brand_id):
    brand_ranking = supabase_credential.table("subgenres").select("subgenre_name","number_of_appearances").eq("brand_id",brand_id).order("number_of_appearances",desc=True).execute().data
    generos = []
    apariciones = []
    for ranking in brand_ranking:
        generos.append(ranking["subgenre_name"])
        apariciones.append(ranking["number_of_appearances"])

    brand_df = pd.DataFrame({
        "subgenero" : generos,
        "apariciones" : apariciones
    })

    brand_df.index = brand_df.index + 1
    brand_df.reset_index(inplace=True)
    brand_df.columns = ["ranking","subgenero","apariciones"]
    brand_df.drop(columns="apariciones",inplace=True)
    brand_df["subgenero"] = brand_df["subgenero"].astype(str)
    return brand_df

def get_user_subgenre_ranking(supabase_credential,user_id):
    user_ranking = supabase_credential.table("user_subgenres").select("subgenre_name","number_of_appearances").eq("user_id",user_id).order("number_of_appearances",desc=True).execute().data
    generos = []
    apariciones = []
    for ranking in user_ranking:
        generos.append(ranking["subgenre_name"])
        apariciones.append(ranking["number_of_appearances"])

    user_df = pd.DataFrame({
        "subgenero" : generos,
        "apariciones" : apariciones
    })

    user_df.index = user_df.index + 1
    user_df.reset_index(inplace=True)
    user_df.columns = ["ranking","subgenero","apariciones"]
    user_df.drop(columns="apariciones",inplace=True)
    user_df["subgenero"] = user_df["subgenero"].astype(str)
    return user_df

def obtener_afinidad_por_subgenero(supabase_credential,brand_id,user_id):
    # Obtener los rankings de la marca y el usuario
    brand_df = get_brand_subgenre_ranking(supabase_credential, brand_id)
    user_df = get_user_subgenre_ranking(supabase_credential, user_id)
    
    # Obtener los subgeneros en común
    generos_comunes = set(user_df['subgenero']).intersection(set(brand_df['subgenero']))
    
    # Si no hay subgeneros en común la afinidad es del 0%
    if len(generos_comunes) == 0:
        return 0.0  
    
    user_df_filtrado = user_df[user_df['subgenero'].isin(generos_comunes)]
    brand_df_filtrado = brand_df[brand_df['subgenero'].isin(generos_comunes)]

    # Reseteamos el Index
    user_df_filtrado.reset_index(drop=True, inplace=True)
    brand_df_filtrado.reset_index(drop=True, inplace=True)

    # Asignar pesos en base a la posición en el ranking
    user_df_filtrado["peso"] = 1 / user_df_filtrado["ranking"]
    brand_df_filtrado["peso"] = 1 / brand_df_filtrado["ranking"]

    # Normalizar los pesos para evitar sesgos por diferencias de tamaño
    user_df_filtrado["peso"] /= user_df_filtrado["peso"].sum()
    brand_df_filtrado["peso"] /= brand_df_filtrado["peso"].sum()

    # Poner como index subgeneros y peso se queda como columna
    pesos_user = user_df_filtrado.set_index("subgenero")["peso"]
    pesos_brand = brand_df_filtrado.set_index("subgenero")["peso"]

    # Ordenamos los subgeneros por orden alfabético para que los vectores estén alineados
    sorted_pesos = sorted(set(pesos_user.index).intersection(set(pesos_brand.index)))

    # Si solo hay un subgenero en común, asumimos 100% de afinidad
    if len(sorted_pesos) == 1:
        return 100.0 

    # Generamos los vectores
    user_vector = np.array([pesos_user.get(a, 0) for a in sorted_pesos])
    brand_vector = np.array([pesos_brand.get(a, 0) for a in sorted_pesos])

    # Crear matriz de comparación
    matriz_pesos = np.vstack([user_vector, brand_vector])

    # Calcular la matriz de distancias con pdist
    matriz_distancias = squareform(pdist(matriz_pesos, metric="euclidean"))

    # Extraer la distancia entre usuario y marca
    distancia = matriz_distancias[0, 1]

    # Convertimos la distancia en afinidad (invirtiendo la escala)
    afinidad = max(0, (1 - distancia) * 100)

    return float(round(afinidad,2))