
# Importamos las librerías que necesitamos

# Librerías de extracción de datos
# -----------------------------------------------------------------------
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
# Tratamiento de datos
# -----------------------------------------------------------------------
import pandas as pd
import numpy as np
import datetime

# Importamos las librerías que necesitamos

# Librerías de extracción de datos
# -----------------------------------------------------------------------

# Importaciones:
# Beautifulsoup
from bs4 import BeautifulSoup

# Requests
import requests
import base64

import pandas as pd
import numpy as np

from time import sleep
import random
# Importar librerías para automatización de navegadores web con Selenium
# -----------------------------------------------------------------------
from selenium import webdriver  # Selenium es una herramienta para automatizar la interacción con navegadores web.
from webdriver_manager.chrome import ChromeDriverManager  # ChromeDriverManager gestiona la instalación del controlador de Chrome.
from selenium.webdriver.common.keys import Keys  # Keys es útil para simular eventos de teclado en Selenium.
from selenium.webdriver.support.ui import Select  # Select se utiliza para interactuar con elementos <select> en páginas web.
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException # Excepciones comunes de selenium que nos podemos encontrar 
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import os
import sys
from tqdm import tqdm 
sys.path.append("../")
from dotenv import load_dotenv
load_dotenv(dotenv_path="../")
#import streamlit as st
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
    ), requests_timeout=50)

    return sp


def request_token(silent = False):
    # 1. Credenciales de la aplicación
    CLIENT_ID = os.getenv("client_ID")
    CLIENT_SECRET = os.getenv("client_Secret")

    # 2. URL para obtener el token
    AUTH_URL = "https://accounts.spotify.com/api/token"

    # 3. Solicitar el token de acceso
    auth_data = {
        "grant_type": "client_credentials"
    }
    auth_headers = {
        "Authorization": f"Basic {base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()}"
    }

    response = requests.post(AUTH_URL, data=auth_data, headers=auth_headers)

    if response.status_code == 200:
        access_token = response.json()["access_token"]
        if silent == False:
            print("Token obtenido con éxito")
    else:
        print("Error al obtener el token:", response.json())
        exit()
    
    return access_token


def obtener_html_followers(user):
    # Iniciar el driver
    driver = webdriver.Chrome()
    url = f"https://open.spotify.com/user/{user}/followers"
    # Navegar a la página
    driver.get(url)
    sleep(2)
    #Maximizar ventana
    driver.maximize_window() 
    sleep(2)
    # Aceptar cookies	
    driver.find_element("css selector", "#onetrust-accept-btn-handler").click()
    # Esperar a que la página cargue
    sleep(2) 
    # Obtener el contenido completo después de cargar el JavaScript
    page_content = driver.page_source
            
    # Usar BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(page_content, "html.parser")
    driver.quit()
    return soup

def extraer_ids_usuario(sp,marca, html):
    print("Iniciando Extracción de Ids Usuario")
    followers = html.findAll("div",{"class":"Box__BoxComponent-sc-y4nds-0 kcRGDn Box-sc-1njtxi4-0 hscyXl aAYpzGljXQv1_zfopxaH Card"})
    id_followers = []
    for follower in followers:
        quitar_html = str(follower).split(" ")[1]
        quedarse_user = quitar_html.split("-")[-2]
        solo_id_user = quedarse_user.split(":")[-1]
        id_followers.append(solo_id_user)

    brand = []
    usernames = []
    users_id = []
    for user in tqdm(id_followers):
        try:
            usernames.append(sp.user(user)["display_name"])
            users_id.append(user)
            brand.append(marca)
        except:
            print(f"No se ha podido obtener el usuario {user}")

    df = pd.DataFrame({
        'brand': brand,
        'username': usernames,
        'user_id': users_id
    })
    return df

def obtener_playlists(sp, user_id):
    playlists = sp.user_playlists(user_id)
    dictio = {}

    if not playlists['items']:
        return "No playlists"
    
    # Iterar sobre todas las playlists (manejar paginación)
    while playlists:
        for playlist in playlists['items']:
            dictio[playlist["name"]] = playlist["id"]

        # Verificar si hay más páginas de playlists
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return dictio

def request_segura(url, token):
    """
    Verifica si la API de Spotify está disponible.
    Si devuelve 200, devuelve True.
    Si devuelve 429, espera el tiempo necesario.
    """
    while True:
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 200:
            return True
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Error 429: Rate limit alcanzado. Esperando {retry_after} segundos...")
            sleep(retry_after)
        else:
            print(f"Error {response.status_code}. Verifica la solicitud.")
            return False  # No se pudo procesar


def obtener_artistas(sp, lista_ids_playlists):
    """
    Usa `requests` para verificar la disponibilidad y `spotipy` para procesar los datos.
    """
    dictio_artistas = {}
    token = request_token(silent=True)  # Obtener el token una sola vez

    for playlist_id in lista_ids_playlists:
        # Construir la URL para verificar con `requests`
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"

        # Verificar disponibilidad con `requests`
        if not request_segura(url, token):
            print(f"No se pudo procesar la playlist {playlist_id}.")
            continue

        # Usar `spotipy` para procesar las canciones
        canciones = sp.playlist_tracks(
            playlist_id, 
            fields="items.track(artists.name,artists.id),next", 
            additional_types=("track",)
        )

        while canciones:
            # Sacar canciones de la página actual
            for cancion in canciones["items"]:
                track = cancion["track"]
                if track and "artists" in track: # Verficar que la canción no sea None
                    for artist in track["artists"]:
                        if artist["id"] not in dictio_artistas:
                            dictio_artistas[artist["id"]] = artist["name"]

            # Verificar si hay más páginas
            if canciones["next"]:
                canciones = sp.next(canciones)
            else:
                canciones = None
    return dictio_artistas
