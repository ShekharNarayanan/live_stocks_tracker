import sqlite3
import io

def export_sqlite_to_sql_dump(db_path, output_path):
    """
    Exports all data and schema from a SQLite database to a single SQL dump file.

    Args:
        db_path (str): The path to the SQLite database file (.db).
        output_path (str): The path where the SQL dump file (.sql) will be saved.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # Create an in-memory string buffer
        with io.StringIO() as buffer:
            # Use the built-in .iterdump() to get the SQL dump
            for line in conn.iterdump():
                # Fix a common issue: add a semicolon at the end of each line
                buffer.write('%s\n' % line)
            
            # Write the content of the buffer to the output file
            with open(output_path, 'w') as output_file:
                output_file.write(buffer.getvalue())
        
        print(f"✅ Successfully exported '{db_path}' to '{output_path}'.")
        
    except sqlite3.Error as e:
        print(f"❌ An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# --- Configuration ---
# Replace 'your_database.db' with the name of your local SQLite file
SQLITE_DB_FILE = 'portfolios.db' 
# Replace 'output.sql' with the desired name for your SQL dump file
OUTPUT_SQL_FILE = 'output.sql'

# Run the export function
if __name__ == "__main__":
    export_sqlite_to_sql_dump(SQLITE_DB_FILE, OUTPUT_SQL_FILE)