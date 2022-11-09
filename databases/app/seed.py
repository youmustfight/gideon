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
    insert_user_query = """ INSERT INTO "user" (name, email) VALUES ('gideon', 'gideon@gideon.com') """
    cursor.execute(insert_user_query)
    connection.commit()
    # --- case
    insert_case_query = """ INSERT INTO "case" DEFAULT VALUES """
    cursor.execute(insert_case_query)
    connection.commit()
    # --- user_case
    cursor.execute(""" SELECT id FROM "case" ORDER BY id DESC LIMIT 1 """)
    case_id = cursor.fetchone()[0]
    cursor.execute(""" SELECT id FROM "user" ORDER BY id DESC LIMIT 1 """)
    user_id = cursor.fetchone()[0]
    print(f'Inserted IDs: case_id ({case_id}), user_id ({user_id})')
    insert_case_user_query = f""" INSERT INTO "case_user" (case_id, user_id) VALUES ({case_id}, {user_id}) """
    cursor.execute(insert_case_user_query)
    connection.commit()


except Exception as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if (connection):
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")
