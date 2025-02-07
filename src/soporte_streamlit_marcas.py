#######################################################################################
##          Importación de bibliotecas para manipulación y análisis de datos         ##
#######################################################################################
# Importar la biblioteca pandas para manipulación y análisis de datos tabulares
import pandas as pd

#######################################################################################
##                  Modificar el sistema de rutas                                    ##
#######################################################################################

# Modificar el sistema de rutas para permitir importar módulos desde el directorio padre
import sys 
sys.path.append("../")

#######################################################################################
##            Fin de los Imports                                                     ##
#######################################################################################

# Consulta a la base de datos para contar seguidores
def obtener_numero_seguidores(supabase_credential, id_brand = 0):
    """
    Obtiene el número de seguidores de una marca específica desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.
    
    id_brand : int, opcional (por defecto 0)
        Identificador de la marca cuyos seguidores se desean contar. Si no se especifica, se muestra un mensaje de error.

    Retorna:
    -------
    int
        Número total de seguidores de la marca especificada.

    Descripción:
    -----------
    - Si no se proporciona un `id_brand` válido, muestra un mensaje de advertencia.
    - Consulta la tabla `followers` en Supabase para contar los seguidores asociados al `id_brand`.
    - Devuelve la cantidad de seguidores de la marca como un entero.
    """

    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        number_of_followers = len(supabase_credential.table("followers").select("*").eq("brand_id", id_brand).execute().data)
        return number_of_followers
    
def obtener_numero_playlists(supabase_credential, id_brand = 0):
    """
    Obtiene el número total de playlists asociadas a los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.
    
    id_brand : int, opcional (por defecto 0)
        Identificador de la marca cuyos seguidores y playlists se desean contar. 
        Si no se especifica, se muestra un mensaje de error.

    Retorna:
    -------
    int
        Número total de playlists asociadas a los seguidores de la marca especificada.

    Descripción:
    -----------
    - Si no se proporciona un `id_brand` válido, muestra un mensaje de advertencia.
    - Obtiene los identificadores de los seguidores de la marca desde la tabla `followers`.
    - Consulta la tabla `playlists` en Supabase para contar todas las playlists creadas por estos seguidores.
    - Utiliza paginación para manejar grandes volúmenes de datos con un límite de 1000 registros por consulta.
    - Devuelve la cantidad total de playlists encontradas.
    """

    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        followers_response = supabase_credential.table("followers").select("id").eq("brand_id", id_brand).execute().data
        # Pasamos los ids a una lista
        lista_follower_ids = [follower['id'] for follower in followers_response]

        all_playlists = []
        limit = 1000
        # Set the limit for each query
        offset = 0
        while True:
            playlists_response = supabase_credential.table("playlists").select("*").in_("follower_id", lista_follower_ids).range(offset, offset + limit - 1).execute()
            if playlists_response.data:
                all_playlists.extend(playlists_response.data)  
                # Add the retrieved playlists to the list
                offset += limit  
                # Move to the next set of results
            else:
                break
    return len(all_playlists)

def obtener_numero_playlists_reducido(supabase_credential, id_brand = 0):
    """
    Obtiene el número total de playlists reducidas asociadas a los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.
    
    id_brand : int, opcional (por defecto 0)
        Identificador de la marca cuyos seguidores y playlists reducidas se desean contar. 
        Si no se especifica, se muestra un mensaje de error.

    Retorna:
    -------
    int
        Número total de playlists reducidas asociadas a los seguidores de la marca especificada.

    Descripción:
    -----------
    - Si no se proporciona un `id_brand` válido, muestra un mensaje de advertencia.
    - Obtiene los identificadores de los seguidores de la marca desde la tabla `followers`.
    - Consulta la tabla `reduced_playlists` en Supabase para contar todas las playlists reducidas creadas por estos seguidores.
    - Devuelve la cantidad total de playlists reducidas encontradas.
    """

    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        followers_response = supabase_credential.table("followers").select("id").eq("brand_id", id_brand).execute().data
        # Pasamos los ids a una lista
        lista_follower_ids = [follower['id'] for follower in followers_response]

    return len(supabase_credential.table("reduced_playlists").select("*").in_("follower_id", lista_follower_ids).execute().data)

def obtener_top_artistas(supabase_credential, start = 0, end = 0, id_brand = 0):
    """
    Obtiene el ranking de los artistas más escuchados por los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.
    
    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    id_brand : int, opcional (por defecto 0)
        Identificador de la marca cuyos artistas más escuchados se desean obtener.
        Si no se especifica, se muestra un mensaje de error.

    Retorna:
    -------
    list[dict]
        Lista de diccionarios con los artistas más escuchados y el número de veces que aparecen en las playlists.

    Descripción:
    -----------
    - Si no se proporciona un `id_brand` válido, muestra un mensaje de advertencia.
    - Consulta la tabla `artists_ranking` en Supabase para obtener los artistas más escuchados de la marca.
    - Filtra por `brand_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Permite paginar los resultados utilizando los parámetros `start` y `end`.
    - Devuelve una lista de diccionarios con los nombres de los artistas y su número de apariciones.
    """

    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('artists_ranking').select('artist_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).order('number_of_appearances',desc=True).execute().data

        return ranking_response
    
def obtener_resto_artistas(supabase_credential, start = 0, end = 0, id_brand = 0):
    """
    Obtiene un DataFrame con los artistas menos escuchados por los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.
    
    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    id_brand : int, opcional (por defecto 0)
        Identificador de la marca cuyos artistas menos escuchados se desean obtener.
        Si no se especifica, se muestra un mensaje de error.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de artistas, sus nombres y la cantidad de veces que han sido escuchados.

    Descripción:
    -----------
    - Si no se proporciona un `id_brand` válido, muestra un mensaje de advertencia.
    - Consulta la tabla `artists_ranking` en Supabase para obtener los artistas menos escuchados de la marca.
    - Filtra por `brand_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los artistas y su cantidad de apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "Ranking", "Artista" y "Cantidad de escuchas".
    """

    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('artists_ranking').select('artist_name','number_of_appearances').eq('brand_id', id_brand).range(start,end).order('number_of_appearances',desc=True).execute().data
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
    
def obtener_top_generos(supabase_credential, start = 0, end = 0, id_brand = 0):
    """
    Obtiene el ranking de los géneros musicales más escuchados por los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.
    
    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    id_brand : int, opcional (por defecto 0)
        Identificador de la marca cuyos géneros más escuchados se desean obtener.
        Si no se especifica, se muestra un mensaje de error.

    Retorna:
    -------
    list[dict]
        Lista de diccionarios con los géneros musicales más escuchados y el número de veces que aparecen en las playlists.

    Descripción:
    -----------
    - Si no se proporciona un `id_brand` válido, muestra un mensaje de advertencia.
    - Consulta la tabla `main_genres` en Supabase para obtener los géneros más escuchados de la marca.
    - Filtra por `brand_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Permite paginar los resultados utilizando los parámetros `start` y `end`.
    - Devuelve una lista de diccionarios con los nombres de los géneros y su número de apariciones.
    """

    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('main_genres').select('genre_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).order('number_of_appearances',desc=True).execute().data
        
        return ranking_response
    
def obtener_resto_generos(supabase_credential, start = 0, end = 0, id_brand = 0):
    """
    Obtiene un DataFrame con los géneros musicales menos escuchados por los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.
    
    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    id_brand : int, opcional (por defecto 0)
        Identificador de la marca cuyos géneros menos escuchados se desean obtener.
        Si no se especifica, se muestra un mensaje de error.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de géneros musicales, sus nombres y la cantidad de veces que han sido escuchados.

    Descripción:
    -----------
    - Si no se proporciona un `id_brand` válido, muestra un mensaje de advertencia.
    - Consulta la tabla `main_genres` en Supabase para obtener los géneros menos escuchados de la marca.
    - Filtra por `brand_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los géneros y su cantidad de apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "Ranking", "Género" y "Cantidad de escuchas".
    """

    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('main_genres').select('genre_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).order('number_of_appearances',desc=True).execute().data
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
    
def obtener_top_subgeneros(supabase_credential, start = 0, end = 0, id_brand = 0):
    """
    Obtiene el ranking de los subgéneros musicales más escuchados por los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.
    
    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    id_brand : int, opcional (por defecto 0)
        Identificador de la marca cuyos subgéneros más escuchados se desean obtener.
        Si no se especifica, se muestra un mensaje de error.

    Retorna:
    -------
    list[dict]
        Lista de diccionarios con los subgéneros musicales más escuchados y el número de veces que aparecen en las playlists.

    Descripción:
    -----------
    - Si no se proporciona un `id_brand` válido, muestra un mensaje de advertencia.
    - Consulta la tabla `subgenres` en Supabase para obtener los subgéneros más escuchados de la marca.
    - Filtra por `brand_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Permite paginar los resultados utilizando los parámetros `start` y `end`.
    - Devuelve una lista de diccionarios con los nombres de los subgéneros y su número de apariciones.
    """

    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('subgenres').select('subgenre_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).order('number_of_appearances',desc=True).execute().data

        return ranking_response
    
def obtener_resto_subgeneros(supabase_credential, start = 0, end = 0, id_brand = 0):
    """
    Obtiene un DataFrame con los subgéneros musicales menos escuchados por los seguidores de una marca desde la base de datos en Supabase.

    Parámetros:
    ----------
    supabase_credential : object
        Credenciales de autenticación para interactuar con la base de datos en Supabase.
    
    start : int, opcional (por defecto 0)
        Índice de inicio para la paginación de resultados.

    end : int, opcional (por defecto 0)
        Índice final para la paginación de resultados.

    id_brand : int, opcional (por defecto 0)
        Identificador de la marca cuyos subgéneros menos escuchados se desean obtener.
        Si no se especifica, se muestra un mensaje de error.

    Retorna:
    -------
    pandas.DataFrame
        DataFrame con el ranking de subgéneros musicales, sus nombres y la cantidad de veces que han sido escuchados.

    Descripción:
    -----------
    - Si no se proporciona un `id_brand` válido, muestra un mensaje de advertencia.
    - Consulta la tabla `subgenres` en Supabase para obtener los subgéneros menos escuchados de la marca.
    - Filtra por `brand_id` y ordena los resultados en orden descendente según el número de apariciones.
    - Construye un DataFrame con los nombres de los subgéneros y su cantidad de apariciones.
    - Ajusta el índice del DataFrame para reflejar el ranking correctamente.
    - Devuelve un DataFrame con las columnas "Ranking", "Subgénero" y "Cantidad de escuchas".
    """
    if id_brand == 0:
        print("No se ha especificado el id de la marca")
    else:
        # Primero obtenemos el id de los seguidores de la marca 
        ranking_response = supabase_credential.table('subgenres').select('subgenre_name','number_of_appearances').eq('brand_id', id_brand).range(start, end).order('number_of_appearances',desc=True).execute().data
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