#######################################################################################
##            Barra de progreso y manipulación de datos                           ##
#######################################################################################
# Barra de progreso para seguir el avance de iteraciones o procesos largos
from tqdm import tqdm  

#######################################################################################
##            Manejo de datos tabulares y estructuras                             ##
#######################################################################################
# Para manipulación y análisis de datos tabulares (DataFrames)
import pandas as pd  
# Para interactuar con el sistema operativo (rutas, variables de entorno, etc.)
import os  
# Para convertir cadenas en estructuras de datos Python
import ast  
# Para trabajar con datos en formato JSON
import json  

#######################################################################################
##            Modificar el sistema de rutas                                          ##
#######################################################################################
# Agrega el directorio padre ("../") al sistema de rutas de búsqueda de módulos, permitiendo importar módulos desde ahí
import sys
sys.path.append("../")  

#######################################################################################
##            Funciones personalizadas para Spotify                                  ##
#######################################################################################
# Funciones para interactuar con la API de Spotify
import src.soporte_spotify as api  

#######################################################################################
##            Fin de los Imports                                                     ##
#######################################################################################


def str_a_diccionario(brand_df, columna):
    """
    Convierte los valores de una columna de un DataFrame de formato string a diccionarios.

    Parámetros:
    ----------
    brand_df : pandas.DataFrame
        DataFrame que contiene la columna con valores en formato string representando diccionarios.
    
    columna : str
        Nombre de la columna cuyos valores serán convertidos de string a diccionario.

    Retorna:
    -------
    pandas.Series
        Serie con los valores de la columna convertidos en diccionarios.
    """

    return brand_df[str(columna)].apply(ast.literal_eval)

def str_a_lista(brand_df, columna):
    """
    Convierte los valores de una columna de un DataFrame de formato string a listas.

    Parámetros:
    ----------
    brand_df : pandas.DataFrame
        DataFrame que contiene la columna con valores en formato string representando listas.
    
    columna : str
        Nombre de la columna cuyos valores serán convertidos de string a lista.

    Retorna:
    -------
    pandas.Series
        Serie con los valores de la columna convertidos en listas. 
        Si el valor es NaN, se devuelve una lista vacía.
    """

    return brand_df[str(columna)].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])

def obtener_id_artistas(brand_df,output_file = "../datos/01 Spotify/00_GuardadoTemporal.csv"):
    """
    Extrae los identificadores de artistas desde las playlists de los usuarios en un DataFrame.

    Parámetros:
    ----------
    brand_df : pandas.DataFrame
        DataFrame que contiene la información de las playlists de los seguidores de una marca.
    
    output_file : str, opcional (por defecto "../datos/01 Spotify/00_GuardadoTemporal.csv")
        Ruta donde se guarda temporalmente el progreso en un archivo CSV.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con una nueva columna 'artistas' que contiene los artistas extraídos de las playlists.
    
    Descripción:
    -----------
    - Convierte la columna 'playlists' de string a diccionario.
    - Extrae los identificadores de playlists y los limita a un máximo de 10 por usuario.
    - Carga el progreso si existe un archivo previo, evitando procesar datos ya obtenidos.
    - Obtiene los artistas de cada playlist usando la API de Spotify.
    - Guarda el progreso en el archivo CSV después de cada iteración.
    """

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
    """
    Obtiene un diccionario de artistas únicos a partir de la columna 'artistas' de un DataFrame.

    Parámetros:
    ----------
    brand_df : pandas.DataFrame
        DataFrame que contiene una columna 'artistas', donde cada fila es un diccionario con identificadores de artistas como claves y nombres de artistas como valores.

    Retorna:
    -------
    dict
        Diccionario donde las claves son los identificadores únicos de artistas y los valores son los nombres de los artistas.

    Descripción:
    -----------
    - Itera sobre la columna 'artistas' del DataFrame.
    - Extrae los identificadores y nombres de los artistas, asegurando que no haya duplicados.
    - Elimina la clave 'None' si está presente en el diccionario resultante.
    """
    artistas_unicos = {}
    for dictio in brand_df["artistas"]:
        for id_artista, artista in dictio.items():
            if id_artista not in artistas_unicos:
                artistas_unicos[id_artista] = artista
    # Eliminar la Key "None"
    del artistas_unicos["None"]
    
    return artistas_unicos

def obtener_ranking_artistas(brand_df):
    """
    Genera un ranking de artistas basado en su frecuencia de aparición en la columna 'artistas' de un DataFrame.

    Parámetros:
    ----------
    brand_df : pandas.DataFrame
        DataFrame que contiene una columna 'artistas', donde cada fila es un diccionario con identificadores de artistas como claves y nombres de artistas como valores.

    Retorna:
    -------
    dict
        Diccionario donde las claves son los nombres de los artistas y los valores representan la cantidad de veces que aparecen en la columna 'artistas'.

    Descripción:
    -----------
    - Itera sobre la columna 'artistas' del DataFrame.
    - Cuenta cuántas veces aparece cada artista en todas las playlists de los seguidores de la marca.
    - Omite valores nulos (None) para evitar errores en el conteo.
    """

    conteo_artistas = {}
    for dictio in brand_df["artistas"]:
        for artista in dictio.values():
            if artista != None:
                conteo_artistas[artista] = conteo_artistas.get(artista,0) + 1
    
    return conteo_artistas

def tabla_resumen(brand_df, followers_path, resumen_path):
    """
    Genera un resumen de datos sobre los seguidores de una marca, incluyendo el número de seguidores,
    los artistas únicos y un ranking de los más escuchados.

    Parámetros:
    ----------
    brand_df : pandas.DataFrame
        DataFrame que contiene información sobre los seguidores de una marca y sus hábitos musicales.
    
    followers_path : str
        Ruta donde se guardará el DataFrame actualizado con los datos procesados de los seguidores.
    
    resumen_path : str
        Ruta donde se guardará el DataFrame resumen con los artistas únicos y el ranking de artistas.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame resumen con la marca analizada, número total de seguidores, artistas únicos y ranking de artistas.

    Descripción:
    -----------
    - Filtra usuarios cuyas playlists no contienen artistas.
    - Convierte columnas de tipo string a listas o diccionarios según corresponda.
    - Guarda el DataFrame actualizado con los seguidores en un CSV.
    - Obtiene los artistas únicos y el ranking de artistas más escuchados.
    - Crea un DataFrame resumen con la información relevante.
    - Convierte las columnas del resumen a listas/diccionarios nuevamente para su correcta interpretación.
    - Guarda el DataFrame resumen en un archivo CSV.
    """

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
    """
    Obtiene y almacena los géneros musicales de los artistas únicos asociados a una marca.

    Parámetros:
    ----------
    brand_df : pandas.DataFrame
        DataFrame que contiene información de los artistas únicos y su ranking para una marca específica.
    
    resumen_path : str
        Ruta del archivo CSV donde se encuentra y se actualizará el resumen de la marca.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame actualizado con la lista de géneros musicales y su ranking basado en frecuencia.

    Descripción:
    -----------
    - Carga el DataFrame desde el archivo CSV de resumen.
    - Convierte las columnas `unique_artists` y `artist_ranking` de string a diccionario y lista respectivamente.
    - Solicita un token de autenticación para la API de Spotify.
    - Obtiene los géneros musicales de los artistas únicos.
    - Añade la lista de géneros y su ranking basado en frecuencia al DataFrame.
    - Guarda el DataFrame actualizado en el archivo CSV de resumen.
    """

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