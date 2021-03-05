import os
import time
import numpy
import requests

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, render_template_string
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from geojson import Point, Feature
from dotenv import load_dotenv
load_dotenv()

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
mapbox_access_token = os.environ.get("MAPBOX_ACCESS_TOKEN")
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
        appointments = db.execute("SELECT appointments.id AS appointments_id, doctors.id AS doctors_id, * FROM appointments JOIN doctors ON doctors_id = appointments.doctor_id WHERE patient_id = ? AND TIME >= datetime('now') ORDER BY TIME DESC", patientDb["id"])
    elif (role == "doctor"):
        doctorDb = db.execute("SELECT * FROM doctors WHERE user_id = ?", session["user_id"])[0]
        appointments = db.execute("SELECT appointments.id AS appointments_id, doctors.id AS doctors_id, patients.id AS patients_id, patients.name AS patients_name, * FROM appointments LEFT JOIN doctors ON appointments.doctor_id = doctors_id LEFT JOIN patients ON appointments.patient_id = patients_id WHERE doctor_id = ? AND TIME >= datetime('now') ORDER BY TIME DESC", doctorDb["id"])
    return render_template("index.html", role=role, appointments=appointments)


@app.route("/history")
@login_required
def history():
    role = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["role"]
    
    if (role == "patient"):
        patientDb = db.execute("SELECT * FROM patients WHERE user_id = ?", session["user_id"])[0]
        appointments = db.execute("SELECT appointments.id AS appointments_id, doctors.id AS doctors_id, * FROM appointments JOIN doctors ON doctors_id = appointments.doctor_id WHERE patient_id = ? AND TIME < datetime('now') ORDER BY TIME DESC", patientDb["id"])
    elif (role == "doctor"):
        doctorDb = db.execute("SELECT * FROM doctors WHERE user_id = ?", session["user_id"])[0]
        appointments = db.execute("SELECT appointments.id AS appointments_id, doctors.id AS doctors_id, patients.id AS patients_id, patients.name AS patients_name, * FROM appointments LEFT JOIN doctors ON appointments.doctor_id = doctors_id LEFT JOIN patients ON appointments.patient_id = patients_id WHERE doctor_id = ? AND TIME < datetime('now') ORDER BY TIME DESC", doctorDb["id"])
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
        role = "patient"
        return render_template("login.html", role=role)


@app.route("/appointment", methods=["GET", "POST"])
@login_required
def appointment():
    role = db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])[0]["role"]
    #if request.method == "POST":

    # look for data from form POST (won't be present when we are invoked with GET initially)
    #selected_spe = request.form['car_vendor'] if 'car_vendor' in request.form else None
    if request.method == "POST":
        role = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["role"]
        if (role == "doctor"):
            return apology("It is only possible to register an appointment with a patient account")
        patientDb = db.execute("SELECT id, user_id, name, occupation FROM patients WHERE user_id = ?", session["user_id"])[0]
        date = request.form.get("schedule")
        hour = request.form.get("appt")
        specialization = request.form.get("specialty")
        doctor = request.form.get("doctor")
        patientLog = request.form.get("log")
        stringDate = date + " " + hour
        
        #Check if another appointment is already scheduled
        count = db.execute("SELECT COUNT(TIME) FROM appointments WHERE doctor_id = ? AND TIME > datetime('now')", doctor)[0]["COUNT(TIME)"]
        if count > 0:
            dateCheck = [count, ""]
            for i in range(count):
                dateCheck = db.execute("SELECT TIME FROM appointments WHERE doctor_id = ? AND TIME > datetime('now')", doctor)[i]["TIME"]
                conditionCheck = dateCheck.split(" ")
                if conditionCheck[0] == date:
                    time = int(conditionCheck[1].split(":")[0]) * 60 + int(conditionCheck[1].split(":")[1])
                    if abs(time - (int(hour.split(":")[0]) * 60 + int(hour.split(":")[1]))) < 30:
                        return apology("This doctor cannot schedule an appointment by this time")

        #Check if time has already passed
        stringDate = datetime.strptime(stringDate, "%Y-%m-%d %H:%M")
        now = datetime.now()
        if stringDate < now:
            return apology("You cannot schedule an appointment for this date and hour")

        db.execute("INSERT INTO appointments(patient_id, doctor_id, type_appointment, TIME, patient_log) VALUES (?, ?, ?, ?, ?)", patientDb["id"], doctor, specialization, stringDate, patientLog)
        message="Appointment successfully scheduled"
        
        return redirect("/")

    else:
        doctorDb = db.execute("SELECT id, name, speciality FROM doctors")
        """
        spe = {}
        for rowSpecialty in SPECIALTY:
            testName = db.execute("SELECT name FROM doctors WHERE speciality = ?", rowSpecialty)
            count = db.execute("SELECT COUNT(name) FROM doctors WHERE speciality = ?", rowSpecialty)[0]["COUNT(name)"]
            if count != 0:
                names = [count, ""]
                for i in range(count):
                    names[i] = testName[i]["name"]
            else:
                names = []
            spe.update({rowSpecialty : names})
            """
        
        #return render_template("appointment.html", spe=spe)
        return render_template("appointment.html", doctorDb=doctorDb, SPECIALTY=SPECIALTY, role=role)
         

@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    role = db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])[0]["role"]
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
    return render_template("change.html",role=role)


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

        #Error Checking
        if not request.form.get("username"):
                return apology("must provide a username", 400)

        #Remember which user has logged in
        username = request.form.get("username")
        testUsername = db.execute("SELECT username FROM users WHERE username = ?", username)

        password = str(request.form.get("password"))
        passwordDuplicate = str(request.form.get("confirmation"))

        if len(testUsername) > 0:
            if username == testUsername[0]["username"]:
                return apology("There is already this username in our database")

        if not request.form.get("role"):
                return apology("must provide a role", 400)

        if len(password) == 0 or len(passwordDuplicate) == 0:
            return apology("Your password is invalid.")

        if password != passwordDuplicate:
            return apology("Your passwords do not match :(")

        role = request.form.get("role")

        #patient error checking
        if role == "patient":
            if not request.form.get("pname"):
                return apology("must provide a name", 400)
            elif not request.form.get("birth"):
                return apology("must provide birth day", 400)
            elif not request.form.get("occupation"):
                return apology("must provide occupation", 400)

        #doctor error checking
        elif role == "doctor":
            if not request.form.get("dname"):
                return apology("must provide a name", 400)
            elif not request.form.get("menumber"):
                return apology("must provide menumber", 400)
            elif not request.form.get("specialty"):
                return apology("must provide speciality", 400)

        else:
            return apology("Something wrong is not right")


        hashed = str(generate_password_hash(request.form.get("password")))

        db.execute("INSERT INTO users(username, hash, role) VALUES (?, ?, ?)", username, hashed, role)
        rows = db.execute("SELECT * FROM users WHERE username = ?",username)
        user_id = rows[0]["id"]

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
            specialty = request.form.get("specialty")

            if (specialty not in SPECIALTY):
                return apology("Enter a valid specialty")

            db.execute("INSERT INTO doctors(username, user_id, name, menumber, speciality) VALUES (?, ?, ?, ?, ?)", username, user_id, name, menumber, specialty)
        else:
            return apology("Something wrong is not right")


        #remember the session
        session["user_id"] = user_id

        return redirect("/")
        # TODO: Add the user's entry into the database
    return render_template("register.html", specialty=SPECIALTY)


@app.route("/details", methods=["GET", "POST"])
@login_required
def details():
   role = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["role"]
   apptId = request.form.get("appointment")
   appointments = db.execute("SELECT appointments.id AS appointments_id, doctors.id AS doctors_id, doctors.name AS doctors_name, patients.id AS patients_id, patients.name AS patients_name, * FROM appointments LEFT JOIN patients ON patients_id = appointments.patient_id LEFT JOIN doctors ON doctors_id = appointments.doctor_id WHERE appointments_id = ?", apptId)
   return render_template("details.html", appointments=appointments, role=role)

#MAP SECTION OF CODE

@app.route("/map-register", methods=["GET", "POST"])
@login_required
def map_register():
    role = db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])[0]["role"]
    if (role=="doctor"):
        if request.method == "POST":
            newLongitude = request.form.get("Longitude")
            newLatitude = request.form.get("Latitude")
            db.execute("UPDATE doctors SET longitude = ?, latitude = ? WHERE user_id = ?", newLongitude, newLatitude, session["user_id"])
            return redirect("/")
        else:
            role = db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])[0]["role"]
            return render_template("map-register.html",role=role, mapbox_access_token=mapbox_access_token)
    else:
        return apology("It looks like this section is not meant for you!")

ROUTE = db.execute("SELECT latitude, longitude, name, speciality FROM doctors")

# Mapbox driving direction API call
ROUTE_URL = "https://api.mapbox.com/directions/v5/mapbox/driving/{0}.json?access_token={1}&overview=full&geometries=geojson"

def create_route_url():
    # Create a string with all the geo coordinates
    lat_longs = ";".join(["{0},{1}".format(point["longitude"], point["latitude"]) for point in ROUTE])
    # Create a url with the geo coordinates and access token
    url = ROUTE_URL.format(lat_longs, mapbox_access_token)
    return url

def get_route_data():
    # Get the route url
    route_url = create_route_url()
    # Perform a GET request to the route API
    result = requests.get(route_url)
    # Convert the return value to JSON
    data = result.json()

    # Create a geo json object from the routing data
    geometry = data["routes"][0]["geometry"]
    route_data = Feature(geometry = geometry, properties = {})

    return route_data

def create_stop_locations_details():
    stop_locations = []
    for location in ROUTE:
        # Create a geojson object for stop location
        point = Point([location['longitude'], location['latitude']])
        properties = {
            'title': location['name'],
            'icon': 'campsite',
            'marker-color': '#3bb2d0',
            'marker-symbol': len(stop_locations) + 1,
            'specialty' : location['speciality']
         }
        feature = Feature(geometry = point, properties = properties)
        stop_locations.append(feature)
    return stop_locations


@app.route('/find-doctors',methods=['GET','POST'])
@login_required
def my_maps():
    role = db.execute("SELECT role FROM users WHERE id = ?", session["user_id"])[0]["role"]
    route_data = get_route_data()
    stop_locations = create_stop_locations_details()

    return render_template('find_doctors.html', mapbox_access_token=mapbox_access_token, stop_locations = stop_locations, route_data=route_data, role=role)


#END OF MAP SECTION

#BEGINNING OF TEST SECTION FOR DEPENDENT SELECTION
"""
@app.route('/dependent', methods=['POST', 'GET'])
def dependent():
    #cars = {'Chevrolet':['Volt','Malibu','Camry'],'Toyota':['Yaris','Corolla'],'KIA':['Cerato','Rio']}
    cars = {}
    for rowSpecialty in SPECIALTY:
        testName = db.execute("SELECT name FROM doctors WHERE speciality = ?", rowSpecialty)
        count = db.execute("SELECT COUNT(name) FROM doctors WHERE speciality = ?", rowSpecialty)[0]["COUNT(name)"]
        if count != 0:
            names = [count, ""]
            for i in range(count):
                names[i] = testName[i]["name"]
        else:
            names = []
            
        cars.update({rowSpecialty : names})
    # look for data from form POST (won't be present when we are invoked with GET initially)
    selected_car = request.form['car_vendor'] if 'car_vendor' in request.form else None
    if not selected_car or selected_car not in cars:
        selected_car = None
        selected_model = None
    else:
        selected_model = request.form['car_model'] if 'car_model' in request.form else None
        # This is an alternative to unselecting the car model whenever a new car vendor is selected.
        # Instead, we just check whether the selected model belongs to the selected car vendor or not:
        if selected_model and selected_model not in cars[selected_car]:
            selected_model = None
    # Use a string template for demonstration purposes:
    return render_template_string("
<!DOCTYPE html>
<html>
<head>
<title>Flask Demo</title>
<meta name="viewport" content="width=device-width, height=device-height, initial-scale=1.0, minimum-scale=1.0">
</head>
<body>
<h2>Select Car</h2>
<form name="f" method="post">
  <table>
    <tr>
      <th>Make</th>
    <th>Model</th>
    </tr>
    <tr>
      <td>
        <select name="car_vendor" id="car_vendor" onchange="document.f.submit();">
{% if not selected_car %}
          <option value=''>-- Select a Make --</option>
{% endif %}
{% for car in cars.keys() %}
          <option value="{{ car }}" {% if car == selected_car %}selected="selected"{% endif %}>{{ car }}</option>
{% endfor %}
        </select>
      </td>
      <td>
{% if selected_car %}
        <select name="car_model" id="car_model" onchange="document.f.submit();">
  {% if not selected_model %}
          <option value=''>-- Select a Model --</option>
  {% endif %}
  {% for model in cars[selected_car] %}
          <option value="{{ model }}" {% if model == selected_model %}selected="selected"{% endif %}>{{ model }}</option>
  {% endfor %}
        </select>
{% endif %}
      </td>
    </tr>
  </table>
</form>

{% if selected_car and selected_model %}
<p style="color: red;">Both make and model have been selected: {{ selected_car }} and {{ selected_model }}.</p>
{% endif %}
</body>
</html>
", cars=cars, selected_car=selected_car, selected_model=selected_model)
"""

#END OF DEPENDENT SELECTION

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
