# load_data.py
import pandas as pd
import psycopg2
import hashlib
from psycopg2.extras import execute_values

db_config = {
    "dbname": "query_system",
    "user": "postgres",
    "password": "lord818720",
    "host": "localhost",
    "port": "5432"
}

def make_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_csv_to_postgres(csv_path="synthetic_client_queries.csv", demo_reset=True):
    df = pd.read_csv(csv_path)

    # --- CLEAN DATA ---
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["status"] = df["status"].replace({
        "resolved": "closed",
        "in progress": "open",
        "inprogress": "open",
        "pending": "open"
    })
    # Title-case to match DB CHECK constraint: 'Open' / 'Closed'
    df["status"] = df["status"].str.title()

    df["date_raised"] = pd.to_datetime(df["date_raised"], errors="coerce")
    df["date_closed"] = pd.to_datetime(df["date_closed"], errors="coerce")

    # Fill required defaults
    df["client_email"] = df["client_email"].astype(str).str.strip()
    df["client_mobile"] = df.get("client_mobile", pd.Series([""] * len(df)))

    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    try:
        if demo_reset:
            # Remove existing demo queries (keeps users)
            cur.execute("TRUNCATE TABLE queries RESTART IDENTITY;")
            conn.commit()

        # Ensure all unique users exist in users table (use a default password)
        unique_emails = df["client_email"].dropna().unique().tolist()
        if unique_emails:
            hashed_default = make_hash("ChangeMe123!")  # change later in production
            users_vals = [(email, hashed_default, "Client") for email in unique_emails]
            # insert many; ON CONFLICT DO NOTHING
            execute_values(
                cur,
                """
                INSERT INTO users (username, hashed_password, role)
                VALUES %s
                ON CONFLICT (username) DO NOTHING
                """,
                users_vals
            )
            conn.commit()

        # Insert queries in bulk
        insert_rows = []
        for _, row in df.iterrows():
            # If date_raised missing, set to now
            created = row["date_raised"] if not pd.isna(row["date_raised"]) else pd.Timestamp.now()
            closed = row["date_closed"] if (("date_closed" in row) and not pd.isna(row["date_closed"])) else None
            insert_rows.append((
                row["client_email"],
                row["client_mobile"] if not pd.isna(row["client_mobile"]) else None,
                row.get("query_heading", "")[:255],
                row.get("query_description", ""),
                row["status"] if row["status"] in ("Open", "Closed") else "Open",
                created,
                closed
            ))

        execute_values(
            cur,
            """
            INSERT INTO queries
            (mail_id, mobile_number, query_heading, query_description, status, query_created_time, query_closed_time)
            VALUES %s
            """,
            insert_rows
        )
        conn.commit()
        print("✅ Clean data imported successfully")

    except Exception as e:
        conn.rollback()
        print("❌ Error during load:", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    load_csv_to_postgres()
