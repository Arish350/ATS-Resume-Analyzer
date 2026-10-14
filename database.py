import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=False)


def get_connection():
    password = os.getenv("MYSQL_PASSWORD")

    if not password:
        raise RuntimeError(
            f"MYSQL_PASSWORD is missing. Check: {env_path}"
        )

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=password,
        database=os.getenv("MYSQL_DATABASE", "ats_resume_db")
    )


if __name__ == "__main__":
    try:
        conn = get_connection()
        print("MySQL Backend Connected Successfully!")
        print("Database:", conn.database)
        conn.close()

    except mysql.connector.Error as error:
        print("MySQL Connection Error:", error)

    except Exception as error:
        print("Error:", error)
