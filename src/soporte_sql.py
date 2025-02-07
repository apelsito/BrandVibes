#######################################################################################
##            Importación de bibliotecas para la conexión a bases de datos           ##
#######################################################################################
# Importar psycopg2 para la conexión y manejo de bases de datos PostgreSQL
import psycopg2

#######################################################################################
##            Manejo de errores específicos de psycopg2                             ##
#######################################################################################
# Importar manejo de errores específicos de psycopg2
from psycopg2 import OperationalError, errorcodes


#######################################################################################
##            Carga de variables de entorno                                        ##
#######################################################################################
# Importar dotenv para cargar variables de entorno desde un archivo .env
from dotenv import load_dotenv

# Importar os para acceder a variables de entorno del sistema
import os

#######################################################################################
##            Manipulación y análisis de datos tabulares                           ##
#######################################################################################
# Importar pandas para manipulación y análisis de datos tabulares
import pandas as pd

#######################################################################################
##            Configuración y manejo de advertencias                                ##
#######################################################################################
# Ignorar warnings
import warnings
warnings.filterwarnings("ignore")  # Suprime advertencias, manteniendo la salida de consola más limpia.

#######################################################################################
##            Carga de credenciales de la base de datos                             ##
#######################################################################################
# Cargar las variables de entorno desde un archivo .env
load_dotenv()

# Obtener credenciales de la base de datos desde las variables de entorno
USER = os.getenv("dbuser")          # Usuario de la base de datos
PASSWORD = os.getenv("dbpassword")  # Contraseña del usuario
HOST = os.getenv("dbhost")          # Dirección del servidor de la base de datos
PORT = os.getenv("dbport")          # Puerto del servidor de la base de datos
DBNAME = os.getenv("dbname")        # Nombre de la base de datos

#######################################################################################
##            Fin de los Imports                                                     ##
#######################################################################################


def conectar_bd():
    """
    Establece una conexión con la base de datos PostgreSQL.

    Retorna:
    --------
    conexion : psycopg2.extensions.connection
        Objeto de conexión a la base de datos, si la conexión es exitosa.

    Excepciones:
    ------------
    - OperationalError:
        - Si ocurre un error relacionado con la conexión a la base de datos.
        - Casos específicos manejados:
            - errorcodes.INVALID_PASSWORD: La contraseña proporcionada es incorrecta.
            - errorcodes.CONNECTION_EXCEPTION: Error general de conexión a la base de datos.

    Proceso:
    --------
    1. Intenta establecer una conexión con la base de datos PostgreSQL utilizando las credenciales 
    almacenadas en las variables de entorno (`USER`, `PASSWORD`, `HOST`, `PORT`, `DBNAME`).
    2. Si la conexión es exitosa:
        - Imprime un mensaje indicando que la conexión fue establecida.
        - Retorna el objeto de conexión.
    3. Si ocurre un error de conexión:
        - Detecta el tipo de error y muestra un mensaje informativo.
        - En caso de un error no específico, muestra un mensaje genérico con el código del error.

    Notas:
    ------
    - Asegúrate de que las credenciales correctas están definidas en las variables de entorno.
    - La base de datos PostgreSQL debe estar en ejecución y accesible desde la máquina que ejecuta esta función.
    """

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
    """
    Ejecuta una consulta SQL para modificar la base de datos PostgreSQL.

    Parámetros:
    -----------
    conexion : psycopg2.extensions.connection
        Objeto de conexión a la base de datos previamente establecido.

    query : str
        Consulta SQL que realiza modificaciones en la base de datos, como `INSERT`, `UPDATE` o `DELETE`.

    Proceso:
    --------
    1. Crea un cursor a partir de la conexión proporcionada.
    2. Ejecuta la consulta SQL especificada en el parámetro `query`.
    3. Confirma los cambios en la base de datos utilizando `commit()`.
    4. Cierra el cursor y la conexión para liberar recursos.
    5. Imprime un mensaje de éxito si la operación se realizó correctamente.

    Excepciones:
    ------------
    - Captura cualquier excepción que ocurra durante la ejecución de la consulta o los procesos relacionados:
        - Si ocurre un error, imprime un mensaje indicando que no se pudo realizar la operación, junto con el error específico.

    Notas:
    ------
    - Asegúrate de que la conexión esté activa y que el usuario tenga los permisos adecuados para realizar la operación.
    - Esta función debe ser utilizada con consultas que modifican la base de datos. Para consultas de solo lectura (como `SELECT`), utiliza una función diferente.
    """

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
    """
    Inserta múltiples registros en la base de datos PostgreSQL utilizando una consulta SQL parametrizada.

    Parámetros:
    -----------
    conexion : psycopg2.extensions.connection
        Objeto de conexión a la base de datos previamente establecido.

    query : str
        Consulta SQL parametrizada para la inserción de datos. Debe contener placeholders (%s) 
        para los valores a insertar, por ejemplo:
        `INSERT INTO tabla (columna1, columna2) VALUES (%s, %s)`.

    tupla : list[tuple]
        Lista de tuplas donde cada tupla representa un registro a insertar en la base de datos.
        Ejemplo: [(valor1, valor2), (valor3, valor4), ...]

    Proceso:
    --------
    1. Crea un cursor a partir de la conexión proporcionada.
    2. Ejecuta la consulta SQL para insertar múltiples registros utilizando `executemany()` con 
    la consulta y la lista de tuplas.
    3. Confirma los cambios en la base de datos utilizando `commit()`.
    4. Cierra el cursor y la conexión para liberar recursos.
    5. Imprime un mensaje de éxito si la operación se realizó correctamente.

    Excepciones:
    ------------
    - Captura cualquier excepción que ocurra durante la ejecución de la consulta o los procesos relacionados:
        - Si ocurre un error, imprime un mensaje indicando que no se pudo realizar la operación, junto con el error específico.

    Notas:
    ------
    - Asegúrate de que la conexión esté activa y que el usuario tenga los permisos adecuados para realizar la operación.
    - Verifica que la estructura de la lista de tuplas coincide con los placeholders definidos en la consulta SQL.
    - Es una función útil para insertar grandes volúmenes de datos de manera eficiente.
    """
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