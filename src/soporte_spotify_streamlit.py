import sys
sys.path.append("../")
import pandas as pd
import src.soporte_spotify as api
import src.soporte_sql as sql


def get_current_user(sp):
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

def get_all_saved_tracks(sp, limit=50):

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

def get_all_top_tracks(sp, limit=20):

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
