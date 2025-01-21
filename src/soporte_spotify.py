# Importamos las librerías necesarias para el proyecto

# Librerías de extracción de datos
# -----------------------------------------------------------------------

from bs4 import BeautifulSoup  # Para analizar y extraer información de HTML o XML.
import requests  # Para realizar solicitudes HTTP a páginas web.
from tqdm import tqdm  # Barra de progreso para seguir el avance de iteraciones o procesos largos.

# Tratamiento de datos
# -----------------------------------------------------------------------

import pandas as pd  # Para manipulación y análisis de datos tabulares (DataFrames).
import numpy as np  # Para cálculos matemáticos y manejo de matrices.
import datetime  # Para trabajar con fechas y horas.

# Codificación y tiempo
# -----------------------------------------------------------------------

import base64  # Para codificar y decodificar datos en formato base64.
from time import sleep, time  # `sleep` para pausar la ejecución y `time` para medir tiempos.
import random  # Para generar valores aleatorios, útil en pausas para evitar detección de scraping.

# Automatización de navegadores web con Selenium
# -----------------------------------------------------------------------

from selenium import webdriver  # Para controlar navegadores web de forma automatizada.
from webdriver_manager.chrome import ChromeDriverManager  
# Instala automáticamente el controlador de Chrome, evitando configuraciones manuales.

from selenium.webdriver.common.keys import Keys  
# Para simular eventos de teclado, como presionar Enter, Tab, etc.

from selenium.webdriver.support.ui import Select  
# Para interactuar con menús desplegables (<select>) en páginas web.

from selenium.webdriver.support.ui import WebDriverWait  
# Espera explícita para garantizar que ciertos elementos estén presentes antes de interactuar.

from selenium.webdriver.support import expected_conditions as EC  
# Para definir condiciones específicas en las esperas explícitas (e.g., visibilidad de un elemento).

from selenium.common.exceptions import NoSuchElementException  
# Excepción que ocurre cuando Selenium no encuentra un elemento en la página.

# Integración con Spotify
# -----------------------------------------------------------------------

import spotipy  # Librería oficial de Spotify para interactuar con su API.
from spotipy.oauth2 import SpotifyClientCredentials  
# Para manejar autenticaciones basadas en cliente y credenciales secretas.

from spotipy.oauth2 import SpotifyOAuth  
# Para autenticación OAuth 2.0, necesaria para operaciones avanzadas como acceso a datos privados.

# Manejo del sistema y variables de entorno
# -----------------------------------------------------------------------
import os  # Para interactuar con el sistema operativo (rutas, variables de entorno, etc.).
import sys  # Para modificar y trabajar con la configuración del entorno de Python.

sys.path.append("../")  
# Agrega el directorio padre ("../") al sistema de rutas de búsqueda de módulos, permitiendo importar módulos desde ahí.

from dotenv import load_dotenv  
# Carga las variables de entorno definidas en un archivo `.env` para configuraciones sensibles como credenciales.

load_dotenv(dotenv_path="../")  
# Especifica la ubicación del archivo `.env` que contiene las variables de entorno.

# Interfaz y manejo de fechas
# -----------------------------------------------------------------------
from datetime import datetime  
# Manejo de fechas y horas de forma más avanzada y con múltiples formatos.

# streamlit
# import streamlit as st  
# Herramienta para crear dashboards interactivos, actualmente comentada en este código.

def load_credentials():
    """
    Carga las credenciales de Spotify desde las variables de entorno y configura la autenticación OAuth.

    Retorna:
    --------
    sp : spotipy.Spotify
        Objeto autenticado de la API de Spotify listo para realizar consultas y operaciones.

    Proceso:
    --------
    1. Obtiene las credenciales necesarias desde las variables de entorno:
        - `client_ID`: Identificador del cliente proporcionado por Spotify.
        - `client_Secret`: Secreto del cliente proporcionado por Spotify.
        - `REDIRECT_URI`: URI de redirección para completar la autenticación OAuth.
        - `SCOPES`: Permisos que se solicitan al usuario, definidos como una cadena separada por espacios.
        
    2. Configura la autenticación OAuth con la clase `SpotifyOAuth` de Spotipy:
        - Proporciona el `client_id`, `client_secret`, `redirect_uri` y el alcance (`scope`) necesario.

    3. Crea una instancia del cliente de la API de Spotify (`spotipy.Spotify`) utilizando el autenticador configurado.

    4. Retorna el objeto autenticado (`sp`) para interactuar con la API de Spotify.

    Notas:
    ------
    - **Variables de entorno:** Asegúrate de que las variables `client_ID` y `client_Secret` estén definidas en un archivo `.env` o en el entorno del sistema.
    - **REDIRECT_URI:** Es una URL necesaria para el flujo de autenticación OAuth. Debe coincidir con la configuración en la cuenta de desarrollador de Spotify.
    - **SCOPES:** Define los permisos requeridos para interactuar con diferentes partes de la API, como playlists, reproducción, y estado del usuario.
    - **Tiempo de espera (`requests_timeout`):** Se establece en 50 segundos para manejar posibles retrasos en las respuestas de la API.

    Ejemplo de uso:
    ---------------
    ```python
    sp = load_credentials()
    user_profile = sp.current_user()
    print(f"Usuario autenticado: {user_profile['display_name']}")
    """
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

def request_token(silent=False):
    """
    Solicita un token de acceso a Spotify utilizando el flujo Client Credentials.

    Devuelve:
    --------
    str
        Token de acceso válido para interactuar con la API de Spotify.

    Excepciones:
    ------------
    Exception
        - Si `CLIENT_ID` o `CLIENT_SECRET` no están configurados en las variables de entorno.
        - Si no se puede obtener el token debido a un error en la solicitud.

    Proceso:
    --------
    1. **Obtener las credenciales de la aplicación:**
    - Se cargan desde las variables de entorno `client_ID` y `client_Secret`.
    - Lanza una excepción si alguna de estas no está configurada.

    2. **Preparar la solicitud de token:**
    - URL del endpoint de autenticación de Spotify (`AUTH_URL`).
    - Datos para la solicitud:
        - `grant_type`: Fijo en `client_credentials`.
    - Encabezados:
        - `Authorization`: Codificación Base64 del `client_ID` y `client_Secret`.

    3. **Enviar la solicitud HTTP POST:**
    - Se envía la solicitud a `AUTH_URL` con los datos y encabezados necesarios.
    - Si el código de estado HTTP es `200`, se extrae el token de acceso del cuerpo de la respuesta.

    4. **Manejo de errores:**
    - Si ocurre un error, muestra el código de estado HTTP y el mensaje de error proporcionado por Spotify.
    - Si el mensaje no está disponible, muestra "Error desconocido".

    Parámetros:
    -----------
    silent : bool, opcional
        Si es `True`, suprime el mensaje de confirmación al obtener el token (por defecto es `False`).

    Notas:
    ------
    - **Variables de entorno:** Asegúrate de configurar correctamente `client_ID` y `client_Secret` en un archivo `.env` o en el sistema.
    - **Flujo Client Credentials:** Este flujo no requiere interacción del usuario, pero solo permite acceder a recursos públicos de Spotify.

    Ejemplo de uso:
    ---------------
    ```python
    token = request_token()
    print(f"Token de acceso: {token}")
    """
    # 1. Credenciales de la aplicación
    CLIENT_ID = os.getenv("client_ID")
    CLIENT_SECRET = os.getenv("client_Secret")
    
    if not CLIENT_ID or not CLIENT_SECRET:
        raise Exception("CLIENT_ID o CLIENT_SECRET no configurados. Asegúrate de configurar las variables de entorno correctamente.")

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
        if not silent:
            print("Token obtenido con éxito")
        return access_token
    else:
        error_message = response.json().get("error_description", "Error desconocido")
        raise Exception(f"Error al obtener el token: {response.status_code} - {error_message}")

def obtener_html_followers(user):
    """
    Obtiene el contenido HTML de la página de seguidores de un usuario de Spotify utilizando Selenium y BeautifulSoup.

    Parámetros:
    -----------
    user : str
        Identificador del usuario de Spotify cuya página de seguidores se desea analizar.

    Retorna:
    --------
    soup : BeautifulSoup
        Objeto BeautifulSoup que contiene el contenido HTML de la página después de que se haya cargado el JavaScript.

    Proceso:
    --------
    1. **Iniciar el navegador web con Selenium:**
    - Se utiliza `webdriver.Chrome()` para iniciar el navegador Google Chrome.
    - Navega a la URL de la página de seguidores del usuario especificado.

    2. **Interacción con la página:**
    - Maximiza la ventana del navegador para asegurarse de que los elementos sean visibles.
    - Acepta las cookies utilizando el selector CSS del botón de aceptación.

    3. **Esperas:**
    - Se utilizan `sleep()` para garantizar que los elementos de la página se carguen antes de interactuar con ellos.

    4. **Obtener el contenido HTML:**
    - Una vez que el JavaScript de la página ha terminado de cargar, se extrae el contenido con `driver.page_source`.

    5. **Analizar el contenido HTML con BeautifulSoup:**
    - Convierte el contenido extraído en un objeto `BeautifulSoup` para facilitar su análisis.

    6. **Cerrar el navegador:**
    - Finaliza la sesión de Selenium cerrando el navegador con `driver.quit()`.

    Notas:
    ------
    - **Cookies:** La función incluye una interacción específica para aceptar las cookies en la página de Spotify.
    - **Espera dinámica:** Sería mejor utilizar esperas explícitas con Selenium (`WebDriverWait`) en lugar de `sleep()` para mejorar la fiabilidad.
    - **Revisar el selector:** Asegúrate de que el selector CSS para aceptar cookies (`#onetrust-accept-btn-handler`) sigue siendo válido, ya que puede cambiar con el tiempo.

    Ejemplo de uso:
    ---------------
    ```python
    html_soup = obtener_html_followers("usuario123")
    print(html_soup.prettify())
    """
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
    """
    Extrae los IDs de usuarios seguidores y sus nombres de usuario asociados a una marca de Spotify.

    Parámetros:
    -----------
    sp : spotipy.Spotify
        Objeto autenticado de la API de Spotify, utilizado para obtener información de los usuarios.

    marca : str
        Nombre de la marca asociada a los seguidores extraídos.

    html : BeautifulSoup
        Objeto BeautifulSoup que contiene el HTML de la página de seguidores de la marca.

    Retorna:
    --------
    df : pandas.DataFrame
        DataFrame que contiene las siguientes columnas:
        - 'brand': Nombre de la marca asociada.
        - 'username': Nombre de usuario del seguidor.
        - 'user_id': Identificador único del usuario.

    Proceso:
    --------
    1. **Extraer bloques de seguidores del HTML:**
    - Encuentra todos los bloques de usuarios utilizando el selector CSS específico para seguidores.

    2. **Procesar y obtener IDs de seguidores:**
    - Itera sobre los bloques de seguidores.
    - Extrae y procesa el identificador único (`user_id`) de cada seguidor a partir de la estructura HTML.

    3. **Obtener nombres de usuario mediante la API de Spotify:**
    - Para cada `user_id`, se utiliza el método `sp.user(user)["display_name"]` para obtener el nombre de usuario.
    - Si ocurre un error (por ejemplo, un usuario no está disponible), se muestra un mensaje indicando que no se pudo obtener el usuario.

    4. **Construir el DataFrame:**
    - Crea un DataFrame con las columnas 'brand', 'username', y 'user_id' a partir de los datos recopilados.

    Notas:
    ------
    - **Selección del HTML:** Asegúrate de que la clase CSS utilizada para encontrar los bloques de seguidores 
    (`Box__BoxComponent-sc-y4nds-0 ... Card`) sigue siendo válida, ya que puede cambiar con el tiempo.
    - **Llamadas a la API de Spotify:** La extracción de nombres de usuario depende del límite de llamadas de la API.
    Asegúrate de respetar las restricciones de uso para evitar bloqueos.

    Ejemplo de uso:
    ---------------
    ```python
    soup = obtener_html_followers("usuario123")
    df_followers = extraer_ids_usuario(sp, "marca_ejemplo", soup)
    print(df_followers.head())
    """
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
    """
    Obtiene todas las playlists públicas de un usuario de Spotify.

    Parámetros:
    -----------
    sp : spotipy.Spotify
        Objeto autenticado de la API de Spotify, utilizado para realizar solicitudes de datos de usuario.

    user_id : str
        Identificador único del usuario de Spotify cuyas playlists se desean obtener.

    Retorna:
    --------
    dictio : dict
        Un diccionario donde las claves son los nombres de las playlists y los valores son los IDs de las playlists.

    O:
    ---
    str
        Retorna "No playlists" si el usuario no tiene playlists públicas disponibles.

    Proceso:
    --------
    1. **Solicitar playlists del usuario:**
    - Utiliza el método `sp.user_playlists(user_id)` para obtener las playlists públicas del usuario.

    2. **Manejar usuarios sin playlists:**
    - Si el campo `items` en la respuesta está vacío, retorna "No playlists".

    3. **Iterar y manejar paginación:**
    - Recorre las playlists disponibles en la respuesta.
    - Agrega el nombre (`name`) y el ID (`id`) de cada playlist al diccionario `dictio`.
    - Si existen más páginas de resultados (`next` no es `None`), realiza la siguiente solicitud utilizando `sp.next(playlists)`.

    4. **Finalizar:**
    - Cuando no queden más páginas de playlists, retorna el diccionario con los datos.

    Notas:
    ------
    - **Playlists públicas:** Este método solo accede a playlists públicas del usuario.
    - **Manejo de paginación:** La API de Spotify devuelve las playlists en páginas (paginación), por lo que es necesario iterar sobre todas las páginas para obtener todos los resultados.

    Ejemplo de uso:
    ---------------
    ```python
    playlists_dict = obtener_playlists(sp, "usuario123")
    print(playlists_dict)
    """
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

# def request_segura(url, token):
#     """
#     Verifica si la API de Spotify está disponible.
#     Si devuelve 200, devuelve True.
#     Si devuelve 429, espera el tiempo necesario.
#     """
#     while True:
#         response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
#         if response.status_code == 200:
#             return True
#         elif response.status_code == 429:
#             retry_after = int(response.headers.get("Retry-After", 1))
#             print(f"Error 429: Rate limit alcanzado. Esperando {retry_after} segundos...")
#             sleep(retry_after)
#         else:
#             print(f"Error {response.status_code}. Verifica la solicitud.")
#             return False  # No se pudo procesar

def obtener_artistas(token, lista_ids_playlists):
    """
    Obtiene un diccionario con los artistas únicos de una lista de playlists en Spotify.

    Parámetros:
    -----------
    token : str
        Token de acceso válido para la API de Spotify.

    lista_ids_playlists : list[str]
        Lista de IDs de playlists de Spotify de las cuales se desea extraer información de artistas.

    Retorna:
    --------
    dictio_artistas : dict
        Un diccionario donde las claves son los IDs de los artistas y los valores son sus nombres.

    Proceso:
    --------
    1. **Inicializar variables:**
    - `dictio_artistas`: Diccionario para registrar artistas únicos.
    - `llamadas`: Contador para controlar el número de solicitudes realizadas a la API.
    - `inicio_tiempo`: Marca de tiempo para gestionar el rate limit (50 llamadas por 30 segundos).

    2. **Iterar sobre las playlists:**
    - Para cada ID de playlist en `lista_ids_playlists`:
        - Realiza solicitudes a la API para obtener las pistas y sus artistas.

    3. **Controlar el rate limit:**
    - Si se realizan más de 50 solicitudes en 30 segundos, el programa espera el tiempo necesario antes de continuar.

    4. **Procesar cada playlist:**
    - Realiza la solicitud HTTP para obtener los datos de las pistas.
    - Extrae los nombres e IDs de los artistas asociados a cada pista y los registra en `dictio_artistas`.
    - Maneja la paginación en la API para obtener todos los resultados si hay múltiples páginas.

    5. **Manejo de errores:**
    - `200`: Procesa la respuesta correctamente.
    - `429`: Espera el tiempo especificado en el encabezado `Retry-After` si se alcanza el rate limit.
    - `401`: Si el token es inválido o ha expirado, lo renueva automáticamente.
    - Otros códigos: Informa del error y pasa a la siguiente playlist.

    6. **Finalizar:**
    - Una vez procesadas todas las playlists, retorna el diccionario de artistas.

    Notas:
    ------
    - **Rate limit:** Spotify permite un máximo de 50 solicitudes por cada 30 segundos. El código maneja este límite automáticamente.
    - **Token:** Asegúrate de proporcionar un token válido. Si se renueva automáticamente, la función llama a `request_token()`.
    - **Datos adicionales:** Este método solo considera pistas y no incluye otro contenido de las playlists.

    Ejemplo de uso:
    ---------------
    ```python
    token = request_token()
    playlists = ["playlist_id_1", "playlist_id_2"]
    artistas = obtener_artistas(token, playlists)
    print(artistas)
    """
    dictio_artistas = {}  # Para mantener un registro de artistas únicos
    llamadas = 0  # Contador de llamadas a la API
    inicio_tiempo = time()  # Tiempo de inicio para controlar el rate limit
    lista_ids_playlists = list(lista_ids_playlists)
    for playlist_id in lista_ids_playlists:
        while True:  # Loop para manejar errores y reintentos
            # Controlar el rate limit
            if llamadas >= 50:
                tiempo_transcurrido = time() - inicio_tiempo
                if tiempo_transcurrido < 31:
                    sleep_time = 30 - tiempo_transcurrido
                    print(f"Rate limit alcanzado. Durmiendo por {sleep_time:.2f} segundos...")
                    sleep(sleep_time)
                llamadas = 0
                inicio_tiempo = time()

            # Realizar la solicitud
            url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields=items.track(artists.name,artists.id),next&limit=50&additional_types=track'
            response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
            llamadas += 1

            # Manejo de respuestas
            if response.status_code == 200:
                canciones = response.json()
                while canciones:
                    for cancion in canciones["items"]:
                        track = cancion.get("track")
                        if track and "artists" in track:
                            for artist in track["artists"]:
                                if artist["id"] not in dictio_artistas:
                                    dictio_artistas[artist["id"]] = artist["name"]
                    # Procesar la siguiente página
                    if canciones["next"]:
                        response = requests.get(canciones["next"], headers={"Authorization": f"Bearer {token}"})
                        llamadas += 1
                        if response.status_code == 200:
                            canciones = response.json()
                        elif response.status_code == 429:
                            retry_after = int(response.headers.get("Retry-After", 1))
                            print(f"Rate limit alcanzado. Esperando {retry_after} segundos...")
                            sleep(retry_after)
                            continue
                        else:
                            print(f"Error al procesar la siguiente página. Código: {response.status_code}")
                            canciones = None
                    else:
                        canciones = None
                break  # Salir del loop para esta playlist
            elif response.status_code == 429:  # Rate limit alcanzado
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f"Rate limit alcanzado. Esperando {retry_after} segundos...")
                sleep(retry_after)
            elif response.status_code == 401:  # Token expirado o inválido
                print("Token expirado o inválido. Renovando token...")
                token = request_token(silent=True)
            else:  # Otros errores
                print(f"Error al procesar la playlist {playlist_id}. Código: {response.status_code}")
                break

    return dictio_artistas

def obtener_urls(dictio_artistas_unicos):
    """
    Genera una lista de URLs para obtener información de artistas desde la API de Spotify.

    Parámetros:
    -----------
    dictio_artistas_unicos : dict
        Un diccionario que contiene artistas únicos, donde las claves son los IDs de los artistas.

    Retorna:
    --------
    lista_urls : list[str]
        Una lista de URLs que se pueden usar para consultar información de artistas en lotes de hasta 50 artistas por solicitud.

    Proceso:
    --------
    1. **Obtener los IDs de artistas:**
    - Convierte las claves del diccionario de artistas únicos (`dictio_artistas_unicos[0].keys()`) en una lista.

    2. **Dividir los IDs en lotes de 50:**
    - La API de Spotify permite un máximo de 50 IDs por solicitud. 
    - Divide la lista de IDs en fragmentos de 50 utilizando rangos con saltos.

    3. **Generar URLs para cada lote:**
    - Para cada fragmento de 50 IDs, crea una URL con el formato:
        `https://api.spotify.com/v1/artists?ids=ID1,ID2,...,ID50`
    - Agrega la URL generada a `lista_urls`.

    4. **Retornar las URLs:**
    - Devuelve la lista de URLs generadas.

    Notas:
    ------
    - **Tamaño del lote:** El límite de 50 IDs por solicitud es impuesto por la API de Spotify.
    - **Progreso:** La barra de progreso de `tqdm` ayuda a visualizar el avance en la generación de URLs.

    Ejemplo de uso:
    ---------------
    ```python
    dictio_artistas_unicos = [{"artist_id_1": "Artist 1", "artist_id_2": "Artist 2", ...}]
    urls = obtener_urls(dictio_artistas_unicos)
    print(urls)
    """
    lista_urls = []
    ids_artistas = list(dictio_artistas_unicos[0].keys())
    
    # Dividir en fragmentos de 50
    for dividir in tqdm(range(0, len(ids_artistas), 50),desc="Generando Urls"):
        chunk = ids_artistas[dividir:dividir + 50]

        url = f"https://api.spotify.com/v1/artists?ids={','.join(chunk)}"
        lista_urls.append(url)

    return lista_urls

def obtener_generos(token, dictio_artistas_unicos):
    """
    Obtiene los géneros musicales asociados a un conjunto de artistas utilizando la API de Spotify.

    Parámetros:
    -----------
    token : str
        Token de acceso válido para interactuar con la API de Spotify.

    dictio_artistas_unicos : dict
        Diccionario con artistas únicos, donde las claves son los IDs de los artistas.

    Retorna:
    --------
    dictio_generos : dict
        Diccionario donde las claves son los nombres de los géneros y los valores son el número de ocurrencias de cada género.

    Proceso:
    --------
    1. **Generar URLs para la API:**
    - Llama a la función `obtener_urls(dictio_artistas_unicos)` para dividir los IDs de artistas en lotes de 50 y generar las URLs correspondientes.

    2. **Iterar sobre las URLs:**
    - Realiza una solicitud HTTP para cada URL generada.
    - Procesa los datos de los artistas devueltos por la API, extrayendo sus géneros y acumulando el conteo en `dictio_generos`.

    3. **Controlar el rate limit de Spotify:**
    - La API permite un máximo de 50 solicitudes cada 30 segundos.
    - Si se alcanza el límite, calcula cuánto tiempo esperar antes de continuar con las solicitudes.

    4. **Manejo de errores:**
    - `200`: Procesa la respuesta y extrae los géneros.
    - `429`: Espera el tiempo indicado por el encabezado `Retry-After` antes de continuar.
    - `401`: Notifica que el token ha expirado o es inválido, y termina el proceso.
    - Otros códigos: Muestra un mensaje de error y continúa con la siguiente URL.

    5. **Retornar los géneros:**
    - Devuelve un diccionario con los géneros y su número de apariciones.

    Notas:
    ------
    - **Rate limit:** Spotify impone un límite de 50 solicitudes cada 30 segundos. Este código maneja automáticamente ese límite.
    - **Reintentos:** Maneja errores temporales como `429` (Rate Limit) con reintentos automáticos después de esperar.
    - **Token:** Asegúrate de proporcionar un token válido. Si el token expira, se requiere renovar manualmente.
    - **Estructura de géneros:** Este método agrupa y cuenta los géneros musicales asociados a los artistas proporcionados.

    Ejemplo de uso:
    ---------------
    ```python
    token = request_token()
    dictio_artistas_unicos = [{"artist_id_1": "Artist 1", "artist_id_2": "Artist 2", ...}]
    generos = obtener_generos(token, dictio_artistas_unicos)
    print(generos)
    """
    lista_urls = obtener_urls(dictio_artistas_unicos)
    dictio_generos = {}  # Diccionario para almacenar géneros y su conteo
    llamadas = 0  # Contador de llamadas a la API
    inicio_tiempo = time()  # Tiempo inicial para manejar el rate limit

    for url in tqdm(lista_urls,desc="Realizando Petición a Spotify"):
        while True:  # Loop para manejar reintentos en caso de errores
            # Controlar el rate limit
            if llamadas >= 50:
                tiempo_transcurrido = time() - inicio_tiempo
                if tiempo_transcurrido < 30:
                    sleep_time = 30 - tiempo_transcurrido
                    print(f"Rate limit alcanzado. Esperando {sleep_time:.2f} segundos...")
                    sleep(sleep_time)
                llamadas = 0
                inicio_tiempo = time()

            # Realizar la petición
            response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
            llamadas += 1

            if response.status_code == 200:
                # Procesar la respuesta exitosa
                artistas = response.json()
                for artista in artistas["artists"]:
                    if artista and artista.get("genres"):
                        for genero in artista["genres"]:
                            dictio_generos[genero] = dictio_generos.get(genero, 0) + 1
                break  # Salir del loop una vez que se procesa la URL
            elif response.status_code == 429:  # Manejar Rate Limit
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f"Rate limit alcanzado. Esperando {retry_after} segundos...")
                sleep(retry_after)
                continue  # Reintentar después de la espera
            elif response.status_code == 401:  # Manejar token expirado
                print("Token expirado o inválido. Por favor, renueva tu token.")
                return None  # Salir y notificar que el token no es válido
            else:  # Otros errores
                print(f"Error al procesar la URL: {response.status_code} - {response.text}")
                break  # Salir del loop en caso de error no recuperable

    return dictio_generos

