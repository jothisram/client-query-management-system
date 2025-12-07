# load_data.py
import pandas as pd
import psycopg2
from datetime import datetime

# --- DATABASE CONFIGURATION ---
db_config = {
    'dbname': 'query_system',
    'user': 'postgres',
    'password': 'lord818720',  # <--- UPDATE THIS
    'host': 'localhost',
    'port': '5432'
}

def load_csv_to_postgres():
    try:
        # Read CSV
        # Using the file provided in context
        df = pd.read_csv('synthetic_client_queries.csv')
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("Importing data to PostgreSQL... please wait.")
        
        for index, row in df.iterrows():
            # Handle dates (NaN check)
            created = row['date_raised']
            closed = row['date_closed'] if pd.notna(row['date_closed']) else None
            
            # Insert Query
            # Mapping CSV columns to your Table Schema
            sql = """
                INSERT INTO queries 
                (mail_id, mobile_number, query_heading, query_description, status, query_created_time, query_closed_time) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            val = (
                row['client_email'], 
                row['client_mobile'], 
                row['query_heading'], 
                row['query_description'], 
                row['status'], 
                created, 
                closed
            )
            cursor.execute(sql, val)
            
        conn.commit()
        print("Data imported successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    load_csv_to_postgres()# load_data.py
import pandas as pd
import psycopg2
from datetime import datetime

# --- DATABASE CONFIGURATION ---
db_config = {
    'dbname': 'query_system',
    'user': 'postgres',
    'password': 'YOUR_PASSWORD',  # <--- UPDATE THIS
    'host': 'localhost',
    'port': '5432'
}

def load_csv_to_postgres():
    try:
        # Read CSV
        # Using the file provided in context
        df = pd.read_csv('synthetic_client_queries.csv')
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        print("Importing data to PostgreSQL... please wait.")
        
        for index, row in df.iterrows():
            # Handle dates (NaN check)
            created = row['date_raised']
            closed = row['date_closed'] if pd.notna(row['date_closed']) else None
            
            # Insert Query
            # Mapping CSV columns to your Table Schema
            sql = """
                INSERT INTO queries 
                (mail_id, mobile_number, query_heading, query_description, status, query_created_time, query_closed_time) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            val = (
                row['client_email'], 
                row['client_mobile'], 
                row['query_heading'], 
                row['query_description'], 
                row['status'], 
                created, 
                closed
            )
            cursor.execute(sql, val)
            
        conn.commit()
        print("Data imported successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    load_csv_to_postgres()