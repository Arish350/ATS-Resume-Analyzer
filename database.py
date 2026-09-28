import os
import mysql.connector


def get_connection():

    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "ats_resume_db"),
        port=int(os.getenv("MYSQL_PORT", "3306"))
    )

    return connection


if __name__ == "__main__":

    try:
        connection = get_connection()

        if connection.is_connected():
            print("MySQL Connected Successfully!")

        connection.close()

    except mysql.connector.Error as error:
        print("MySQL Connection Error:", error)