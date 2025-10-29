import mysql.connector
import sys
from urllib.parse import urlparse

# === CONFIGURATION ===
# Replace this placeholder with your actual Railway database connection URL.
# This URL contains all your credentials (user, password, host, port, etc.).
CONNECTION_URL = "mysql://root:GObNpMpeklBWLrHhvOfIQPTXbhhQspJn@ballast.proxy.rlwy.net:34464/railway"
SQL_FILE = "output.sql"
# =====================

def upload_sql_file(connection_url, sql_file_path):
    """
    Connects to a MySQL database using a full URL and executes all SQL commands from a file.
    """
    connection = None
    cursor = None
    try:
        print("Connecting to the MySQL database...")
        
        # Parse the connection URL to extract individual components
        url = urlparse(connection_url)
        
        # Extract the necessary connection details
        conn_params = {
            "host": url.hostname,
            "user": url.username,
            "password": url.password,
            "database": url.path.strip('/'),
            "port": url.port if url.port else 3306  # Use default port if none is specified
        }
        
        connection = mysql.connector.connect(**conn_params)
        cursor = connection.cursor()
        print("Connection successful.")

        print(f"Reading SQL commands from '{sql_file_path}'...")
        sql_commands = ""
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_commands = f.read()
        except UnicodeDecodeError:
            print("UTF-8 decoding failed. Trying 'latin-1' encoding...")
            try:
                with open(sql_file_path, 'r', encoding='latin-1') as f:
                    sql_commands = f.read()
            except Exception as e:
                print(f"An error occurred while reading the file with 'latin-1': {e}")
                sys.exit(1)

        # Pre-process the SQL commands to be MySQL-compatible
        # Replace double quotes around table/column names with backticks
        sql_commands = sql_commands.replace('"', '`')
        # Replace TEXT with VARCHAR for MySQL compatibility
        sql_commands = sql_commands.replace('TEXT', 'VARCHAR(255)')

        # Split the commands by semicolon.
        commands = sql_commands.split(';')

        print("Executing SQL commands...")
        for command in commands:
            command_stripped = command.strip()
            # Skip SQLite-specific transaction commands and empty commands
            if not command_stripped or command_stripped.upper() in ["BEGIN TRANSACTION", "COMMIT"]:
                continue

            try:
                cursor.execute(command_stripped)
            except mysql.connector.Error as err:
                print(f"Error executing command: {command_stripped}")
                print(f"Error details: {err}")
                # You can choose to break here if an error occurs.
                # For this script, we'll continue to try other commands.

        # Commit all the changes to the database.
        connection.commit()
        print("All SQL commands executed and committed successfully!")

    except mysql.connector.Error as err:
        print(f"An error occurred: {err}")
        sys.exit(1)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            print("MySQL connection is closed.")

if __name__ == "__main__":
    # Ensure you are in the same directory as this script and the SQL file.
    upload_sql_file(CONNECTION_URL, SQL_FILE)


