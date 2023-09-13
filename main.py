import psycopg2
import operations
import create_db


# TODO: This feels weird to have as global.
# Database connection settings
db_connection = psycopg2.connect(
    database="patients",
    user="postgres",
    password="Oblivion14",
    host="localhost",
    port="5432"
)


def main():
    create_db.create_database('patients')
    create_db.add_tables()

    print("Patient Management System - Login")
    login_choice = int(input("Press 1 to login, 2 to create new user: "))
    if login_choice == 1:
        pat_id = operations.login()

        running = True
        while running:
            print("\nOptions:")
            print("1. Add / Update Information")
            print("2. Delete Patient")
            print("3. Logout")
            op_choice = int(input("Enter your choice: "))

            if op_choice == 1:
                t_choice = table_choice()
                add_info(pat_id, t_choice)

            # TODO: Works good, but add secondary check (are you sure?)
            elif op_choice == 2:
                operations.delete_patient_data(pat_id)
            elif op_choice == 3:
                print("Logged out.")
                running = False
            else:
                print("Invalid choice. Please select a valid option (1-4).")

    elif login_choice == 2:
        operations.create_user()


# Which table to add / update
def table_choice():
    # Add information
    print("\nSelect a table to add information:")
    print("1. Login Info")
    print("2. Demographic Info")
    print("3. Insurance Info")
    print("4. Vital Signs")
    table = int(input("Enter your choice: "))

    return table


# TODO: This will be replaced by a form
def add_info(pat_id, t_choice):
    if t_choice == 1:
        # Add login info
        # Implement logic to add login info here
        # TODO: Update password here
        pass
    elif t_choice == 2:

        patient_demo_data = []
        patient_name = input("Enter patient name: ")
        patient_sex = input("Sex: ")
        patient_birth = input("Birth: ")  # TODO: Change to b-day not age
        patient_address = input("Address: ")
        patient_phone = input("Phone: ")
        patient_email = input("Email: ")
        patient_em_name = input("Emergency Contact Name: ")
        patient_em_relationship = input("Emergency Contact Relationship: ")
        patient_em_phone = input("Emergency Contact Phone: ")

        patient_demo_data.append(patient_name)
        patient_demo_data.append(patient_sex)
        patient_demo_data.append(patient_birth)
        patient_demo_data.append(patient_address)
        patient_demo_data.append(patient_phone)
        patient_demo_data.append(patient_email)
        patient_demo_data.append(patient_em_name)
        patient_demo_data.append(patient_em_relationship)
        patient_demo_data.append(patient_em_phone)

        operations.insert_demographic_info(pat_id, patient_demo_data)

    elif t_choice == 3:
        patient_insurance_data = []
        patient_insurer = input("Enter patient insurer: ")
        patient_subscriber = input("Subscriber Name (Policy Owner): ")
        patient_policy_num = input("Policy Number: ")
        patient_relationship = input("Relationship to Insured: ")

        patient_insurance_data.append(patient_insurer)
        patient_insurance_data.append(patient_subscriber)
        patient_insurance_data.append(patient_policy_num)
        patient_insurance_data.append(patient_relationship)

        operations.insert_insurance_info(pat_id, patient_insurance_data)

    elif t_choice == 4:
        patient_vital_data = []
        visit_date = input("Enter visit date: ")
        blood_pressure = input("Enter blood pressure: ")
        heart_rate = input("Enter heart rate: ")
        body_temp = input("Enter temperature: ")

        patient_vital_data.append(visit_date)
        patient_vital_data.append(blood_pressure)
        patient_vital_data.append(heart_rate)
        patient_vital_data.append(body_temp)

        operations.insert_patient_vitals(pat_id, patient_vital_data)
    else:
        print("Invalid table choice. Please select a valid option (1-4).")


if __name__ == '__main__':
    main()

