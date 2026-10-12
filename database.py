
import os
import mysql.connector
from mysql.connector import Error


def get_connection():
    required_vars = [
        "MYSQL_HOST",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE",
    ]

    missing = [
        name for name in required_vars
        if not os.getenv(name)
    ]

    if missing:
        raise RuntimeError(
            "Missing database environment variables: "
            + ", ".join(missing)
        )

    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("Arish18092024"),
        database=os.getenv("MYSQL_DATABASE"),
        connection_timeout=10,
    )


if __name__ == "__main__":
    connection = None

    try:
        connection = get_connection()
        print("MySQL Connected Successfully!")

    except (Error, RuntimeError, ValueError) as error:
        print("MySQL Connection Error:", error)

    finally:
        if connection is not None and connection.is_connected():
            connection.close()
