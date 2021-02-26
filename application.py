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


# Make sure API key is set
"""
if not os.environ.get("API_KEY"):
   raise RuntimeError("API_KEY not set")
"""

@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    """
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    balance = float(db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"])
    count = db.execute("SELECT COUNT(DISTINCT symbol) FROM history WHERE username = ?", username)[0]["COUNT(DISTINCT symbol)"]
    if count == 0:
        shares = ""
        values = ""
        portfolio = ""
        symbols = ""
        total = balance
    else:
        symbols = []
        shares = []
        values = []
        portfolio = []
        for i in range(count):
            portfolioI = db.execute("SELECT DISTINCT symbol FROM history WHERE username=?", username)[i]["symbol"]
            portfolio.append(portfolioI)
            symbolsI = lookup(portfolio[i])
            symbols.append(symbolsI)
            sharesI = db.execute("SELECT SUM(shares) FROM history WHERE username=? AND symbol=?",
                                 username, portfolio[i])[0]["SUM(shares)"]
            shares.append(sharesI)
            valuesI = float(shares[i]) * float(symbolsI["price"])
            values.append(valuesI)
        total = balance + sum(values)
    return render_template("index.html", balance=balance, shares=shares, values=values, symbols=symbols, portfolio=portfolio, count=count, total=total, username=username)
    """
    return render_template("index.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    """
    INTEGERS = []
    for i in range(999):
        index = float(i + 1)
        INTEGERS.append(index)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if symbol == "":
            return apology("It looks like you didn't insert a symbol. Please insert one.")
        shares = request.form.get("shares")
        if not shares.isnumeric():
            return apology("Please insert a number.")
        shares = float(shares)
        if shares not in INTEGERS or shares < 0 or not shares:
            return apology("Please insert a positive integer number.")
        shares = int(shares)
        result = lookup(symbol)
        if not result:
            return apology("There is currently no match for this quote!")
        balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        balance = balance[0]["cash"]
        value = float(shares * result["price"])
        if balance < value:
            return apology("It looks like you do not have enough funds for this transaction")
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])
        username = username[0]["username"]
        transactionTime = time.strftime('%A %B, %d %Y %H:%M:%S')
        db.execute("INSERT INTO history(username, shares, symbol, value, time) VALUES (?, ?, ?, ?, ?)",
                   username, shares, symbol, value, transactionTime)
        historyId = db.execute("SELECT id FROM history WHERE username = ? AND time = ?", username, transactionTime)
        historyId = historyId[0]["id"]
        newbalance = balance - value
        db.execute("UPDATE history SET shares = ? WHERE id = ?", shares, historyId)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", newbalance, session["user_id"])
        return render_template("buying.html", result=result, username=username, value=value, transactionTime=transactionTime, shares=shares, newbalance=newbalance)

    return render_template("buy.html")
"""

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    """
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    history = db.execute("SELECT * FROM history WHERE username = ?", username)

    return render_template("history.html", history=history)
"""

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
    if request.method == "POST":
        date = request.form.get("schedule")
        hour = request.form.get("appt")
        specialization = request.form.get("specialization")
        doctor = request.form.get("doctor")
        log = request.form.get("log")
        stringDate = date + " " + hour
        stringDate = datetime.strptime(stringDate, "%Y-%m-%d %H:%M")
        username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        #TO-DO: If schedule is already booked, suggest other appointments.
        db.execute("INSERT INTO appointments(username, doctor, type_appointment, TIME, log) VALUES (?, ?, ?, ?, ?)", username, doctor, specialization, stringDate, log)
        return render_template("appointment.html")
    else:
         return render_template("appointment.html")

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    """Get stock quote."""

    """
    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("It looks like you didn't insert a quote. Please insert one.")
        result = lookup(symbol)
        if not result:
            return apology("There is currently no match for this quote!")
        return render_template("quoted.html", result=result, symbol=symbol)

    return render_template("quote.html")
    """


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        
        username = request.form.get("username")
        if not request.form.get("username"):
                return apology("must provide a username", 400)

        testUsername = db.execute("SELECT username FROM users WHERE username = ?", username)

        if len(testUsername) > 0:
            if username == testUsername[0]["username"]:
                return apology("There is already this username in our database")
                
        password = str(request.form.get("password"))
        passwordDuplicate = str(request.form.get("confirmation"))


        if not request.form.get("role"):
                return apology("must provide a role", 400)

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

        #patient registration
        if role == "patient":
            if not request.form.get("pname"):
                return apology("must provide a name", 400)
            elif not request.form.get("birth"):
                return apology("must provide birth day", 400)
            elif not request.form.get("occupation"):
                return apology("must provide occupation", 400)

            name = request.form.get("pname")
            birth = request.form.get("birth")
            occupation = request.form.get("occupation")
            db.execute("INSERT INTO patients(username, user_id, name, birth, occupation) VALUES (?, ?, ?, ?, ?)", username, user_id, name, birth, occupation)

        #doctor registration
        elif role == "doctor":
            if not request.form.get("dname"):
                return apology("must provide a name", 400)
            elif not request.form.get("menumber"):
                return apology("must provide menumber", 400)
            elif not request.form.get("speciality"):
                return apology("must provide speciality", 400)

            name = request.form.get("dname")
            menumber = request.form.get("menumber")
            speciality = request.form.get("speciality")

            db.execute("INSERT INTO doctors(username, user_id, name, menumber, speciality) VALUES (?, ?, ?, ?, ?)", username, user_id, name, menumber, speciality)
        else:
            return apology("Something wrong is not right")

        #remember the session
        session["user_id"] = user_id

        return redirect("/")
        # TODO: Add the user's entry into the database
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    """
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    portfolio = db.execute("SELECT DISTINCT symbol FROM history WHERE username = ?", username)
    count = db.execute("SELECT COUNT(DISTINCT symbol) FROM history WHERE username = ?", username)[0]["COUNT(DISTINCT symbol)"]
    symbols = [count, ""]
    for i in range(count):
        symbols[i] = lookup(portfolio[i]["symbol"])
    symbols = list(symbols)

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        if symbol == "":
            return apology("It looks like you didn't insert a symbol. Please insert one.")
        if shares < 0:
            return apology("You submitted a not accepted amount of shares")
        sumShares = db.execute(
            "SELECT SUM(shares) FROM history WHERE username = ? AND symbol = ? GROUP BY symbol HAVING shares > 0", username, symbol)[0]["SUM(shares)"]
        if shares > sumShares:
            return apology("You don't have enough shares to sell")
        balance = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        balance = balance[0]["cash"]
        value = float(shares * lookup(symbol)["price"])
        transactionTime = time.strftime('%A %B, %d %Y %H:%M:%S')
        db.execute("INSERT INTO history(username, shares, symbol, value, time) VALUES (?, ?, ?, ?, ?)",
                   username, shares, symbol, value, transactionTime)
        historyId = db.execute("SELECT id FROM history WHERE username = ? AND time = ?", username, transactionTime)
        historyId = historyId[0]["id"]
        shares = 0 - shares
        db.execute("UPDATE history SET shares = ? WHERE id = ?", shares, historyId)
        newbalance = balance + value
        db.execute("UPDATE users SET cash = ? WHERE id = ?", newbalance, session["user_id"])
        shares = 0 - shares
        result = lookup(symbol)
        return render_template("selling.html", symbols=symbols, username=username, value=value, transactionTime=transactionTime, shares=shares, result=result, portfolio=portfolio, newbalance=newbalance)

    return render_template("sell.html", portfolio=portfolio)
"""

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
