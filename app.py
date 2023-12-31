from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, url_for, session, flash
from passlib.hash import sha256_crypt
import psycopg2
import operations
import os

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"  # Replace with a secure secret key


# TODO: For local db
# def connect_to_database():
#     return psycopg2.connect(
#         database="patients",
#         user='postgres',
#         password='Oblivion14',
#         host='localhost',
#         port='5432'
#     )

# TODO: For remote db (ElephantSQL)
def connect_to_database():
    # Extract the host from the ElephantSQL URL
    url = urlparse("postgres://hppjpzgb:9Jahd0BH-IsGSHJNmOxK75HncHLZgIdC@berry.db.elephantsql.com/hppjpzgb")
    hostname = url.hostname

    return psycopg2.connect(
        database="hppjpzgb",
        user='hppjpzgb',
        password='9Jahd0BH-IsGSHJNmOxK75HncHLZgIdC',
        host=hostname,
        port='5432'
    )


'''
    Login 
'''
@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    patient_id = is_valid_login(username, password)

    if patient_id:
        session["patient_id"] = patient_id
        return redirect(url_for("dashboard", pat_id=patient_id))
    else:
        flash("Invalid login credentials. Please try again.", "danger")
        return redirect(url_for("login_page"))



def is_valid_login(username, password):
    cursor = connect_to_database().cursor()
    cursor.execute("SELECT pat_id, password FROM login_data WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:
        patient_id, hashed_password = result
        if sha256_crypt.verify(password, hashed_password):
            return patient_id

    return None


'''
    Register new user
'''
@app.route("/create_user")
def create_user_page():
    return render_template("create_user.html")


@app.route("/register", methods=["POST"])
def register():
    new_username = request.form.get("new_username")
    new_password = request.form.get("new_password")
    new_password_2 = request.form.get("new_password_2")

    # TODO: Maybe abstract out password matching check into operations.create_user()
    if new_password != new_password_2:
        flash("Passwords do not match. Please try again.", "danger")
        return redirect(url_for("create_user_page"))
    else:
        new_user = operations.create_user(new_username, new_password)

    if new_user:
        flash("User registered successfully. Please log in.", "success")
        return redirect(url_for("login_page"))
    else:
        flash("User already exists. Please try again.", "danger")
        return redirect(url_for("create_user_page"))



'''
    Main Dashboard
'''
@app.route("/dashboard")
def dashboard():

    patient_id = session.get("patient_id")

    if patient_id is not None:
        # Get the patient_id from the session
        # pat_id = get_patient_id()

        # Get the patient's name using the patient_id
        patient_name = operations.get_patient_name(patient_id)

        if patient_name is None:
            # If no patient exists, then redirect to demographic form
            # Flash "new patient message"
            flash("New patient. Please fill out basic info to continue.", "success")
            return redirect(url_for("add_demographic_info"))

        else:
            return render_template("dashboard.html", patient_name=patient_name)
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
        return "Invalid option selected."


'''
    Adding user data from forms to database
'''
@app.route("/add_demographic_info", methods=["GET", "POST"])
def add_demographic_info():

    if request.method == "POST":
        pat_name = request.form.get("pat_name")
        pat_sex = request.form.get("pat_sex")
        pat_birth = request.form.get("pat_birth")
        pat_address = request.form.get("pat_address")
        pat_phone = request.form.get("pat_phone")
        pat_email = request.form.get("pat_email")
        pat_em_name = request.form.get("pat_em_name")
        pat_em_relationship = request.form.get("pat_em_relationship")
        pat_em_phone = request.form.get("pat_em_phone")

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

        pat_id = get_patient_id()
        operations.insert_demographic_info(pat_id, patient_data)

        flash("Patient information added successfully", "success")
        return redirect(url_for("dashboard"))

    return render_template("demo_form.html")


@app.route("/add_insurance_info", methods=["GET", "POST"])
def add_insurance_info():
    if request.method == "POST":

        ins_name = request.form.get("ins_name")
        ins_subscriber = request.form.get("ins_subscriber")
        ins_policy_num = request.form.get("ins_policy_num")
        pat_relationship = request.form.get("pat_relationship")

        pat_id = get_patient_id()

        insurance_data = [
            ins_name,
            ins_subscriber,
            ins_policy_num,
            pat_relationship
        ]

        operations.insert_insurance_info(pat_id, insurance_data)

        flash("Insurance information added successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("insurance_form.html")


@app.route("/add_vital_signs", methods=["GET", "POST"])
def add_vital_signs():
    if request.method == "POST":
        visit_date = request.form.get("visit_date")
        blood_pressure = request.form.get("blood_pressure")
        heart_rate = request.form.get("heart_rate")
        body_temp = request.form.get("body_temp")

        pat_id = get_patient_id()

        vital_signs_data = [
            visit_date,
            blood_pressure,
            heart_rate,
            body_temp
        ]

        operations.insert_patient_vitals(pat_id, vital_signs_data)

        flash("Vital signs information added successfully", "success")
        return redirect(url_for("dashboard"))
    return render_template("vitals_form.html")


'''
    Pull user data from database and display on info_display.html
'''
def get_patient_id():
    return session.get("patient_id", None)


@app.route('/display_patient_name')
def display_patient_name():
    # Get the patient_id from the session
    pat_id = get_patient_id()

    # Get the patient's name using the patient_id
    patient_name = operations.get_patient_name(pat_id)

    if patient_name is None:
        return "Patient name not found."

    return patient_name

    # Pass the patient's name to the HTML template
    # return render_template('dashboard.html', patient_name=patient_name)


@app.route('/patient_data', methods=['GET', 'POST'])
def patient_data():
    pat_id = get_patient_id()
    login_data, demo_data, insurance_data, vitals = operations.get_patient_data(pat_id)

    if login_data is None:
        return "Patient data not found."

    return render_template('info_display.html', login_data=login_data, demo_data=demo_data, insurance_data=insurance_data,
                           vitals=vitals)

'''
    Settings Options
'''
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))


@app.route("/delete_account", methods=["POST"])
def delete_account():
    if request.method == "POST":
        pat_id = get_patient_id()

        if pat_id:
            operations.delete_patient_data(pat_id)
            return redirect(url_for("login_page"))

    return "Invalid request"


@app.route("/account_deleted")
def account_deleted():
    return "Your account has been successfully deleted."


# if __name__ == "__main__":
#     app.run(debug=True)


# TODO: Don't like this as global
port = int(os.environ.get("PORT", 5000))
if __name__ == "__main__":
    # app.run(debug=True)
    # app.run()
    # app.run(debug=False)
    app.run(host="0.0.0.0", port=port)
