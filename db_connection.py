import pyodbc
from typing import Optional

def get_db_connection(server: str = r"DESKTOP-GKI5BE3\SQLEXPRESS", 
                      database: str = "RetroRPG", 
                      trusted_connection: bool = True) -> Optional[pyodbc.Connection]:
    """
    Establece conexión a SQL Server.
    """
    
    # Cadena de conexión segura
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )

    try:
        connection = pyodbc.connect(connection_string)
        print(f"Successfully connected to {database} on {server}")
        return connection
    except pyodbc.Error as e:
        print(f"Database connection error: {e}")
        return None

# Bloque de prueba (opcional, por si quieres ejecutar este archivo solo)
if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("¡Conexión exitosa!")
        conn.close()
    else:
        print("Falló la conexión.")