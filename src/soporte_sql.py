import psycopg2
from psycopg2 import OperationalError, errorcodes, errors  # Manejo de errores específicos de psycopg2 para controlar excepciones
from dotenv import load_dotenv
import os
import pandas as pd
# Ignorar warnings
# -----------------------------------------------------------------------
import warnings
warnings.filterwarnings("ignore")                 # Suprime advertencias, manteniendo la salida de consola más limpia

# Load environment variables from .env
load_dotenv()

USER = os.getenv("dbuser")
PASSWORD = os.getenv("dbpassword")
HOST = os.getenv("dbhost")
PORT = os.getenv("dbport")
DBNAME = os.getenv("dbname")

def conectar_bd():
    # Connect to the database
    try:
        conexion = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
        print (f"Conectado a la base de datos")
        
        return conexion
    except OperationalError as e:
        if e.pgcode == errorcodes.INVALID_PASSWORD:
            print("La contraseña es errónea")
        elif e.pgcode == errorcodes.CONNECTION_EXCEPTION:
            print("Error de conexión")
        else:
            print(f"Ocurrió el error {e}")

def modificar_bd(conexion, query):
    try:
        cursor = conexion.cursor()
        cursor.execute(query)
        conexion.commit()
        cursor.close()
        conexion.close()
        print("Se ha modificado correctamente la base de Datos")
    except Exception as e:
        print("No se ha podido realizar la operación:", e)
    
def insertar_muchos_datos(conexion,query,tupla):
    try:
        cursor = conexion.cursor()
        cursor.executemany(query,tupla)
        conexion.commit()
        cursor.close()
        conexion.close()
        print("Se han añadido los valores correctamente")
    except Exception as e:
        print("No se ha podido realizar la operación:", e)
    
def generar_tupla(df,drop_index=False,fix_np = False):
    """
    Convierte un DataFrame de pandas en una lista de tuplas para su uso en operaciones de inserción en bases de datos.

    Args:
        df (pandas.DataFrame): DataFrame que se convertirá en una lista de tuplas.
        drop_index (bool, optional): Indica si se debe eliminar la columna de índice llamada "index" del DataFrame. 
                                     El valor predeterminado es False.

    Returns:
        list of tuples: Lista de tuplas, donde cada tupla representa una fila del DataFrame.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'col1': [1, 2], 'col2': ['A', 'B']})
        >>> generar_tupla(df)
        [(1, 'A'), (2, 'B')]
    """
    if drop_index == True:
        df.drop(columns="index",inplace=True)
    
    tupla = [tuple(valores) for valores in df.values]
    
    if fix_np == True:
        tupla = [(int(x), int(y)) for x, y in tupla]

    return tupla

def consulta_sql(conexion, query):
    """
    Ejecuta una consulta SQL en la base de datos PostgreSQL y devuelve los resultados en un DataFrame de pandas.

    Args:
        conexion: Objeto de conexión a la base de datos, previamente establecido.
        query (str): Cadena de texto con la consulta SQL a ejecutar.

    Returns:
        pandas.DataFrame: DataFrame que contiene los resultados de la consulta, con las columnas correspondientes.

    Example:
        >>> df = consulta_sql(conexion, "SELECT * FROM productos")
        >>> print(df.head())
        
    Notes:
        La conexión a la base de datos se cierra después de ejecutar la consulta.
    """
    cursor = conexion.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    columnas = [col[0] for col in cursor.description]
    cursor.close()
    conexion.close()
    df = pd.DataFrame(resultados,columns=columnas)
    return df