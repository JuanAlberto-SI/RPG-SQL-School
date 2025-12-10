import pyodbc
from typing import Optional

def get_db_connection(server: str = r".\SQLEXPRESS", 
                      database: str = "RetroRPG", 
                      trusted_connection: bool = True) -> Optional[pyodbc.Connection]:
    """
    Establece conexión a SQL Server.
    Intenta conectar a la instancia local y tiene un fallback a localhost.
    """
    
    # 1. INTENTO PRINCIPAL: Conectar a .\SQLEXPRESS (Estándar en casas)
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )

    try:
        connection = pyodbc.connect(connection_string)
        # print(f"Conectado exitosamente a {server}") # Comentado para no llenar consola
        return connection
        
    except pyodbc.Error:
        # 2. PLAN B (FALLBACK): Intentar conectar a 'localhost' (Estándar en laboratorios)
        print(f"Aviso: Falló conexión a {server}. Intentando con 'localhost'...")
        
        fallback_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER=localhost;" 
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
        )
        
        try:
            connection = pyodbc.connect(fallback_string)
            print("--> Conectado a 'localhost' (Plan B exitoso)")
            return connection
        except pyodbc.Error as e:
            # 3. SI TODO FALLA
            print("\nError Fatal de Conexión:")
            print(f"No se pudo conectar ni a '{server}' ni a 'localhost'.")
            print(f"Detalle del error: {e}")
            print("\nTips para solucionar:")
            print("1. Asegurate que SQL Server este corriendo.")
            print("2. Ejecuta el script setup_database.sql en la maquina.")
            return None

def test_connection() -> bool:
    """
    Función de prueba para verificar la conexión.
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            print(f"Versión de SQL Server detectada: {version[0][:50]}...")
            conn.close()
            return True
        except Exception as e:
            print(f"Error probando conexión: {e}")
            return False
    return False

if __name__ == "__main__":
    print("Probando conexión a base de datos...")
    if test_connection():
        print("¡TODO LISTO! La conexión funciona.")
    else:
        print("FALLÓ la conexión.")