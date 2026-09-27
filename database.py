
import mysql.connector


def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Arish18092024",
        database="ats_resume_db"
    )

    return connection


if __name__ == "__main__":
    connection = get_connection()

    if connection.is_connected():
        print("MySQL Connected Successfully!")

    connection.close()