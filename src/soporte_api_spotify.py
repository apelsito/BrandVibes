import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import os
import sys
from tqdm import tqdm 
sys.path.append("../")
from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from datetime import datetime

from spotipy.oauth2 import SpotifyOAuth

def load_credentials():
    CLIENT_ID = os.getenv("client_ID")
    CLIENT_SECRET = os.getenv("client_Secret")
    REDIRECT_URI = "http://localhost:3000"
    SCOPES = (
        "user-read-private user-read-email user-library-read user-library-modify "
        "playlist-read-private playlist-read-collaborative playlist-modify-public "
        "playlist-modify-private user-top-read user-read-recently-played "
        "user-read-currently-playing user-read-playback-state user-modify-playback-state "
        "streaming user-follow-read user-follow-modify app-remote-control ugc-image-upload"
    )

    # Autenticación
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPES
    ))

    return sp

def create_credentials():
    """
    Crea las credenciales para acceder a la API de Spotify utilizando las variables de entorno CLIENT_ID y CLIENT_SECRET.

    Returns:
        sp (spotipy.Spotify): Objeto de la clase Spotify con las credenciales para realizar peticiones a la API.
    """


    # The above code is setting the client secret and client id to the environment variables.
    CLIENT_SECRET = os.getenv("client_Secret")
    CLIENT_ID = os.getenv("client_ID")

    # Creating a Spotify object that will be used to make requests to the Spotify API.
    credenciales = SpotifyClientCredentials(CLIENT_ID, CLIENT_SECRET)
    sp = spotipy.Spotify(client_credentials_manager = credenciales)

    return sp

def prepare_url(link):
    """
    Extrae el URI de la playlist a partir de su URL completa de Spotify.

    Args:
        link (str): URL de la playlist de Spotify.

    Returns:
        playlist_URI (str): URI de la playlist.
    """

    playlist_URI = link.split("/")[-1].split("?")[0]
    return playlist_URI



def extract_songs(conexion, playlist_URI):
    """
    Extrae todas las canciones de una playlist de Spotify usando su URI.

    Args:
        conexion (spotipy.Spotify): Objeto de la clase Spotify con las credenciales de acceso a la API.
        playlist_URI (str): URI de la playlist.

    Returns:
        all_data (list): Lista con todas las canciones y sus características obtenidas del endpoint playlist_tracks.
    """

    numero_canciones = conexion.playlist_tracks(playlist_URI, limit = 1)["total"]
    numero_canciones = int(str(numero_canciones + 100)[0])
    print(numero_canciones)
    offset = 0
    all_data = []
    for i in range(numero_canciones):
        all_data.append(conexion.playlist_tracks(playlist_URI, offset=offset)["items"])
        offset += 100
    return all_data


def add_to_dict(dictionary, data):
    """
    Añade datos a un diccionario de listas.

    Args:
        dictionary (dict): Diccionario donde se agregarán los datos.
        data (dict): Datos a agregar, donde las claves coinciden con las del diccionario.
    """

    for key, value in data.items():
        dictionary[key].append(value)

def clean_data(all_data):
    """
    Limpia los datos de las canciones y devuelve un DataFrame con la información seleccionada.

    Args:
        all_data (list): Lista con todas las canciones y sus características, resultado del endpoint playlist_tracks.

    Returns:
        df (pandas.DataFrame): DataFrame con la información seleccionada.
    """

    basic_info = {
        "song": [], 
        "artist": [], 
        "date": [], 
        "explicit": [], 
        "uri_cancion": [], 
        "popularity": [], 
        "usuario": [], 
        "links": [], 
        'uri_artista': []
    }

    for playlist in all_data: 
        for track_info in playlist: 
            track = track_info["track"]
            artistas = track["artists"]

            # Manejar uno o varios artistas
            if len(artistas) == 1:
                artist_name = artistas[0]["name"]
                artist_uri = artistas[0]["id"]
            else:
                artist_name = ", ".join([artist["name"] for artist in artistas])
                artist_uri = [artist["id"] for artist in artistas]

            # Preparar el diccionario con la información a agregar
            data = {
                "uri_cancion": track["uri"],
                "song": track["name"],
                "date": track["album"]["release_date"],
                "explicit": track["explicit"],
                "popularity": track["popularity"],
                "usuario": track_info["added_by"]["id"],
                "links": track["external_urls"]["spotify"],
                "artist": artist_name,
                "uri_artista": artist_uri
            }

            # Añadir la información al diccionario basic_info
            add_to_dict(basic_info, data)

    # Crear DataFrame a partir del diccionario
    df = pd.DataFrame(basic_info)
    
    return df

def get_features(conexion, df_basic_info, list_uris_songs):
    """
    Obtiene los detalles de las características de audio de las canciones (audio features) a partir de sus URIs.

    Args:
        conexion (spotipy.Spotify): Objeto de la clase Spotify con las credenciales de acceso a la API.
        df_basic_info (pandas.DataFrame): DataFrame con la información básica de las canciones.
        list_uris_songs (list): Lista de URIs de canciones.

    Returns:
        final (pandas.DataFrame): DataFrame final con la información básica y las características de audio.
    """
    
    features = []
    for track in tqdm(list_uris_songs):
        try:
            features.append(conexion.audio_features(track))
        except:
            print(track)

        
        
    df = pd.DataFrame(features)
    df_features = df[0].apply(pd.Series)
    final = pd.merge(df_basic_info, df_features,  left_on='uri_cancion', right_on="uri")
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')
    final.to_csv(f"../data/basic_info_{fecha_hoy}.csv")
    return final

def clean_df(df):
    """
    Explota (separa) los valores de las listas en las columnas de artistas y URIs, guardando un nuevo DataFrame con la información limpia.

    Args:
        df (pandas.DataFrame): DataFrame con la información básica de las canciones.

    Returns:
        df (pandas.DataFrame): DataFrame con las columnas de canciones, artistas y URIs separadas.
    """
   
    df = df.explode("artist")
    df = df.explode("uri_artista")
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')
    df.to_csv(f"../data/basic_info_{fecha_hoy}.csv")
    return df[["song", "date", "popularity", "usuario", "artist", "uri_artista",  "uri_cancion"]]


def get_artist_album(conexion, artist_uri):
    """
    Extrae la información de los álbumes de los artistas dados, crea un DataFrame con los datos y lo guarda en un archivo CSV.

    Args:
        conexion (spotipy.Spotify): Objeto de la clase Spotify con las credenciales de acceso a la API.
        artist_uri (list): Lista de URIs de artistas.

    Returns:
        df_artistas (pandas.DataFrame): DataFrame con la información de los álbumes de los artistas.
    """
    # Lista para almacenar la información de los álbumes
    albumes_data = []

    for artista in tqdm(artist_uri):
        albumes = conexion.artist_albums(artista)["items"]

        for album in albumes:
            albumes_data.append({
                "artist_name": album["artists"][0]["name"],
                "album_name": album["name"].title(),  # Convertir el nombre del álbum a título
                "release_date": album["release_date"],
                "total_tracks": album["total_tracks"]
            })

    # Crear DataFrame a partir de la lista
    df_artistas = pd.DataFrame(albumes_data)
    
    # Eliminar duplicados por el nombre del álbum
    df_artistas.drop_duplicates(subset="album_name", inplace=True)
    
    # Guardar en un archivo CSV
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')
    df_artistas.to_csv(f"../data/albums_artistas_{fecha_hoy}.csv", index=False)

    return df_artistas


def get_artist_data(conexion, artist_uri):
    """
    Extrae la información de los artistas, crea un DataFrame con los datos y lo guarda en un archivo CSV.

    Args:
        conexion (spotipy.Spotify): Objeto de la clase Spotify con las credenciales de acceso a la API.
        artist_uri (list): Lista de URIs de artistas.

    Returns:
        df_artistas_info (pandas.DataFrame): DataFrame con la información de los artistas (nombre, seguidores, géneros, popularidad).
    """
    # Lista para acumular los datos de los artistas
    artistas_data = []

    for artista in tqdm(artist_uri):
        info = conexion.artist(artista)
        
        artistas_data.append({
            "artist_name": info['name'],
            "artist_id": info['id'],
            "followers": info["followers"]["total"],
            "genres": info["genres"],
            "popularity": info["popularity"]
        })

    # Convertir la lista a DataFrame
    df_artistas_info = pd.DataFrame(artistas_data)
    
    # Eliminar duplicados por el nombre del artista
    df_artistas_info.drop_duplicates(subset="artist_name", inplace=True)
    
    # Guardar los datos en un archivo CSV
    fecha_hoy = datetime.today().strftime('%Y-%m-%d')
    df_artistas_info.to_csv(f"../data/info_artistas_{fecha_hoy}.csv", index=False)

    return df_artistas_info