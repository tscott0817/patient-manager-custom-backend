import psycopg2
from psycopg2 import sql
from psycopg2 import errors
from passlib.hash import sha256_crypt


def create_roles():
    # Database connection parameters
    conn = psycopg2.connect(
        database="patients",
        user='postgres',
        password='Oblivion14',
        host='localhost',
        port='5432'
    )

    # Connect to the database with superuser privileges
    # conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Define the roles you want to create
    roles_to_create = ["admin", "doctor", "nurse", "patient"]

    # Create roles
    for role in roles_to_create:
        create_role_query = f"CREATE ROLE {role};"
        cur.execute(create_role_query)

    # Grant permissions to roles
    db_name = "patients"
    grant_permissions_queries = [
        f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO admin;",
        f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin;",
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON patients TO doctor;",
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON vitals TO doctor;",
        f"GRANT SELECT, INSERT, UPDATE ON patients TO nurse;",
        f"GRANT SELECT, INSERT, UPDATE ON demographic_info TO nurse;",
        f"GRANT SELECT ON demographic_info TO patient;"
    ]

    for query in grant_permissions_queries:
        cur.execute(query)

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()


def connect_to_database():
    return psycopg2.connect(
        database="patients",
        user='postgres',
        password='Oblivion14',
        host='localhost',
        port='5432'
    )


def create_user(username, password):

    # Check to make sure username is not already stored in database
    conn = connect_to_database()
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM login_data WHERE username = %s", (username,))
    result = cursor.fetchone()
    if result:
        return False  # User already exists
    else:
        insert_user(username, password)
        return True  # User does not exist


def login():
    while True:
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        cursor = connect_to_database().cursor()
        cursor.execute("SELECT pat_id, password FROM login_data WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            patient_id, hashed_password = result
            if sha256_crypt.verify(password, hashed_password):
                print("Login successful!")
                return patient_id
            else:
                print("Invalid password. Try again.")
        else:
            print("User not found. Try again.")


def insert_user(username, password):
    conn = connect_to_database()
    conn.autocommit = True
    cursor = conn.cursor()

    try:
        # Insert into login_data table and return the login unique ID
        hashed_password = sha256_crypt.hash(password)
        sql_login = '''
            INSERT INTO login_data (username, password)
            VALUES (%s, %s)
            RETURNING pat_id
        '''
        cursor.execute(sql_login, (username, hashed_password))
        pat_id = cursor.fetchone()[0]

        return pat_id
    except Exception as e:
        print(f"Error inserting user: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_demographic_info(pat_id, patient_demo_data):
    conn = connect_to_database()
    conn.autocommit = True
    cursor = conn.cursor()

    # Convert the list to a tuple using the tuple() constructor
    patient_demo_data_tuple = tuple(patient_demo_data)  # TODO: Not sure I like this cast here

    try:
        # Check if a row already exists for the patient in the demographic_info table
        cursor.execute("SELECT COUNT(*) FROM demographic_info WHERE pat_id = %s", (pat_id,))
        row_count = cursor.fetchone()[0]

        if row_count > 0:
            # Update the existing row if it exists
            sql_update = '''
                UPDATE demographic_info
                SET pat_name = %s, pat_sex = %s, pat_birth = %s, pat_address = %s,
                    pat_phone = %s, pat_email = %s, pat_em_name = %s, pat_em_relationship = %s, pat_em_phone = %s
                WHERE pat_id = %s
            '''
            cursor.execute(sql_update, patient_demo_data_tuple + (pat_id,))
        else:
            # Insert a new row if no row exists for the patient
            sql_insert = '''
                INSERT INTO demographic_info (
                    pat_id,
                    pat_name,
                    pat_sex,
                    pat_birth,
                    pat_address,
                    pat_phone,
                    pat_email,
                    pat_em_name,
                    pat_em_relationship,
                    pat_em_phone
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            '''
            cursor.execute(sql_insert, (pat_id,) + patient_demo_data_tuple)
    except Exception as e:
        print(f"Error inserting/updating demographic info: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_insurance_info(pat_id, patient_insurance_data):
    conn = connect_to_database()
    conn.autocommit = True
    cursor = conn.cursor()

    # Convert the list to a tuple using the tuple() constructor
    patient_insurance_data_tuple = tuple(patient_insurance_data)  # TODO: Not sure I like this cast here

    try:
        # Check if a row already exists for the patient in the insurance_info table
        cursor.execute("SELECT COUNT(*) FROM insurance_info WHERE pat_id = %s", (pat_id,))
        row_count = cursor.fetchone()[0]

        if row_count > 0:
            # Update the existing row if it exists
            sql_update = '''
                UPDATE insurance_info
                SET ins_name = %s, ins_subscriber = %s, ins_policy_num = %s, pat_relationship = %s
                WHERE pat_id = %s
            '''
            cursor.execute(sql_update, patient_insurance_data_tuple + (pat_id,))
        else:
            # Insert a new row if no row exists for the patient
            sql_insert = '''
                INSERT INTO insurance_info (
                    pat_id,
                    ins_name,
                    ins_subscriber,
                    ins_policy_num,
                    pat_relationship
                )
                VALUES (%s, %s, %s, %s, %s)
            '''
            cursor.execute(sql_insert, (pat_id,) + patient_insurance_data_tuple)
    except Exception as e:
        print(f"Error inserting/updating insurance info: {e}")
    finally:
        cursor.close()
        conn.close()


def update_patient_data(pat_id, patient_demo_data, patient_insurance_data):
    conn = psycopg2.connect(
        database="patients",
        user='postgres',
        password='Oblivion14',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True

    cursor = conn.cursor()

    try:
        # Update demographic_info table
        sql_demo_update = f'''
            UPDATE demographic_info
            SET
                pat_name = '{patient_demo_data[0]}',
                pat_sex = '{patient_demo_data[1]}',
                pat_birth = '{patient_demo_data[2]}',
                pat_address = '{patient_demo_data[3]}',
                pat_phone = '{patient_demo_data[4]}',
                pat_email = '{patient_demo_data[5]}',
                pat_em_name = '{patient_demo_data[6]}',
                pat_em_relationship = '{patient_demo_data[7]}',
                pat_em_phone = '{patient_demo_data[8]}'
            WHERE
                pat_id = {pat_id}
        '''
        cursor.execute(sql_demo_update)

        # Update insurance_info table
        sql_insurance_update = f'''
            UPDATE insurance_info
            SET
                ins_name = '{patient_insurance_data[0]}',
                ins_subscriber = '{patient_insurance_data[1]}',
                ins_policy_num = '{patient_insurance_data[2]}',
                pat_relationship = '{patient_insurance_data[3]}'
            WHERE
                pat_id = {pat_id}
        '''
        cursor.execute(sql_insurance_update)

        conn.commit()
    except Exception as e:
        # Handle any exceptions that may occur during database operations
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def insert_patient_vitals(pat_id, patient_vital_data):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        database="patients",
        user='postgres',
        password='Oblivion14',
        host='localhost',
        port='5432'
    )

    # Create a cursor
    cursor = conn.cursor()

    # Convert the list to a tuple using the tuple() constructor
    patient_vital_data_tuple = tuple(patient_vital_data)  # TODO: Not sure I like this cast here
    try:
        # Define the SQL statement to insert vitals data
        insert_query = sql.SQL("""
            INSERT INTO vitals (pat_id, visit_date, blood_pressure, heart_rate, body_temp)
            VALUES (%s, %s, %s, %s, %s)
        """)

        # Execute the SQL statement with the provided data
        cursor.execute(insert_query, (pat_id,) + patient_vital_data_tuple)

        # Commit the transaction
        conn.commit()

        print("Vitals data added successfully.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error adding vitals data: {error}")
    finally:
        # Close the database connection
        if conn:
            cursor.close()
            conn.close()


def get_pat_id():
    # Return the pat_id from the login_data table
    conn = psycopg2.connect(
        database="patients",
        user='postgres',
        password='Oblivion14',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True

    cursor = conn.cursor()

    try:
        sql_select = '''
            SELECT pat_id
            FROM login_data
        '''
        cursor.execute(sql_select)
        pat_id = cursor.fetchone()[0]
        return pat_id

    except Exception as e:
        # Handle any exceptions that may occur during database operations
        print(f"Error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()



def get_patient_data(pat_id):
    conn = psycopg2.connect(
        database="patients",
        user='postgres',
        password='Oblivion14',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True

    cursor = conn.cursor()

    try:

        sql_login_select = f'''
            SELECT *
            FROM login_data
            WHERE pat_id = {pat_id}
        '''
        cursor.execute(sql_login_select)
        login_data = cursor.fetchone()

        # Retrieve all columns from the demographic_info table
        sql_demo_select = f'''
            SELECT *
            FROM demographic_info
            WHERE pat_id = {pat_id}
        '''
        cursor.execute(sql_demo_select)
        demo_data = cursor.fetchone()

        # Retrieve all columns from the insurance_info table
        sql_insurance_select = f'''
            SELECT *
            FROM insurance_info
            WHERE pat_id = {pat_id}
        '''
        cursor.execute(sql_insurance_select)
        insurance_data = cursor.fetchone()

        # Retrieve all columns from the insurance_info table
        sql_vitals_select = f'''
            SELECT *
            FROM vitals
            WHERE pat_id = {pat_id}
        '''
        cursor.execute(sql_vitals_select)
        vitals = cursor.fetchall()  # To get every row with appropriate patient ID

        return login_data, demo_data, insurance_data, vitals

    except Exception as e:
        # Handle any exceptions that may occur during database operations
        print(f"Error: {e}")
        return None, None
    finally:
        cursor.close()
        conn.close()


def delete_patient_data(pat_id):
    conn = psycopg2.connect(
        database="patients",
        user='postgres',
        password='Oblivion14',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True

    cursor = conn.cursor()

    try:
        sql_login_delete = f'''
            DELETE FROM login_data
            WHERE pat_id = {pat_id}
        '''
        cursor.execute(sql_login_delete)

        # Delete records from the demographic_info table
        sql_demo_delete = f'''
            DELETE FROM demographic_info
            WHERE pat_id = {pat_id}
        '''
        cursor.execute(sql_demo_delete)

        # Delete records from the insurance_info table
        sql_insurance_delete = f'''
            DELETE FROM insurance_info
            WHERE pat_id = {pat_id}
        '''
        cursor.execute(sql_insurance_delete)

        # Retrieve all columns from the insurance_info table
        sql_vitals_delete = f'''
            DELETE FROM vitals
            WHERE pat_id = {pat_id}
        '''
        cursor.execute(sql_vitals_delete)

        print(f"Deleted all data for patient with pat_id {pat_id}")

    except Exception as e:
        # Handle any exceptions that may occur during database operations
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()