from flask import Flask, render_template, request, redirect, url_for, session, flash
from passlib.hash import sha256_crypt
import psycopg2
from psycopg2 import sql
from psycopg2 import errors

import create_db
import operations

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"  # Replace with a secure secret key


def connect_to_database():
    return psycopg2.connect(
        database="patients",
        user='postgres',
        password='Oblivion14',
        host='localhost',
        port='5432'
    )


# Define your login logic
def is_valid_login(username, password):
    cursor = connect_to_database().cursor()
    cursor.execute("SELECT pat_id, password FROM login_data WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:
        patient_id, hashed_password = result
        if sha256_crypt.verify(password, hashed_password):
            return patient_id

    return None

# Get the patient ID from the session
def get_patient_id():
    return session.get("patient_id", None)


@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # Check if login is valid
    patient_id = is_valid_login(username, password)

    if patient_id:
        # Store the patient ID in the session
        session["patient_id"] = patient_id
        return redirect(url_for("dashboard", pat_id=patient_id))
    else:
        return "Invalid login credentials. Please try again."


# Dashboard route
@app.route("/dashboard")
def dashboard():
    # Retrieve the patient ID from the session
    patient_id = session.get("patient_id")

    if patient_id is not None:
        return render_template("dashboard.html")
    else:
        return "Unauthorized. Please login."


@app.route("/select_option", methods=["POST"])
def select_option():
    option = request.form.get("option")

    if option == "demographic":
        return redirect(url_for("add_demographic_info"))
    elif option == "insurance":
        return redirect(url_for("add_insurance_info"))
    elif option == "vitals":
        return redirect(url_for("add_vital_signs"))
    else:
        # Handle invalid or unexpected options
        return "Invalid option selected."


@app.route("/add_demographic_info", methods=["GET", "POST"])
def add_demographic_info():

    if request.method == "POST":
        # Retrieve user input from the form
        pat_name = request.form.get("pat_name")
        pat_sex = request.form.get("pat_sex")
        pat_birth = request.form.get("pat_birth")
        pat_address = request.form.get("pat_address")
        pat_phone = request.form.get("pat_phone")
        pat_email = request.form.get("pat_email")
        pat_em_name = request.form.get("pat_em_name")
        pat_em_relationship = request.form.get("pat_em_relationship")
        pat_em_phone = request.form.get("pat_em_phone")

        # Create a list to represent patient data
        patient_data = [
            pat_name,
            pat_sex,
            pat_birth,
            pat_address,
            pat_phone,
            pat_email,
            pat_em_name,
            pat_em_relationship,
            pat_em_phone,
        ]

        # Add the patient data list to the list of patient data
        # patient_data_list.append(patient_data)

        pat_id = get_patient_id()
        operations.insert_demographic_info(pat_id, patient_data)

        flash("Patient information added successfully", "success")
        return redirect(url_for("dashboard"))

    return render_template("demo_form.html")


@app.route("/add_insurance_info", methods=["GET", "POST"])
def add_insurance_info():
    if request.method == "POST":
        # Retrieve user input from the form
        ins_name = request.form.get("ins_name")
        ins_subscriber = request.form.get("ins_subscriber")
        ins_policy_num = request.form.get("ins_policy_num")
        pat_relationship = request.form.get("pat_relationship")

        # Assuming you have a function to get the patient ID
        pat_id = get_patient_id()

        # Create a list to represent insurance info data
        insurance_data = [
            ins_name,
            ins_subscriber,
            ins_policy_num,
            pat_relationship
        ]

        # Add the insurance data to the database
        operations.insert_insurance_info(pat_id, insurance_data)

        flash("Insurance information added successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("insurance_form.html")


@app.route("/add_vital_signs", methods=["GET", "POST"])
def add_vital_signs():
    if request.method == "POST":
        # Retrieve user input from the form
        visit_date = request.form.get("visit_date")
        blood_pressure = request.form.get("blood_pressure")
        heart_rate = request.form.get("heart_rate")
        body_temp = request.form.get("body_temp")

        # Assuming you have a function to get the patient ID
        pat_id = get_patient_id()

        # Create a list to represent vital signs data
        vital_signs_data = [
            visit_date,
            blood_pressure,
            heart_rate,
            body_temp
        ]

        # Add the vital signs data to the database
        operations.insert_patient_vitals(pat_id, vital_signs_data)

        flash("Vital signs information added successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("vitals_form.html")


@app.route("/delete_account")
def delete_account():
    # Add logic for handling account deletion
    # Redirect or render the appropriate template
    return "Delete My Account Page"

@app.route("/logout")
def logout():
    # Add logic for logging out (e.g., clearing session)
    # Redirect to the login page or any other page as needed
    return "Logged out. You can redirect to the login page here."


if __name__ == "__main__":
    app.run(debug=True)