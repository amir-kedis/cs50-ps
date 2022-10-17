import json
import os

import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)    

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    user_cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    user_cash = user_cash_db[0]["cash"]

    transctions = db.execute("SELECT symbol, SUM(shares) AS shares, price FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 1", user_id)

    shares_value = 0
    for row in transctions:
        shares_value += row["price"] * row["shares"]

    return render_template("index.html", database = transctions, cash = user_cash, shares_value=shares_value)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # symbol must be provided
        if not symbol:
            return apology("Must Enter Symbol")

        # shares must be provided
        if not shares:
            return apology("Must Enter shares")

        shares = int(shares)

        # get stock data for the symbol
        stock = lookup(symbol.upper())

        # if symbol is incorrect throw error
        if stock == None:
            return apology("No Such Symbol")

        # check shares postive number
        if shares < 1:
            return apology("shares must be a postive number")

        # get user id from sessoion
        user_id = session["user_id"]

        # get user cash
        user_cash_db = db.execute("SELECT cash FROM users WHERE id=?", user_id)
        user_cash = user_cash_db[0]["cash"]

        transiction_value = stock["price"] * shares;

        # check if user have enough money
        if user_cash < transiction_value:
            return apology("Not enough Money")

        # update user cash
        update_cash = user_cash - transiction_value;
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)

        # add the transiction to database
        date = datetime.datetime.now();

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)", user_id, stock["symbol"], shares, stock["price"], date)

        flash("Bought!")
        return redirect("/")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    user_id = session["user_id"]

    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)

    return render_template("history.html", transactions=transactions)


@app.route("/add-cash", methods=["GET", "POST"])
@login_required
def add_cash():
    """Show history of transactions"""
    if request.method == "GET":
        return render_template("add-cash.html")
    else:
        user_id = session["user_id"]

        add_cash = request.form.get("cash")

        if not add_cash:
            return apology("must enter cash")

        add_cash = int(request.form.get("cash"))

        if add_cash < 1:
            return apology("cash must be a postive number")

        # get user cash
        user_cash_db = db.execute("SELECT cash FROM users WHERE id=?", user_id)
        user_cash = user_cash_db[0]["cash"]

        updated_cash = user_cash + add_cash

        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)

        flash("Cash added!")
        return redirect("/")



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

    # if get show the form
    if request.method == "GET":
        return render_template("quote.html")

    # if form submited look up symbol
    if request.method == "POST":

        # get symbol
        symbol = request.form.get("symbol")

        # symbol must be provided
        if not symbol:
            return apology("Must Enter Symbol")

        # get stock data for the symbol
        stock = lookup(symbol.upper())

        # if symbol is incorrect throw error
        if stock == None:
            return apology("No Such Symbol")

        # send stock data back to front-end
        return render_template("quoted.html", name=stock["name"], price=stock["price"], symbol=stock["symbol"])




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # if get show the form
    if request.method == "GET":
        return render_template("register.html")

    # if form submited
    if request.method == "POST":

        # get form inputs from request
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # check that they exist and password match cofirmation
        if not username:
            return apology("Must enter a username")

        if not password:
            return apology("Must enter a password")

        if not confirmation:
            return apology("Must confirm password")

        if password != confirmation:
            return apology("Passwords Must match")

        # make a hash for password
        hash = generate_password_hash(password)

        # insert user
        try:
            new_uesr = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except:
            return apology("Username already exist")

        # store the user and redirect to homepage
        session["user_id"] = new_uesr
        return redirect("/")






@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":

        # get user id from sessoion
        user_id = session["user_id"]

        symbols = db.execute("SELECT symbol FROM transactions WHERE user_id=? GROUP BY symbol", user_id)

        return render_template("sell.html", symbols=symbols)

    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # symbol must be provided
        if not symbol:
            return apology("Must Enter Symbol")

        # shares must be provided
        if not shares:
            return apology("Must Enter shares")

        shares = int(shares)

        # get stock data for the symbol
        stock = lookup(symbol.upper())

        # if symbol is incorrect throw error
        if stock == None:
            return apology("No Such Symbol")

        # check shares postive number
        if shares < 1:
            return apology("shares must be a postive number")

        # get user id from sessoion
        user_id = session["user_id"]

        # get user cash
        user_cash_db = db.execute("SELECT cash FROM users WHERE id=?", user_id)
        user_cash = user_cash_db[0]["cash"]

        transiction_value = stock["price"] * shares;

        # SELECT SUM(shares) AS shares FROM transactions WHERE user_id=:id AND symbol = :symbol
        user_shares = db.execute("SELECT SUM(shares) AS shares FROM transactions WHERE user_id=? AND symbol=?",user_id, symbol)

        # check if user have enough shared
        if user_shares[0]["shares"] < shares:
            return apology("You Don't have enough shares")

        # update user cash
        update_cash = user_cash + transiction_value;
        db.execute("UPDATE users SET cash = ? WHERE id = ?", update_cash, user_id)

        # add the transiction to database
        date = datetime.datetime.now();

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)", user_id, stock["symbol"], (-1) * shares, stock["price"], date)

        flash("Sold!")
        return redirect("/")