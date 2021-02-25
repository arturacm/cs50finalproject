import os
import time
import numpy


from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

#from helpers import apology, login_required, lookup, usd
from helpers import apology, login_required, usd


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")

# Setting accepted Doctors' Specialties
SPECIALTY = {"Physician", "Pediatrician", "Geriatric medicine", "Allergist", "Dermatologist", "Infectologist", "Ophtalmologist", "Obstetrician", "Gynecologist", "Cardiologist"} 

# Make sure API key is set
"""
if not os.environ.get("API_KEY"):
   raise RuntimeError("API_KEY not set")
"""

@app.route("/")
@login_required
def index():
    role = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["role"]
    
    if (role == "patient"):
        patientDb = db.execute("SELECT * FROM patients WHERE user_id = ?", session["user_id"])[0]
        appointments = db.execute("SELECT * FROM appointments JOIN doctors ON doctors.id = appointments.doctor_id WHERE patient_id = ? AND TIME >= datetime('now') ORDER BY TIME DESC", patientDb["id"])
    elif (role == "doctor"):
        doctorDb = db.execute("SELECT * FROM doctors WHERE user_id = ?", session["user_id"])[0]
        appointments = db.execute("SELECT * FROM appointments LEFT JOIN doctors ON appointments.doctor_id = doctors.id LEFT JOIN patients ON appointments.patient_id = patients.id WHERE doctor_id = ? AND TIME >= datetime('now') ORDER BY TIME DESC", doctorDb["id"])
    return render_template("index.html", role=role, appointments=appointments)


@app.route("/history")
@login_required
def history():
    role = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["role"]
    
    if (role == "patient"):
        patientDb = db.execute("SELECT * FROM patients WHERE user_id = ?", session["user_id"])[0]
        appointments = db.execute("SELECT * FROM appointments JOIN doctors ON doctors.id = appointments.doctor_id WHERE patient_id = ? AND TIME < datetime('now') ORDER BY TIME DESC", patientDb["id"])
    elif (role == "doctor"):
        doctorDb = db.execute("SELECT * FROM doctors WHERE user_id = ?", session["user_id"])[0]
        appointments = db.execute("SELECT * FROM appointments LEFT JOIN doctors ON appointments.doctor_id = doctors.id LEFT JOIN patients ON appointments.patient_id = patients.id WHERE doctor_id = ? AND TIME < datetime('now') ORDER BY TIME DESC", doctorDb["id"])
    return render_template("history.html", role=role, appointments=appointments)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():
    doctorDb = db.execute("SELECT id, name, speciality FROM doctors")
    patientDb = db.execute("SELECT id, user_id, name, occupation FROM patients WHERE user_id = ?", session["user_id"])[0]
    if request.method == "POST":
        date = request.form.get("schedule")
        hour = request.form.get("appt")
        specialization = request.form.get("specialty")
        doctor = request.form.get("doctor")
        patientLog = request.form.get("log")
        stringDate = date + " " + hour
        #TO-DO: If schedule is already booked, suggest other appointments.
        checkVacancy = db.execute("SELECT TIME FROM appointments WHERE doctor_id = ?", doctor)
        for row in checkVacancy["TIME"]:
            if (stringDate - row > -1 or stringDate - row < 1):
                print(stringDate - row)
        stringDate = datetime.strptime(stringDate, "%Y-%m-%d %H:%M")

        db.execute("INSERT INTO appointments(patient_id, doctor_id, type_appointment, TIME, patient_log) VALUES (?, ?, ?, ?, ?)", patientDb["id"], doctor, specialization, stringDate, patientLog)
        message="Appointment successfully scheduled"
        return render_template("appointment.html", message=message)
    else:
         return render_template("appointment.html", specialty=SPECIALTY, doctorDb=doctorDb)

@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)

        elif not request.form.get("password") or not request.form.get("newPassword") or not request.form.get("confirmation") or request.form.get("newPassword") != request.form.get("confirmation"):
            return apology("complete all password fields")

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        hashed = str(generate_password_hash(request.form.get("newPassword")))
        db.execute("UPDATE users SET hash = ? WHERE username = ?", hashed, request.form.get("username"))

        return redirect("/")
    return render_template("change.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        if len(username) == 0:
            return apology("It looks like you didn't insert a valid username.")
        testUsername = db.execute("SELECT username FROM users WHERE username = ?", username)
        if len(testUsername) > 0:
            if username == testUsername[0]["username"]:
                return apology("There is already this username in our database")
        password = str(request.form.get("password"))
        passwordDuplicate = str(request.form.get("confirmation"))
        role = request.form.get("role")
        if len(password) == 0 or len(passwordDuplicate) == 0:
            return apology("Your password is invalid.")

        if password != passwordDuplicate:
            return apology("Your passwords do not match :(")


        hashed = str(generate_password_hash(request.form.get("password")))
        db.execute("INSERT INTO users(username, hash, role) VALUES (?, ?, ?)", username, hashed, role)

        #Remember which user has logged in

        rows = db.execute("SELECT * FROM users WHERE username = ?",username)
        user_id = rows[0]["id"]

        print(user_id)

        #patient registration
        if role == "patient":
            name = request.form.get("pname")
            birth = request.form.get("birth")
            occupation = request.form.get("occupation")
            db.execute("INSERT INTO patients(username, user_id, name, birth, occupation) VALUES (?, ?, ?, ?, ?)", username, user_id, name, birth, occupation)

        #doctor registration
        elif role == "doctor":
            name = request.form.get("dname")
            menumber = request.form.get("menumber")
            speciality = request.form.get("specialty")
            #if (speciality not in SPECIALTY):
            #    return apology("Enter a valid specialty")
            db.execute("INSERT INTO doctors(username, user_id, name, menumber, speciality) VALUES (?, ?, ?, ?, ?)", username, user_id, name, menumber, speciality)
        else:
            return apology("Something wrong is not right")

        #remember the session
        session["user_id"] = user_id

        return redirect("/")
        # TODO: Add the user's entry into the database
    return render_template("register.html", specialty=SPECIALTY)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
