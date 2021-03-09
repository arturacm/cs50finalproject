# DocLog
#### Video Demo:  https://www.youtube.com/watch?v=R8cvyEp0Vxs

# Table of Contents
- [About The Project](#About-The-Project)
  - [Built With](##Built-With)
- [Getting Started](#Getting-Started)
- [Prerequisites](#Prerequisites)
- [Installation](#Installation)
- [Project’s schemes](#Projects-schemes)
- [Usage](#Usage)
- [Roadmap](#Roadmap)
- [Contributing](#Contributing)
- [License](#License)
- [Contact](#Contact)
- [Acknowledgements](#Acknowledgements)


# About The Project
This project is the last activity of Harvard's CS50 Introduction to Computer Science with David Malay. With the task that was given, we decided to make a Flask-based web application that tackles on the aspects of making an appointment with a doctor. The website is composed of a series of html templates and a python file which guide the user to register a doctor or a patient account and then treating according to each role, providing specific routes for each of their necessities. It is inspired by an Open Source Software called OpenEMS.
## Built With
This project was made possible using:
- Visual Studio Code
- Python
- Flask
- Mapbox

# Getting Started
#### Prerequisites

Using your Text Editor and terminal, install Git and Python 3.7.9 and execute the command
```
pip install venv
```



#### Installation

in order to set up a virtual python environment to install the requirements. Then, activate your venv folder, which should be inside your project root folder and run the next commands
```
Git clone https://github.com/arturacm/cs50finalproject
Pip install ‘requirements.txt’
```
Setup an account at Mapbox and navigate to Access Tokens section and create a public token, copy it and create a ‘.env’ file on the project’s root folder and set up the file as below
```
MAPBOX_ACCESS_TOKEN = * Insert copied token here * (exclude the asterisk sign)
```

Open once again your terminal and configure your Flask settings (example below assumes your terminal is a Linux WSL bash terminal, for other terminals, such as PowerShell or cmd, access Flask’s Command Line Interface Documentation:
``` 
export FLASK_APP=application:app
export FLASK_DEBUG=TRUE
Flask run
```
If you followed the configuration correctly, you should be able to open to your configured default browser the application hosted on http://127.0.0.1:5000/

# Project’s schemes
Our current project scheme can be seen as:

<p align="center">
  <img width="15%" height="100%" src="https://i.imgur.com/7XHQeSo.png">
</p>

| File Name           | Description                                                                                                           |
|:--------------------|:----------------------------------------------------------------------------------------------------------------------|
| /static             | _Folder for organizing the front-end styles, CSS and Map Marker._                                                     |
|   favicon.ico       | _Webpage tab icon_                                                                                                    |
|   marker.png        | _Map marker_                                                                                                          |
|   styles.css        | _CSS configurations_                                                                                                  |
| /templates          | _Folder containing the pages_                                                                                         |
|   apology.html      | _Renders application failures_                                                                                        |
|   appointment.html  | _Renders form to submit appointments_                                                                                 |
|   change.html       | _Renders form to change password_                                                                                     |
|   details.html      | _Renders details for a specific appointment_                                                                          |
|   find_doctors.html | _Renders map with doctors in the database_                                                                            |
|   history.html      | _Renders past appointments in tabular manner_                                                                         |
|   index.html        | _Renders future appointments in tabular manner_                                                                       |
|   layout.html       | _Flask based layout to reduce repetition of code in each template_                                                    |
|   login.html        | _Renders user login form_                                                                                             |
|   map-register.html | _Renders map to update a doctor’s location_                                                                           |
|   register.html     | _Renders a user patient or doctor registration form_                                                                  |
| .env                | _Contains MapBox API Token_                                                                                           |
| application.py      | _Contains all the necessary functions and rules for rendering all the templates and registering info to the database_ |
| database.db         | _SQL based database containing users, doctors, patients, appointments tables_                                         |
| helpers.py          | _Side application to load apology template if an error occurs_                                                        |
| requirements.txt    | _All of the Python’s packages and dependencies necessary for running the project locally._                            |
| run.py              | _Optional application that calls application.py and loads with FLASK_DEBUG on by default._                            |

# Usage

Once opened, you may create an account at register and pick a role as a patient or a doctor.

<p align="center">
  <img width="50%" height="100%" src="https://i.imgur.com/hbgIfoP.png">
</p>

After selecting the account’s role, the form will act accordingly and provide you with the necessary camps to provide for the SQL database.

The index webpage will show you your next validated appointments and upon registration should show a page which looks like the image below.

<p align="center">
  <img width="100%" height="100%" src="https://i.imgur.com/yq2j49G.png">
</p>

From there, you have, as a patient, the following fields:
- Appointment
- History
- Find Doctors
- Change Password
- Log Out

The appointment webpage will show you a simple form to submit an appointment and should look like the image below.

<p align="center">
  <img width="75%" height="100%" src="https://user-images.githubusercontent.com/73298622/110504981-793af700-80dc-11eb-90cb-36328cfcdf2c.png">
</p>


History webpage works similarly to the index webpage and shows you appointments which already happened.

<p align="center">
  <img width="75%" height="100%" src="https://user-images.githubusercontent.com/73298622/110505307-c9b25480-80dc-11eb-88d1-10c567005134.png">
</p>


Lastly, the other main functionality is a map which shows you the current list of doctors subscribed to the database.

<p align="center">
  <img width="50%" height="50%" src="https://media1.giphy.com/media/KES6iXUlz3Grt0zb0N/giphy.gif">
</p>

# Roadmap
If checked thoroughly, it can be perceived that the website is still in its development stages and it can be improved greatly by a new stylization with newer graphs, images and fonts. This should be an ever-increasing aspect of this website if opted to continue improving on it.
Other aspects should be:
- Implement fixed scheduled appointment hours;
- Implement acceptance of schedules;
- Implement a calendar interface;
- Implement a real time chat API for doctor and user;
- And many others.

# Contributing
If interested in contributing for this open source project, it can be done so by following the next steps:
1. Fork the Project
2. Create your Feature Branch (git checkout -b feature/AmazingFeature)
3. Commit your Changes (git commit -m ‘Add some AmazingFeature’)
4. Push to the Branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

# License
Distributed under the MIT License.

# Contact
Artur Moreira - [LinkedIn](www.linkedin.com/in/artur-moreira) - email: arturacm@gmail.com

Davi Leal - [LinkedIn](https://www.linkedin.com/in/davi-pinheiro-barros-leal-b62474121/) - email: davipbl@gmail.com

[Project Link](https://github.com/arturacm/cs50finalproject)

# Acknowledgements
- OpenEMS
- Flask
- Python
- David Malay from CS50
