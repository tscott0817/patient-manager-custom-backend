import psycopg2
from psycopg2 import sql
from psycopg2 import errors


'''
    Create DB
'''
def create_database(database_name):
    try:
        # Supposed to connect to default database 'postgres' instead of just the server??
        conn = psycopg2.connect(
            database="postgres",
            user='postgres',
            password='Oblivion14',
            host='localhost',
            port='5432'
        )
        conn.autocommit = True

        cursor = conn.cursor()
        sql_check_db = f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'"
        cursor.execute(sql_check_db)
        database_exists = cursor.fetchone()

        if not database_exists:
            sql_create_db = f"CREATE DATABASE {database_name}"
            cursor.execute(sql_create_db)
            print(f"Database '{database_name}' has been created successfully!")
        else:
            print(f"Database '{database_name}' already exists.")
        conn.close()

    except psycopg2.OperationalError as e:
        print("An error occurred:", e)


'''
    Table Creation
'''
def create_login_table(conn):
    table_name = "login_data"

    if table_exists(conn, table_name):
        print(f"The table '{table_name}' already exists.")
        return

    cursor = conn.cursor()
    table_creation = '''
        CREATE TABLE login_data (
            pat_id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    '''

    cursor.execute(table_creation)
    cursor.close()
    print(f"The table '{table_name}' has been created successfully.")


def create_demo_table(conn):
    # TODO: Table data
    #   Patient ID, Photo, Name, Address, Phone, Email,
    #   Sex, Age, B-Day, Race, Occupation, Employer Info, Emergency Contact

    table_name = "demographic_info"

    if table_exists(conn, table_name):
        print(f"The table '{table_name}' already exists.")
        return

    cursor = conn.cursor()
    table_creation = '''
        CREATE TABLE demographic_info (
            pat_id SERIAL PRIMARY KEY,
            pat_photo TEXT,
            pat_name TEXT NOT NULL,
            pat_sex TEXT NOT NULL,
            pat_birth TEXT NOT NULL,
            pat_address TEXT NOT NULL, 
            pat_phone TEXT NOT NULL,
            pat_email TEXT NOT NULL,
            pat_em_name TEXT NOT NULL,
            pat_em_relationship TEXT NOT NULL,
            pat_em_phone TEXT NOT NULL
        )
    '''

    cursor.execute(table_creation)
    cursor.close()
    print(f"The table '{table_name}' has been created successfully.")


def create_insurance_table(conn):
    # TODO: Data
    #   Insurer and info, Subscriber (who owns insurance) and info, Policy #, Patient Relationship to Insured

    table_name = "insurance_info"

    if table_exists(conn, table_name):
        print(f"The table '{table_name}' already exists.")
        return

    cursor = conn.cursor()
    table_creation = '''
        CREATE TABLE insurance_info (
            pat_id SERIAL PRIMARY KEY,
            ins_name TEXT NOT NULL,
            ins_subscriber TEXT NOT NULL,
            ins_policy_num TEXT NOT NULL,
            pat_relationship TEXT NOT NULL
        )
    '''

    cursor.execute(table_creation)
    cursor.close()
    print(f"The table '{table_name}' has been created successfully.")


def create_vitals_table(conn):
    table_name = "vitals"

    if table_exists(conn, table_name):
        print(f"The table '{table_name}' already exists.")
        return

    cursor = conn.cursor()
    table_creation = '''
        CREATE TABLE vitals (
            vitals_id SERIAL,
            pat_id SERIAL,
            visit_date TEXT NOT NULL,
            heart_rate TEXT NOT NULL,
            blood_pressure TEXT NOT NULL,
            body_temp TEXT NOT NULL,
            oxygen_sat TEXT,
            resp_rate TEXT,
            PRIMARY KEY (pat_id, vitals_id)
        )
    '''

    cursor.execute(table_creation)
    cursor.close()
    print(f"The table '{table_name}' has been created successfully.")


'''
    Helper Functions
'''
def table_exists(conn, table_name):
    try:
        cursor = conn.cursor()
        sql = f'''
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = '{table_name}'
        )
        '''
        cursor.execute(sql)
        exists = cursor.fetchone()[0]
        cursor.close()
        return exists
    except psycopg2.OperationalError as e:
        print("An error occurred:", e)
        return False


def add_tables():

    conn = psycopg2.connect(
        database="patients",
        user='postgres',
        password='Oblivion14',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True

    create_demo_table(conn)
    create_insurance_table(conn)
    create_vitals_table(conn)
    create_login_table(conn)

    conn.close()
