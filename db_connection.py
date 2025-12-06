"""
Database Connection Module
Handles SQL Server database connections using pyodbc
"""
import pyodbc
from typing import Optional


def get_db_connection(server: str = "localhost\\SQLEXPRESS", 
                     database: str = "RetroRPG",
                     trusted_connection: bool = True) -> Optional[pyodbc.Connection]:
    """
    Establishes a connection to SQL Server database.
    
    Args:
        server: SQL Server instance name (default: localhost\\SQLEXPRESS)
        database: Database name (default: RetroRPG)
        trusted_connection: Use Windows Authentication (default: True)
    
    Returns:
        pyodbc.Connection object if successful, None otherwise
    """
    try:
        # Build connection string
        if trusted_connection:
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;"
            )
        else:
            # For SQL Server authentication (if needed later)
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE={database};"
                f"UID=your_username;"
                f"PWD=your_password;"
            )
        
        # Attempt connection
        connection = pyodbc.connect(connection_string)
        print(f"Successfully connected to {database} on {server}")
        return connection
    
    except pyodbc.Error as e:
        print(f"Database connection error: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure SQL Server Express is running")
        print("2. Verify the server name (try 'localhost' or '.\\SQLEXPRESS')")
        print("3. Check if ODBC Driver 17 for SQL Server is installed")
        print("4. Verify the database 'RetroRPG' exists")
        return None
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def test_connection() -> bool:
    """
    Test function to verify database connection.
    
    Returns:
        True if connection successful, False otherwise
    """
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT @@VERSION")
            version = cursor.fetchone()
            print(f"SQL Server version: {version[0]}")
            conn.close()
            return True
        except Exception as e:
            print(f"Error testing connection: {e}")
            return False
    return False


if __name__ == "__main__":
    # Test the connection when run directly
    print("Testing database connection...")
    test_connection()

