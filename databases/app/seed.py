# adjusted from https://pynative.com/python-postgresql-tutorial/
# avoiding using sqlalchemy bc its faster to write simlple SQL commands than deal w/ models/engines/etc.

import psycopg2
import env

# Connect to an existing database
connection = psycopg2.connect(user=env.env_get_database_app_user_name(),
                                  password=env.env_get_database_app_user_password(),
                                  host=env.env_get_database_app_host(),
                                  port=env.env_get_database_app_port(),
                                  database=env.env_get_database_app_name())

try:
    # Create a cursor to perform database operations
    cursor = connection.cursor()
    # Executing a SQL query
    # --- user
    insert_user_query = """ INSERT INTO "user" (name, email, password) VALUES ('gideon', 'gideon@gideon.foundation', 'gideon') """
    cursor.execute(insert_user_query)
    connection.commit()


except Exception as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
