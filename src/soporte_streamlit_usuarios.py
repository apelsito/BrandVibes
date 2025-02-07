#######################################################################################
##            Manejo del sistema y rutas de archivos                                 ##
#######################################################################################
# Para interactuar con el sistema operativo (rutas de archivos)
import os  
# Para modificar las rutas de búsqueda de módulos
import sys  

#######################################################################################
##            Manejo de datos y procesamiento                                        ##
#######################################################################################
# Para manipulación y análisis de datos tabulares (DataFrames)
import pandas as pd  
# Para cálculos matemáticos y manejo de matrices
import numpy as np  
# Para trabajar con datos en formato JSON
import json  
# Para controlar y suprimir advertencias
import warnings  
# Suprimir advertencias para mantener la salida más limpia
warnings.filterwarnings("ignore")  

#######################################################################################
##            Cálculos y distancia                                                   ##
#######################################################################################
# Para cálculos de distancia euclidiana
from scipy.spatial.distance import pdist, squareform  

#######################################################################################
##            Funciones personalizadas para Spotify y Base de Datos                  ##
#######################################################################################
# Funciones para interactuar con la API de Spotify
import src.soporte_spotify as api  
# Funciones para manejar la base de datos SQL
import src.soporte_sql as sql  

#######################################################################################
##            Configuración y manejo de datos iniciales                              ##
#######################################################################################

# Obtiene la ruta absoluta del script
# Esto se realiza para que la aplicación en Streamlit, cuando esté desplegada, 
# pueda leer correctamente la ruta al archivo en el repositorio, sin importar 
# dónde se ejecute el código en el entorno de producción.
base_path = os.path.dirname(os.path.abspath(__file__))  

# Ruta del archivo JSON con los géneros
# Se construye la ruta completa al archivo JSON que contiene el mapeo de géneros.
# Esta ruta se genera de manera relativa, permitiendo que funcione tanto en 
# el entorno local como en la versión desplegada de la aplicación en Streamlit.
file_path = os.path.join(base_path, "../datos/00_Spotify_Genres/genres_dict.json")

#######################################################################################
##            Fin de los Imports                                                     ##
#######################################################################################



#######################################################################################
##            Obtener Datos Iniciales User y subir a la Base de datos                ##
#######################################################################################
def generate_current_user(sp):
    """
    Obtiene los datos del usuario actual de Spotify y los almacena en la base de datos.

    Parámetros:
    ----------
    sp : spotipy.Spotify
        Objeto de autenticación de la API de Spotify con acceso al usuario actual.

    Retorna:
    -------
    None

    Descripción:
    -----------
    - Recupera la información del usuario autenticado desde la API de Spotify.
    - Crea un DataFrame con los datos relevantes: ID de usuario, nombre, URL de Spotify, email y tipo de suscripción.
    - Establece una conexión con la base de datos mediante `sql.conectar_bd()`.
    - Inserta los datos del usuario en la tabla `users` usando una consulta SQL parametrizada.
    """

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
    """
    Obtiene todas las canciones guardadas por el usuario en su biblioteca de Spotify y las almacena en la base de datos.

    Parámetros:
    ----------
    sp : spotipy.Spotify
        Objeto de autenticación de la API de Spotify con acceso al usuario actual.

    limit : int, opcional (por defecto 50)
        Número máximo de canciones a recuperar por cada solicitud paginada.

    Retorna:
    -------
    None

    Descripción:
    -----------
    - Recupera todas las canciones guardadas del usuario usando paginación.
    - Extrae los datos relevantes de cada canción, incluyendo:
        - ID de usuario
        - Nombre de la canción
        - ID de la canción
        - Popularidad
        - URL de la canción en Spotify
        - Nombre del artista
        - ID del artista
        - URL del artista en Spotify
        - Fecha en que el usuario guardó la canción
    - Organiza la información en un DataFrame de Pandas.
    - Establece una conexión con la base de datos mediante `sql.conectar_bd()`.
    - Inserta los datos en la tabla `tracks_user_likes` usando una consulta SQL parametrizada.
    """

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
    """
    Obtiene las canciones más escuchadas por el usuario en Spotify a largo plazo y las almacena en la base de datos.

    Parámetros:
    ----------
    sp : spotipy.Spotify
        Objeto de autenticación de la API de Spotify con acceso al usuario actual.

    limit : int, opcional (por defecto 20)
        Número máximo de canciones a recuperar por cada solicitud paginada.

    Retorna:
    -------
    None

    Descripción:
    -----------
    - Recupera las canciones más escuchadas del usuario en el período de largo plazo ("long_term") usando paginación.
    - Extrae los datos relevantes de cada canción, incluyendo:
        - ID de usuario
        - Ranking de la canción
        - Nombre de la canción
        - ID de la canción
        - Popularidad
        - URL de la canción en Spotify
        - Nombre del artista
        - ID del artista
        - URL del artista en Spotify
    - Organiza la información en un DataFrame de Pandas con un índice basado en el ranking.
    - Establece una conexión con la base de datos mediante `sql.conectar_bd()`.
    - Inserta los datos en la tabla `top_tracks` usando una consulta SQL parametrizada.
    """

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
    """
    Genera un ranking de artistas basado en las canciones guardadas y las más escuchadas por el usuario en Spotify, y lo almacena en la base de datos.

    Parámetros:
    ----------
    sp : spotipy.Spotify
        Objeto de autenticación de la API de Spotify con acceso al usuario actual.
    
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    Retorna:
    -------
    None

    Descripción:
    -----------
    - Obtiene el ID del usuario actual de Spotify.
    - Recupera los artistas de las canciones más escuchadas (`top_tracks`) y las canciones guardadas (`tracks_user_likes`) desde Supabase.
    - Combina los nombres de los artistas en una lista.
    - Genera un DataFrame que cuenta la frecuencia de aparición de cada artista.
    - Formatea el DataFrame para incluir el ID de usuario y los artistas con su número de apariciones.
    - Establece una conexión con la base de datos mediante `sql.conectar_bd()`.
    - Inserta los datos en la tabla `user_artists_ranking` usando una consulta SQL parametrizada.
    """

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

    Funciona tanto en local como en Streamlit Community Cloud.

    Retorna:
    --------
    dictio_genres : dict
        Un diccionario donde las claves son los subgéneros y los valores son los géneros principales.

    Proceso:
    --------
    1. Detecta la ruta absoluta de ejecución.
    2. Construye la ruta correcta del archivo JSON sin importar el entorno.
    3. Carga los datos y crea el diccionario de mapeo.

    Notas:
    ------
    - El archivo JSON debe tener una clave llamada "genres_map" que contenga el mapeo entre géneros principales y subgéneros.
    """

    # Obtiene la ruta del directorio actual del script
    base_path = os.path.dirname(os.path.abspath(__file__))

    # Construye la ruta del archivo JSON de manera segura
    file_path = os.path.join(base_path, "..", "datos", "00_Spotify_Genres", "genres_dict.json")

    # Carga el archivo JSON y construye el diccionario de mapeo
    with open(file_path, "r", encoding="utf-8") as file:
        genres_mapping = json.load(file)

    dictio_genres = {subgenre: main_genre for main_genre, subgenres in genres_mapping["genres_map"].items() for subgenre in subgenres}
    
    return dictio_genres
#######################################################################################
##              Obtener Géneros y Subgéneros y subir a la Base de Datos              ##
#######################################################################################
def generate_user_genre_and_subgenre_ranking(sp, supabase_credential):
    """
    Genera y almacena un ranking de géneros y subgéneros musicales basado en los artistas más escuchados y las canciones guardadas del usuario en Spotify.

    Parámetros:
    ----------
    sp : spotipy.Spotify
        Objeto de autenticación de la API de Spotify con acceso al usuario actual.
    
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    Retorna:
    -------
    None

    Descripción:
    -----------
    - Obtiene el ID del usuario actual de Spotify.
    - Recupera los artistas de las canciones más escuchadas (`top_tracks`) y las canciones guardadas (`tracks_user_likes`) desde Supabase.
    - Extrae los nombres e identificadores de los artistas en listas y genera un diccionario único de ID de artista a nombre de artista.
    - Solicita un token de autenticación y obtiene los subgéneros asociados a los artistas.
    - Crea un DataFrame con los subgéneros y su número de apariciones.
    - Inserta los datos en la tabla `user_subgenres` en la base de datos.
    - Utiliza un mapeo de subgéneros a géneros principales (`mapeo_genres`) para agrupar los subgéneros en géneros principales.
    - Cuenta las apariciones de cada género principal y crea un ranking.
    - Inserta los datos en la tabla `user_main_genres` en la base de datos.
    """

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
    """
    Obtiene el ranking de los artistas más escuchados por un usuario desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    user_id : str
        Identificador único del usuario en Spotify cuyos artistas más escuchados se desean obtener.

    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    Retorna:
    -------
    list[dict]
        Lista de diccionarios con los artistas más escuchados y el número de veces que aparecen en las playlists del usuario.

    Descripción:
    -----------
    - Consulta la tabla `user_artists_ranking` en Supabase para obtener los artistas más escuchados por el usuario.
    - Filtra por `user_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Permite paginar los resultados utilizando los parámetros `start` y `end`.
    - Devuelve una lista de diccionarios con los nombres de los artistas y su número de apariciones.
    """

    # Primero obtenemos el id de los seguidores de la marca 
    ranking_response = supabase_credential.table("user_artists_ranking").select("artist_name", "number_of_appearances").eq("user_id", user_id).range(start,end).order('number_of_appearances',desc=True).execute().data

    return ranking_response
    
def obtener_resto_artistas(supabase_credential, user_id, start = 0, end = 0):
    """
    Obtiene un DataFrame con el ranking de los artistas menos escuchados por un usuario desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    user_id : str
        Identificador único del usuario en Spotify cuyos artistas menos escuchados se desean obtener.

    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de artistas, sus nombres y la cantidad de veces que han sido escuchados.

    Descripción:
    -----------
    - Consulta la tabla `user_artists_ranking` en Supabase para obtener los artistas menos escuchados del usuario.
    - Filtra por `user_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los artistas y su cantidad de apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "Ranking", "Artista" y "Cantidad de escuchas".
    """

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
    """
    Obtiene el ranking de los géneros musicales más escuchados por un usuario desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    user_id : str
        Identificador único del usuario en Spotify cuyos géneros más escuchados se desean obtener.

    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    Retorna:
    -------
    list[dict]
        Lista de diccionarios con los géneros más escuchados y el número de veces que aparecen en las playlists del usuario.

    Descripción:
    -----------
    - Consulta la tabla `user_main_genres` en Supabase para obtener los géneros más escuchados por el usuario.
    - Filtra por `user_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Permite paginar los resultados utilizando los parámetros `start` y `end`.
    - Devuelve una lista de diccionarios con los nombres de los géneros y su número de apariciones.
    """

    # Primero obtenemos el id de los seguidores de la marca
    ranking_response = supabase_credential.table("user_main_genres").select("genre_name", "number_of_appearances").eq("user_id", user_id).range(start,end).order('number_of_appearances',desc=True).execute().data
        
    return ranking_response
    
def obtener_resto_generos(supabase_credential, user_id, start = 0, end = 0):
    """
    Obtiene un DataFrame con el ranking de los géneros musicales menos escuchados por un usuario desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    user_id : str
        Identificador único del usuario en Spotify cuyos géneros menos escuchados se desean obtener.

    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de géneros, sus nombres y la cantidad de veces que han sido escuchados.

    Descripción:
    -----------
    - Consulta la tabla `user_main_genres` en Supabase para obtener los géneros menos escuchados del usuario.
    - Filtra por `user_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los géneros y su cantidad de apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "Ranking", "Género" y "Cantidad de escuchas".
    """

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
    """
    Obtiene el ranking de los subgéneros musicales más escuchados por un usuario desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    user_id : str
        Identificador único del usuario en Spotify cuyos subgéneros más escuchados se desean obtener.

    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    Retorna:
    -------
    list[dict]
        Lista de diccionarios con los subgéneros más escuchados y el número de veces que aparecen en las playlists del usuario.

    Descripción:
    -----------
    - Consulta la tabla `user_subgenres` en Supabase para obtener los subgéneros más escuchados por el usuario.
    - Filtra por `user_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Permite paginar los resultados utilizando los parámetros `start` y `end`.
    - Devuelve una lista de diccionarios con los nombres de los subgéneros y su número de apariciones.
    """

    # Primero obtenemos el id de los seguidores de la marca 
    ranking_response = supabase_credential.table("user_subgenres").select("subgenre_name", "number_of_appearances").eq("user_id", user_id).range(start,end).order('number_of_appearances',desc=True).execute().data
    return ranking_response
    
def obtener_resto_subgeneros(supabase_credential, user_id, start = 0, end = 0):
    """
    Obtiene un DataFrame con el ranking de los subgéneros musicales menos escuchados por un usuario desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    user_id : str
        Identificador único del usuario en Spotify cuyos subgéneros menos escuchados se desean obtener.

    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de subgéneros, sus nombres y la cantidad de veces que han sido escuchados.

    Descripción:
    -----------
    - Consulta la tabla `user_subgenres` en Supabase para obtener los subgéneros menos escuchados del usuario.
    - Filtra por `user_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los subgéneros y su cantidad de apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "Ranking", "Subgénero" y "Cantidad de escuchas".
    """

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
    """
    Obtiene un DataFrame con el ranking de artistas más escuchados por los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    brand_id : int
        Identificador único de la marca cuyos artistas más escuchados se desean obtener.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de artistas más escuchados de la marca.

    Descripción:
    -----------
    - Consulta la tabla `artists_ranking` en Supabase para obtener los artistas más escuchados de la marca.
    - Filtra por `brand_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los artistas y su ranking basado en apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "ranking" y "artista".
    """

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
    """
    Obtiene un DataFrame con el ranking de artistas más escuchados por un usuario desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    user_id : str
        Identificador único del usuario en Spotify cuyos artistas más escuchados se desean obtener.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de artistas más escuchados del usuario.

    Descripción:
    -----------
    - Consulta la tabla `user_artists_ranking` en Supabase para obtener los artistas más escuchados del usuario.
    - Filtra por `user_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los artistas y su ranking basado en apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "ranking" y "artista".
    """

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
    """
    Calcula el porcentaje de afinidad entre un usuario y una marca en base a los artistas que ambos tienen en común.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    brand_id : int
        Identificador único de la marca cuyo ranking de artistas se comparará.

    user_id : str
        Identificador único del usuario en Spotify cuyo ranking de artistas se comparará.

    Retorna:
    -------
    float
        Porcentaje de afinidad entre el usuario y la marca en base a sus artistas en común.

    Descripción:
    -----------
    - Obtiene los rankings de artistas de la marca y el usuario desde Supabase.
    - Encuentra los artistas en común entre ambos rankings.
    - Si no hay artistas en común, devuelve una afinidad del 0%.
    - Si solo hay un artista en común, asigna automáticamente un 100% de afinidad.
    - Asigna pesos a los artistas según su posición en el ranking.
    - Normaliza los pesos para evitar sesgos por diferencias de tamaño en los rankings.
    - Genera vectores de comparación con los pesos de cada artista en común.
    - Calcula la distancia euclidiana entre los vectores y la convierte en un porcentaje de afinidad.
    - Devuelve la afinidad como un valor entre 0 y 100.

    Nota:
    ----
    - A mayor similitud en los rankings de artistas, mayor será la afinidad calculada.
    """

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
    """
    Obtiene un DataFrame con el ranking de géneros musicales más escuchados por los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    brand_id : int
        Identificador único de la marca cuyos géneros más escuchados se desean obtener.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de géneros más escuchados de la marca.

    Descripción:
    -----------
    - Consulta la tabla `main_genres` en Supabase para obtener los géneros más escuchados de la marca.
    - Filtra por `brand_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los géneros y su ranking basado en apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "ranking" y "genero".
    """

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
    """
    Obtiene un DataFrame con el ranking de géneros musicales más escuchados por un usuario desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    user_id : str
        Identificador único del usuario en Spotify cuyos géneros más escuchados se desean obtener.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de géneros más escuchados del usuario.

    Descripción:
    -----------
    - Consulta la tabla `user_main_genres` en Supabase para obtener los géneros más escuchados del usuario.
    - Filtra por `user_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los géneros y su ranking basado en apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "ranking" y "genero".
    """

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
    """
    Calcula el porcentaje de afinidad entre un usuario y una marca en base a los géneros musicales que ambos tienen en común.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    brand_id : int
        Identificador único de la marca cuyo ranking de géneros se comparará.

    user_id : str
        Identificador único del usuario en Spotify cuyo ranking de géneros se comparará.

    Retorna:
    -------
    float
        Porcentaje de afinidad entre el usuario y la marca en base a sus géneros en común.

    Descripción:
    -----------
    - Obtiene los rankings de géneros de la marca y el usuario desde Supabase.
    - Encuentra los géneros en común entre ambos rankings.
    - Si no hay géneros en común, devuelve una afinidad del 0%.
    - Si solo hay un género en común, asigna automáticamente un 100% de afinidad.
    - Asigna pesos a los géneros según su posición en el ranking.
    - Normaliza los pesos para evitar sesgos por diferencias de tamaño en los rankings.
    - Genera vectores de comparación con los pesos de cada género en común.
    - Calcula la distancia euclidiana entre los vectores y la convierte en un porcentaje de afinidad.
    - Devuelve la afinidad como un valor entre 0 y 100.

    Nota:
    ----
    - A mayor similitud en los rankings de géneros, mayor será la afinidad calculada.
    """

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
    """
    Obtiene un DataFrame con el ranking de subgéneros musicales más escuchados por los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    brand_id : int
        Identificador único de la marca cuyos subgéneros más escuchados se desean obtener.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de subgéneros más escuchados de la marca.

    Descripción:
    -----------
    - Consulta la tabla `subgenres` en Supabase para obtener los subgéneros más escuchados de la marca.
    - Filtra por `brand_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los subgéneros y su ranking basado en apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "ranking" y "subgenero".
    """

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
    """
    Obtiene un DataFrame con el ranking de subgéneros musicales más escuchados por un usuario desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    user_id : str
        Identificador único del usuario en Spotify cuyos subgéneros más escuchados se desean obtener.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de subgéneros más escuchados del usuario.

    Descripción:
    -----------
    - Consulta la tabla `user_subgenres` en Supabase para obtener los subgéneros más escuchados del usuario.
    - Filtra por `user_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los subgéneros y su ranking basado en apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "ranking" y "subgenero".
    """

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
    """
    Calcula el porcentaje de afinidad entre un usuario y una marca en base a los subgéneros musicales que ambos tienen en común.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.

    brand_id : int
        Identificador único de la marca cuyo ranking de subgéneros se comparará.

    user_id : str
        Identificador único del usuario en Spotify cuyo ranking de subgéneros se comparará.

    Retorna:
    -------
    float
        Porcentaje de afinidad entre el usuario y la marca en base a sus subgéneros en común.

    Descripción:
    -----------
    - Obtiene los rankings de subgéneros de la marca y el usuario desde Supabase.
    - Encuentra los subgéneros en común entre ambos rankings.
    - Si no hay subgéneros en común, devuelve una afinidad del 0%.
    - Si solo hay un subgénero en común, asigna automáticamente un 100% de afinidad.
    - Asigna pesos a los subgéneros según su posición en el ranking.
    - Normaliza los pesos para evitar sesgos por diferencias de tamaño en los rankings.
    - Genera vectores de comparación con los pesos de cada subgénero en común.
    - Calcula la distancia euclidiana entre los vectores y la convierte en un porcentaje de afinidad.
    - Devuelve la afinidad como un valor entre 0 y 100.

    Nota:
    ----
    - A mayor similitud en los rankings de subgéneros, mayor será la afinidad calculada.
    """

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