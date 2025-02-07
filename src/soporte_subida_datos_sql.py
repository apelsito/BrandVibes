#######################################################################################
##            Modificar el sistema de rutas para permitir importar módulos desde el directorio padre ##
#######################################################################################
# Modificar el sistema de rutas para permitir importar módulos desde el directorio padre
import sys 
sys.path.append("../")

#######################################################################################
##            Importación de módulos personalizados para manejo de bases de datos SQL ##
#######################################################################################
# Importar el módulo personalizado para manejo de bases de datos SQL
import src.soporte_sql as sql

#######################################################################################
##            Importación de bibliotecas para manipulación y análisis de datos         ##
#######################################################################################
# Importar la biblioteca pandas para manipulación y análisis de datos tabulares
import pandas as pd

# Importar la biblioteca JSON para trabajar con datos en formato JSON
import json

# Importar la biblioteca AST para convertir cadenas en estructuras de datos Python
import ast

#######################################################################################
##            Fin de los Imports                                                     ##
#######################################################################################


def obtener_tabla_followers(followers_df, brand_id = 0):
    """
    Genera una tabla de seguidores con la marca asociada para su posterior almacenamiento en la base de datos.

    Parámetros:
    ----------
    followers_df : pandas.DataFrame
        DataFrame que contiene la información de los seguidores, incluyendo `username` y `user_id`.

    brand_id : int, opcional (por defecto 0)
        Identificador único de la marca a la que pertenecen los seguidores.
        Si el `brand_id` no es válido, se muestra un mensaje con los IDs de marcas disponibles.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con las columnas `username`, `user_id` y `brand` si el `brand_id` es válido.

    Descripción:
    -----------
    - Consulta la base de datos para obtener la lista de marcas y sus IDs.
    - Verifica si el `brand_id` ingresado existe en la base de datos.
    - Si el `brand_id` no es válido, muestra un mensaje con los IDs de las marcas disponibles.
    - Si el `brand_id` es válido, asigna la marca a los seguidores y devuelve el DataFrame resultante.
    """

    conexion = sql.conectar_bd()
    query = ''' SELECT * FROM brands'''
    df = sql.consulta_sql(conexion, query)
    df = df[["id","name"]]
    check = df["id"].tolist()
    if brand_id not in check:
        print("El id de la marca no existe")
        print("Los ids de las marcas son:")
        return display(df)
    
    followers_df["brand"] = brand_id
    followers_df = followers_df[["username","user_id","brand"]]
    return followers_df

def subir_followers(followers_df):
    """
    Inserta los datos de seguidores en la base de datos en la tabla `followers`.

    Parámetros:
    ----------
    followers_df : pandas.DataFrame
        DataFrame que contiene la información de los seguidores con las columnas `username`, `user_id` y `brand_id`.

    Retorna:
    -------
    None

    Descripción:
    -----------
    - Establece una conexión con la base de datos mediante `sql.conectar_bd()`.
    - Prepara la consulta SQL para insertar los datos en la tabla `followers`.
    - Convierte el DataFrame en una tupla para su inserción masiva en la base de datos.
    - Inserta los datos en la base de datos usando `sql.insertar_muchos_datos()`.
    """

    conexion = sql.conectar_bd()
    query = '''INSERT INTO followers(username,user_id,brand_id) VALUES (%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(followers_df))

def obtener_tabla_playlists(playlists_df, brand_id = 0):
    """
    Genera una tabla de playlists asociadas a los seguidores de una marca para su posterior almacenamiento en la base de datos.

    Parámetros:
    ----------
    playlists_df : pandas.DataFrame
        DataFrame que contiene la información de las playlists, incluyendo `user_id` y `playlists`.

    brand_id : int, opcional (por defecto 0)
        Identificador único de la marca a la que pertenecen los seguidores y sus playlists.
        Si el `brand_id` no es válido, se muestra un mensaje con los IDs de marcas disponibles.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con las columnas `playlist_name`, `playlist_id` y `id` (identificador del seguidor en la base de datos)
        si el `brand_id` es válido.

    Descripción:
    -----------
    - Consulta la base de datos para obtener la lista de marcas y sus IDs.
    - Verifica si el `brand_id` ingresado existe en la base de datos.
    - Si el `brand_id` no es válido, muestra un mensaje con los IDs de las marcas disponibles.
    - Obtiene la lista de seguidores de la marca desde la base de datos.
    - Realiza un merge entre los seguidores y sus playlists.
    - Convierte la información de las playlists de string a diccionario (`ast.literal_eval`).
    - Genera un DataFrame con cada playlist, asignándola a su respectivo seguidor.
    - Devuelve un DataFrame con las columnas `playlist_name`, `playlist_id` y `id`.
    """

    conexion = sql.conectar_bd()
    query = ''' SELECT * FROM brands'''
    df = sql.consulta_sql(conexion, query)
    df = df[["id","name"]]
    check = df["id"].tolist()
    if brand_id not in check:
        print("El id de la marca no existe")
        print("Los ids de las marcas son:")
        return display(df)
    
    # Obtenemos el id de los usuarios desde la base de datos
    conexion = sql.conectar_bd()
    query = '''SELECT * FROM followers'''
    df_users = sql.consulta_sql(conexion,query)
    df_users = df_users[["id","user_id","username"]]
    df_users.sample()
    
    # Realizamos merge y convertimos a diccionario las playlists
    unir = pd.merge(left=df_users,right=playlists_df,on="user_id")
    playlists = unir[["id","playlists"]]
    playlists["playlists"] = playlists["playlists"].apply(ast.literal_eval)

    # Generamos la tabla de playlists
    id_list = []
    playlist_names = []
    playlist_ids = []

    for _, fila in playlists.iterrows():
        user_id = fila["id"]
        playlist = fila["playlists"]

        for playlist_name, playlist_id in playlist.items():
            id_list.append(user_id)
            playlist_names.append(playlist_name)
            playlist_ids.append(playlist_id)

    playlists =  pd.DataFrame({
        "id" : id_list,
        "playlist_name" : playlist_names,
        "playlist_id" : playlist_ids
    })
    playlists = playlists[["playlist_name","playlist_id","id"]]
    return playlists

def subir_playlists(playlists_df):
    """
    Inserta los datos de playlists en la base de datos en la tabla `playlists`.

    Parámetros:
    ----------
    playlists_df : pandas.DataFrame
        DataFrame que contiene la información de las playlists con las columnas `playlist_name`, `playlist_id` y `follower_id`.

    Retorna:
    -------
    None

    Descripción:
    -----------
    - Establece una conexión con la base de datos mediante `sql.conectar_bd()`.
    - Prepara la consulta SQL para insertar los datos en la tabla `playlists`.
    - Convierte el DataFrame en una tupla para su inserción masiva en la base de datos.
    - Inserta los datos en la base de datos usando `sql.insertar_muchos_datos()`.
    """

    conexion = sql.conectar_bd()
    query = '''INSERT INTO playlists(playlist_name,playlist_id,follower_id) VALUES (%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(playlists_df))

def obtener_tabla_reduced_playlists(playlists_df, brand_id = 0):
    """
    Genera una tabla de playlists reducidas asociadas a los seguidores de una marca para su posterior almacenamiento en la base de datos.

    Parámetros:
    ----------
    playlists_df : pandas.DataFrame
        DataFrame que contiene la información de las playlists, incluyendo `user_id` y `playlists`.

    brand_id : int, opcional (por defecto 0)
        Identificador único de la marca a la que pertenecen los seguidores y sus playlists.
        Si el `brand_id` no es válido, se muestra un mensaje con los IDs de marcas disponibles.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con las columnas `playlist_name`, `playlist_id` y `id` (identificador del seguidor en la base de datos)
        si el `brand_id` es válido.

    Descripción:
    -----------
    - Consulta la base de datos para obtener la lista de marcas y sus IDs.
    - Verifica si el `brand_id` ingresado existe en la base de datos.
    - Si el `brand_id` no es válido, muestra un mensaje con los IDs de las marcas disponibles.
    - Convierte las cadenas de texto de la columna `playlists` a diccionarios reales (`ast.literal_eval`).
    - Reduce las playlists por usuario a un máximo de 10 elementos.
    - Obtiene la lista de seguidores de la marca desde la base de datos.
    - Realiza un merge entre los seguidores y sus playlists reducidas.
    - Genera un DataFrame con cada playlist reducida, asignándola a su respectivo seguidor.
    - Devuelve un DataFrame con las columnas `playlist_name`, `playlist_id` y `id`.
    """

    conexion = sql.conectar_bd()
    query = ''' SELECT * FROM brands'''
    df = sql.consulta_sql(conexion, query)
    df = df[["id","name"]]
    check = df["id"].tolist()
    if brand_id not in check:
        print("El id de la marca no existe")
        print("Los ids de las marcas son:")
        return display(df)

    # Convertir las cadenas de texto de la columna "playlists" a diccionarios reales
    if type(playlists_df["playlists"][0]) == str:
        playlists_df["playlists"] = playlists_df["playlists"].apply(ast.literal_eval)

    
    # Seleccionar columnas clave
    playlists_df = playlists_df[["brand", "username", "user_id", "playlists"]]

    # Lista para almacenar los diccionarios reducidos
    reduced_playlists_list = []

    # Iterar sobre cada diccionario en la columna "playlists"
    for dict_item in playlists_df["playlists"]:
        reduced_dict = {}  # Diccionario reducido
        count = 0  # Contador para elementos procesados

        # Iterar sobre los elementos del diccionario y limitar a 10
        for key, value in dict_item.items():
            if count < 10:
                reduced_dict[key] = value
                count += 1
            else:
                break
        
        # Agregar el diccionario reducido a la lista
        reduced_playlists_list.append(reduced_dict)

    # Crear la nueva columna "reduced_playlists" en el DataFrame
    playlists_df["reduced_playlists"] = reduced_playlists_list
    playlists_df = playlists_df[["user_id","reduced_playlists"]]

    # Obtenemos el id de los usuarios haciendo una consulta a la bd
    conexion = sql.conectar_bd()
    query = '''SELECT * FROM followers'''
    df_users = sql.consulta_sql(conexion,query)
    df_users = df_users[["id","user_id","username"]]

    # Realizamos merge y convertimos a diccionario "playlists"
    unir = pd.merge(left=df_users,right=playlists_df,on="user_id")
    playlists = unir[["id","reduced_playlists"]]

    id_list = []
    playlist_names = []
    playlist_ids = []

    for _ , fila in playlists.iterrows():
        user_id = fila["id"]
        playlist = fila["reduced_playlists"]

        for playlist_name, playlist_id in playlist.items():
            id_list.append(user_id)
            playlist_names.append(playlist_name)
            playlist_ids.append(playlist_id)

    playlists =  pd.DataFrame({
        "id" : id_list,
        "playlist_name" : playlist_names,
        "playlist_id" : playlist_ids
    })
    playlists = playlists[["playlist_name","playlist_id","id"]]
    return playlists

def subir_reduced_playlists(playlists):
    """
    Inserta los datos de playlists reducidas en la base de datos en la tabla `reduced_playlists`.

    Parámetros:
    ----------
    playlists : pandas.DataFrame
        DataFrame que contiene la información de las playlists reducidas con las columnas `playlist_name`, `playlist_id` y `follower_id`.

    Retorna:
    -------
    None

    Descripción:
    -----------
    - Establece una conexión con la base de datos mediante `sql.conectar_bd()`.
    - Prepara la consulta SQL para insertar los datos en la tabla `reduced_playlists`.
    - Convierte el DataFrame en una tupla para su inserción masiva en la base de datos.
    - Inserta los datos en la base de datos usando `sql.insertar_muchos_datos()`.
    """

    conexion = sql.conectar_bd()
    query = '''INSERT INTO reduced_playlists(playlist_name,playlist_id,follower_id) VALUES (%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(playlists))

def obtener_tabla_artistas(artistas_df,brand_id = 0, ruta_csv = "../datos/02 Base de Datos/tempsave.csv"):
    """
    Genera un DataFrame con la información de artistas asociados a una marca y guarda un archivo CSV temporal.

    Parámetros:
    -----------
    artistas_df : pandas.DataFrame
        DataFrame que contiene la información de los artistas. Debe incluir las columnas 
        'brand' y 'unique_artists', donde 'unique_artists' contiene diccionarios con 
        los identificadores y nombres de los artistas.

    brand_id : int, opcional
        El identificador de la marca a la que están asociados los artistas. 
        El valor predeterminado es 0.

    ruta_csv : str, opcional
        Ruta donde se guardará el archivo CSV temporal. El valor predeterminado 
        es "../datos/02 Base de Datos/tempsave.csv".

    Retorna:
    --------
    artistas : pandas.DataFrame
        DataFrame con las columnas:
        - 'artist_name': Nombre del artista.
        - 'artist_id': Identificador único del artista.
        - 'brand_id': Identificador de la marca asociada.

    Proceso:
    --------
    1. Comprueba si el `brand_id` existe en la base de datos. Si no existe, retorna un display 
    con los IDs y nombres de marcas disponibles.
    2. Convierte los datos de 'unique_artists' de cadenas a diccionarios.
    3. Descompone los diccionarios en un formato plano con columnas para el nombre del artista,
    el identificador del artista y el ID de la marca.
    4. Crea un DataFrame con la información descompuesta.
    5. Guarda el DataFrame generado en un archivo CSV temporal.
    6. Elimina los valores nulos del DataFrame.
    7. Muestra un mensaje para revisar la tabla antes de subirla y sugiere usar la función 
    `subir_artistas()` para insertar los datos en la base de datos.

    Notas:
    ------
    - Si el `brand_id` no existe, se imprime un mensaje con los IDs y nombres de marcas disponibles.
    - La función utiliza métodos auxiliares de un módulo `sql` para conectar y realizar consultas en la base de datos.
    """

    conexion = sql.conectar_bd()
    query = ''' SELECT * FROM brands'''
    df = sql.consulta_sql(conexion, query)
    df = df[["id","name"]]
    check = df["id"].tolist()
    if brand_id not in check:
        print("El id de la marca no existe")
        print("Los ids de las marcas son:")
        return display(df)

    artistas = artistas_df[["brand","unique_artists"]]
    # Convertimos unique_artists a diccionario
    artistas["unique_artists"] = artistas["unique_artists"].apply(ast.literal_eval)
    lista_brand = []
    nombres_artistas = []
    ids_artistas = []

    for dictio in artistas["unique_artists"]:
        for artist_id, artist_name in dictio.items():
            lista_brand.append(brand_id) # El id de zara en la bd es 1
            nombres_artistas.append(artist_name)
            ids_artistas.append(artist_id)
    artistas = pd.DataFrame({
        "artist_name" : nombres_artistas,
        "artist_id" : ids_artistas,
        "brand_id" : lista_brand
    })
    # Guardar en CSV el archivo
    artistas.to_csv(ruta_csv,index=False)
    # Eliminar Nulos
    artistas.dropna(inplace=True)
    print("Revisa la tabla antes de subirla!")
    print("Usa la funcion subir_artistas(artistas) para subir los datos")
    return artistas

def subir_artistas(artistas_df):
    """
    Sube los datos de artistas a la base de datos.

    Parámetros:
    -----------
    artistas_df : pandas.DataFrame
        DataFrame que contiene la información de los artistas. Debe incluir las columnas:
        - 'artist_name': Nombre del artista.
        - 'artist_id': Identificador único del artista.
        - 'brand_id': Identificador de la marca asociada.

    Proceso:
    --------
    1. Establece una conexión con la base de datos utilizando la función `sql.conectar_bd()`.
    2. Define la consulta SQL para insertar múltiples registros en la tabla `artists`.
    3. Convierte el DataFrame en una tupla de valores utilizando `sql.generar_tupla()`.
    4. Inserta los datos en la base de datos utilizando `sql.insertar_muchos_datos()`.

    Notas:
    ------
    - Asegúrate de que el DataFrame `artistas_df` no contiene valores nulos antes de ejecutar esta función.
    - La tabla `artists` en la base de datos debe estar configurada con las columnas adecuadas para que la inserción sea exitosa.
    """

    conexion = sql.conectar_bd()
    query = '''INSERT INTO artists(artist_name,artist_id,brand_id) VALUES (%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(artistas_df))

def obtener_ranking_artistas(ranking_df,brand_id = 0, ruta_csv = "../datos/02 Base de Datos/00_tempsaves/tempsave_ranking.csv"):
    """
    Genera un DataFrame con el ranking de artistas asociados a una marca y guarda un archivo CSV temporal.

    Parámetros:
    -----------
    ranking_df : pandas.DataFrame
        DataFrame que contiene la información del ranking de artistas. Debe incluir las columnas:
        - 'brand': Nombre de la marca asociada.
        - 'artist_ranking': Listas de tuplas donde cada tupla contiene el nombre del artista y 
        su número de apariciones.

    brand_id : int, opcional
        El identificador de la marca a la que está asociado el ranking de artistas.
        El valor predeterminado es 0.

    ruta_csv : str, opcional
        Ruta donde se guardará el archivo CSV temporal. El valor predeterminado 
        es "../datos/02 Base de Datos/tempsave_ranking.csv".

    Retorna:
    --------
    ranking_art : pandas.DataFrame
        DataFrame con las columnas:
        - 'artist_name': Nombre del artista.
        - 'number_of_appearances': Número de apariciones del artista.
        - 'brand_id': Identificador de la marca asociada.

    Proceso:
    --------
    1. Comprueba si el `brand_id` existe en la base de datos. Si no existe, retorna un display 
    con los IDs y nombres de marcas disponibles.
    2. Convierte los valores de 'artist_ranking' de cadenas a listas de tuplas si no son nulos.
    3. Descompone las listas de tuplas en un formato plano con columnas para el nombre del artista,
    el número de apariciones y el ID de la marca.
    4. Crea un DataFrame con la información descompuesta.
    5. Guarda el DataFrame generado en un archivo CSV temporal.
    6. Muestra un mensaje para revisar la tabla antes de subirla y sugiere usar la función 
    `subir_ranking_artistas()` para insertar los datos en la base de datos.

    Notas:
    ------
    - Si el `brand_id` no existe, se imprime un mensaje con los IDs y nombres de marcas disponibles.
    - La función utiliza métodos auxiliares de un módulo `sql` para conectar y realizar consultas en la base de datos.
    """

    conexion = sql.conectar_bd()
    query = ''' SELECT * FROM brands'''
    df = sql.consulta_sql(conexion, query)
    df = df[["id","name"]]
    check = df["id"].tolist()
    if brand_id not in check:
        print("El id de la marca no existe")
        print("Los ids de las marcas son:")
        return display(df)

    ranking_art = ranking_df[["brand","artist_ranking"]]
    # Convertimos unique_artists a lista
    ranking_art["artist_ranking"] = ranking_art["artist_ranking"].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
    
    lista_brands = []
    lista_artistas = []
    lista_conteos = []
    for tuplas in ranking_art["artist_ranking"]:
        for artista, conteo in tuplas:
            lista_artistas.append(artista)
            lista_conteos.append(conteo)
            lista_brands.append(brand_id) # el id de la marca

    ranking_art = pd.DataFrame({
        "artist_name" : lista_artistas,
        "number_of_appearances" : lista_conteos,
        "brand_id" : lista_brands
    })
    # Guardar en CSV el archivo
    ranking_art.to_csv(ruta_csv,index=False)
    print("Revisa la tabla antes de subirla!")
    print("Usa la funcion subir_ranking_artistas(ranking_df) para subir los datos")
    return ranking_art

def subir_ranking_artistas(ranking_df):
    """
    Sube el ranking de artistas a la base de datos.

    Parámetros:
    -----------
    ranking_df : pandas.DataFrame
        DataFrame que contiene la información del ranking de artistas. Debe incluir las columnas:
        - 'artist_name': Nombre del artista.
        - 'number_of_appearances': Número de apariciones del artista.
        - 'brand_id': Identificador de la marca asociada.

    Proceso:
    --------
    1. Establece una conexión con la base de datos utilizando la función `sql.conectar_bd()`.
    2. Define la consulta SQL para insertar múltiples registros en la tabla `artists_ranking`.
    3. Convierte el DataFrame en una tupla de valores utilizando `sql.generar_tupla()`.
    4. Inserta los datos en la tabla `artists_ranking` de la base de datos utilizando 
    `sql.insertar_muchos_datos()`.

    Notas:
    ------
    - Asegúrate de que el DataFrame `ranking_df` no contiene valores nulos antes de ejecutar esta función.
    - La tabla `artists_ranking` en la base de datos debe estar configurada con las columnas 
    adecuadas para que la inserción sea exitosa.
    """

    conexion = sql.conectar_bd()
    query = '''INSERT INTO artists_ranking(artist_name,number_of_appearances,brand_id) VALUES (%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(ranking_df))

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

def mapear_main_genres(generos_df,brand_id = 0, ruta_csv = "../datos/02 Base de Datos/tempsave_check_genre.csv"):
    """
    Función 1 de 3:
    ------------
    Esta Función se ejecuta en 3 pasos por seguridad y para verificar los datos antes de subirlos a la base de datos.

    Mapea los géneros principales a partir de un ranking de géneros y devuelve un DataFrame con el mapeo como paso 1 de 3 funciones.

    Parámetros:
    -----------
    generos_df : pandas.DataFrame
        DataFrame que contiene la información del ranking de géneros. Debe incluir las columnas:
        - 'brand': Nombre de la marca asociada.
        - 'genres_ranking': Listas de tuplas donde cada tupla contiene el subgénero y su número de apariciones.

    brand_id : int, opcional
        El identificador de la marca a la que está asociado el ranking de géneros.
        El valor predeterminado es 0.

    ruta_csv : str, opcional
        Ruta donde se guardará un archivo CSV temporal si es necesario. El valor predeterminado 
        es "../datos/02 Base de Datos/tempsave_check_genre.csv".

    Retorna:
    --------
    generos : pandas.DataFrame
        DataFrame con las columnas:
        - 'subgenre_name': Nombre del subgénero.
        - 'number_of_appearances': Número de apariciones del subgénero.
        - 'brand_id': Identificador de la marca asociada.
        - 'genre': Género principal mapeado desde el subgénero.

    Proceso:
    --------
    1. Comprueba si el `brand_id` existe en la base de datos:
    - Se conecta a la base de datos y extrae la tabla `brands` con los IDs y nombres de marcas.
    - Si el `brand_id` no está presente, imprime un mensaje con los IDs disponibles y retorna un display de la tabla.

    2. Convierte los valores de 'genres_ranking' de cadenas a listas de tuplas:
    - Aplica `ast.literal_eval` a los valores no nulos para transformar las cadenas en listas de tuplas.

    3. Descompone las listas de tuplas:
    - Itera sobre las listas para descomponerlas en columnas planas:
        - 'subgenre_name': Nombre del subgénero.
        - 'number_of_appearances': Conteo del subgénero.
        - 'brand_id': Identificador de la marca.

    4. Llama a la función `mapeo_genres()`:
    - Genera un diccionario que mapea subgéneros a géneros principales desde un archivo JSON.

    5. Mapea los subgéneros a los géneros principales:
    - Asocia cada subgénero con su género principal utilizando el diccionario de mapeo.

    6. Muestra mensajes informativos:
    - Indica al usuario que revise la tabla para verificar el mapeo.
    - Recomienda rellenar el JSON si faltan géneros principales y volver a ejecutar la función.
    - Sugiere continuar con la función `obtener_main_genres()` para completar el siguiente paso.

    Notas:
    ------
    - Este es el **Paso 1 de 3** en el proceso de mapeo y subida de datos.
    - Si el `brand_id` no existe, se imprime un mensaje con los IDs y nombres de marcas disponibles.
    - El archivo JSON para el mapeo debe estar estructurado correctamente y accesible desde la ruta relativa definida en `mapeo_genres()`.

    Siguientes pasos:
    -----------------
    1. Ejecutar `mapear_main_genres()` (esta función) para generar el DataFrame con los géneros mapeados.
    2. Revisar y completar el archivo JSON si faltan géneros principales.
    3. Ejecutar `obtener_main_genres()` para procesar y subir los datos mapeados.
    """

    conexion = sql.conectar_bd()
    query = ''' SELECT * FROM brands'''
    df = sql.consulta_sql(conexion, query)
    df = df[["id","name"]]
    check = df["id"].tolist()
    if brand_id not in check:
        print("El id de la marca no existe")
        print("Los ids de las marcas son:")
        return display(df)
    
    generos = generos_df[["brand","genres_ranking"]]
    generos["genres_ranking"] = generos["genres_ranking"].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
    
    lista_brands = []
    lista_generos = []
    lista_conteos = []
    for tuplas in generos["genres_ranking"]:
        for artista, conteo in tuplas:
            lista_generos.append(artista)
            lista_conteos.append(conteo)
            lista_brands.append(brand_id) # 1 es zara en la base de datos

    generos = pd.DataFrame({
        "subgenre_name" : lista_generos,
        "number_of_appearances" : lista_conteos,
        "brand_id" : lista_brands
    })

    # LLamamos al JSON y generamos el diccionario de Mapeo de subgeneros a generos principales
    mapping_dict = mapeo_genres()
    # Mapeamos los subgeneros a los generos principales
    generos["genre"] = generos["subgenre_name"].map(mapping_dict)
    print("Revisa la tabla para asegurarte de que los generos principales esten bien mapeados")
    print("Si no rellena el json con los faltantes y vuelve a ejecutar la funcion")
    print("Después ejecuta la función obtener_main_genres(generos) para subir los datos")
    return generos

def obtener_main_genres(generos_df,brand_id = 0, ruta_csv = "../datos/02 Base de Datos/tempsave_main_genre.csv"):
    """
    Función 2 de 3:
    ------------
    Agrupa y calcula el conteo de apariciones por género principal.

    Parámetros:
    -----------
    generos_df : pandas.DataFrame
        DataFrame que contiene la información de los géneros, debe incluir las columnas:
        - 'genre': Género principal mapeado.
        - 'number_of_appearances': Número de apariciones de cada subgénero.

    brand_id : int, opcional
        Identificador de la marca asociada a los géneros.
        El valor predeterminado es 0.

    ruta_csv : str, opcional
        Ruta donde se guardará un archivo CSV con el conteo de géneros principales.
        El valor predeterminado es "../datos/02 Base de Datos/tempsave_main_genre.csv".

    Retorna:
    --------
    main_generos : pandas.DataFrame
        DataFrame con las columnas:
        - 'genre': Género principal.
        - 'number_of_appearances': Número total de apariciones de cada género principal.
        - 'brand_id': Identificador de la marca asociada.

    Proceso:
    --------
    1. Agrupa los datos por la columna 'genre' y suma los valores de 'number_of_appearances':
    - Obtiene el número total de apariciones de cada género principal.

    2. Ordena el DataFrame por la columna 'number_of_appearances' en orden descendente:
    - Los géneros principales con más apariciones aparecen primero.

    3. Resetea los índices del DataFrame para organizarlo:
    - Crea una columna ordenada con índices consecutivos.

    4. Añade una columna 'brand_id' al DataFrame:
    - Indica la marca asociada a los géneros principales.

    5. Guarda el DataFrame resultante en un archivo CSV temporal en la ruta especificada.

    6. Muestra mensajes para:
    - Indicar que el archivo se generó correctamente.
    - Recomendar revisar el archivo antes de subirlo.
    - Sugerir usar la función `subir_main_genres()` para completar el siguiente paso.

    Notas:
    ------
    - Este es el **Paso 2 de 3** en el proceso de mapeo y subida de datos.
    - La función se basa en los resultados generados por `mapear_main_genres()` en el paso anterior.
    - Asegúrate de revisar el CSV generado antes de continuar.

    Siguientes pasos:
    -----------------
    1. Ejecutar `mapear_main_genres()` para generar el DataFrame inicial con los géneros mapeados.
    2. Ejecutar esta función para calcular y guardar el conteo por género principal.
    3. Usar la función `subir_main_genres()` para insertar los datos procesados en la base de datos.
    """
    # Obtenemos el conteo de apariciones por genero principal
    main_generos = generos_df.groupby("genre")["number_of_appearances"].sum().reset_index()
    # Ordenamos por numero de apariciones
    main_generos.sort_values(by="number_of_appearances",ascending=False,inplace=True)
    main_generos.reset_index(drop=True,inplace=True)
    main_generos["brand_id"] = brand_id
    # Guardar en csv
    main_generos.to_csv(ruta_csv,index=False)
    print("Revisa la tabla antes de subirla!")
    print("Usa la funcion subir_main_genres(main_generos) para subir los datos")
    return main_generos

def subir_main_genres(main_generos_df):
    """
    Función 3 de 3:
    ------------
    Sube los datos de géneros principales a la base de datos como paso 3 de 3 funciones.

    Parámetros:
    -----------
    main_generos_df : pandas.DataFrame
        DataFrame que contiene la información de los géneros principales. Debe incluir las columnas:
        - 'genre': Nombre del género principal.
        - 'number_of_appearances': Número total de apariciones del género.
        - 'brand_id': Identificador de la marca asociada.

    Proceso:
    --------
    1. Establece una conexión con la base de datos utilizando la función `sql.conectar_bd()`.
    2. Define la consulta SQL para insertar múltiples registros en la tabla `main_genres`.
    3. Convierte el DataFrame en una tupla de valores utilizando `sql.generar_tupla()`.
    4. Inserta los datos en la tabla `main_genres` de la base de datos utilizando 
    `sql.insertar_muchos_datos()`.

    Notas:
    ------
    - Este es el **Paso 3 de 3** en el proceso de mapeo y subida de datos.
    - Asegúrate de que el DataFrame `main_generos_df` no contiene valores nulos antes de ejecutar esta función.
    - La tabla `main_genres` en la base de datos debe estar configurada con las columnas adecuadas para que la inserción sea exitosa.

    Siguientes pasos:
    -----------------
    1. Ejecutar `mapear_main_genres()` para generar el DataFrame inicial con los géneros mapeados.
    2. Ejecutar `obtener_main_genres()` para calcular y guardar el conteo por género principal.
    3. Usar esta función para insertar los datos procesados en la base de datos.
    """
    conexion = sql.conectar_bd()
    query = '''INSERT INTO main_genres(genre_name,number_of_appearances,brand_id) VALUES (%s,%s,%s)'''
    sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(main_generos_df))

def obtener_subgenres(subgeneros_df, brand_id = 0, ruta_csv = "../datos/02 Base de Datos/tempsave_subgenre.csv"):
    """
    Esta Función espera el df que obtienes de `mapear_main_genres()`:
    -----------
    Procesa y genera un DataFrame con subgéneros asociados a géneros principales y sus identificadores, como paso intermedio para subir subgéneros a la base de datos.

    Parámetros:
    -----------
    subgeneros_df : pandas.DataFrame
        DataFrame que contiene la información de los subgéneros. Debe ser el resultado de `mapear_main_genres()` 
        y contener las columnas:
        - 'subgenre_name': Nombre del subgénero.
        - 'number_of_appearances': Número de apariciones del subgénero.
        - 'genre': Nombre del género principal mapeado.
        - 'brand_id': Identificador de la marca asociada.

    brand_id : int, opcional
        Identificador de la marca asociada a los subgéneros.
        El valor predeterminado es 0.

    ruta_csv : str, opcional
        Ruta donde se guardará un archivo CSV con la información procesada de los subgéneros.
        El valor predeterminado es "../datos/02 Base de Datos/tempsave_subgenre.csv".

    Retorna:
    --------
    subgeneros : pandas.DataFrame
        DataFrame con las columnas:
        - 'subgenre_name': Nombre del subgénero.
        - 'number_of_appearances': Número total de apariciones del subgénero.
        - 'main_genre': Identificador del género principal asociado.
        - 'brand_id': Identificador de la marca asociada.

    Proceso:
    --------
    1. Comprueba si el `brand_id` existe en la base de datos:
    - Se conecta a la tabla `brands` y verifica si el `brand_id` está presente.
    - Si no está, imprime un mensaje con los IDs disponibles y retorna un display de la tabla.

    2. Filtra y renombra columnas del DataFrame `subgeneros_df`:
    - Renombra la columna 'genre' a 'genre_name' para que coincida con la base de datos.

    3. Obtiene los géneros principales de la base de datos:
    - Se conecta a la tabla `main_genres` y filtra los registros por el `brand_id`.
    - Obtiene las columnas 'genre_name' y su identificador asociado ('id').

    4. Realiza un merge entre subgéneros y géneros principales:
    - Combina los datos para asociar cada subgénero con el identificador de su género principal.

    5. Ajusta las columnas y guarda el DataFrame en un archivo CSV:
    - Filtra las columnas necesarias y guarda el resultado en la ruta especificada.

    6. Muestra mensajes para:
    - Indicar que el archivo se generó correctamente.
    - Recomendar revisar el archivo antes de continuar.

    Notas:
    ------
    - Esta función espera como entrada el DataFrame generado por `mapear_main_genres()`.
    - Asegúrate de que los datos de la tabla `main_genres` en la base de datos estén completos antes de ejecutar esta función.
    - Este paso es esencial para mapear los subgéneros a los identificadores de los géneros principales en la base de datos.

    Siguientes pasos:
    -----------------
    1. Ejecutar `mapear_main_genres()` para generar el DataFrame inicial con los géneros mapeados.
    2. Verificar y procesar el DataFrame con esta función.
    3. Subir los datos procesados de subgéneros a la base de datos.
    """

    conexion = sql.conectar_bd()
    query = ''' SELECT * FROM brands'''
    df = sql.consulta_sql(conexion, query)
    df = df[["id","name"]]
    check = df["id"].tolist()
    if brand_id not in check:
        print("El id de la marca no existe")
        print("Los ids de las marcas son:")
        return display(df)
    
    subgeneros = subgeneros_df[["subgenre_name","number_of_appearances","genre","brand_id"]]
    subgeneros.rename(columns={"genre":"genre_name"},inplace=True)

    # LLamamos a la tabla de géneros principales
    conexion = sql.conectar_bd()
    query = f''' SELECT * FROM main_genres WHERE brand_id = {brand_id}'''
    main_genres_bd = sql.consulta_sql(conexion, query)
    main_genres_bd = main_genres_bd[["genre_name","id"]]
    
    #  Realizamos un merge para obtener el id de los géneros principales
    subgeneros = subgeneros.merge(main_genres_bd,how="left",on="genre_name")
    subgeneros = subgeneros[["subgenre_name","number_of_appearances","id","brand_id"]]
    subgeneros.rename(columns={"id":"main_genre"},inplace=True)
    # Guardar en csv
    subgeneros.to_csv(ruta_csv,index=False)
    print("Revisa la tabla antes de subirla!")
    print("Usa la funcion subir_main_genres(main_generos) para subir los datos")
    return subgeneros

def subir_subgenres(subgeneros_df, auto_id=False):
    """
    Sube los datos de subgéneros a la base de datos.

    Parámetros:
    -----------
    subgeneros_df : pandas.DataFrame
        DataFrame que contiene la información de los subgéneros. Debe incluir las columnas:
        - 'subgenre_name': Nombre del subgénero.
        - 'number_of_appearances': Número total de apariciones del subgénero.
        - 'main_genre': Identificador del género principal asociado.
        - 'brand_id': Identificador de la marca asociada.

    Proceso:
    --------
    1. Establece una conexión con la base de datos utilizando la función `sql.conectar_bd()`.
    2. Define la consulta SQL para insertar múltiples registros en la tabla `subgenres`.
    3. Convierte el DataFrame en una tupla de valores utilizando `sql.generar_tupla()`.
    4. Inserta los datos en la tabla `subgenres` de la base de datos utilizando 
    `sql.insertar_muchos_datos()`.

    Notas:
    ------
    - Asegúrate de que el DataFrame `subgeneros_df` no contiene valores nulos antes de ejecutar esta función.
    - La tabla `subgenres` en la base de datos debe estar configurada con las columnas adecuadas para que la inserción sea exitosa.
    - Esta función debe ejecutarse después de procesar los subgéneros con la función `obtener_subgenres()`.

    Siguientes pasos:
    -----------------
    1. Ejecutar `obtener_subgenres()` para procesar y preparar los datos de subgéneros.
    2. Usar esta función para insertar los datos procesados en la base de datos.
    """
    if auto_id:
        conexion = sql.conectar_bd()
        query = '''INSERT INTO subgenres(id,subgenre_name,number_of_appearances,main_genre,brand_id) VALUES (%s,%s,%s,%s,%s)'''
        sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(subgeneros_df))
    else:
        conexion = sql.conectar_bd()
        query = '''INSERT INTO subgenres(subgenre_name,number_of_appearances,main_genre,brand_id) VALUES (%s,%s,%s,%s)'''
        sql.insertar_muchos_datos(conexion,query,sql.generar_tupla(subgeneros_df))
