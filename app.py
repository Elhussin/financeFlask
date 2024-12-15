import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, password_confiarm

# Configure application
# Initialize the Flask application and configure it to use the filesystem for sessions.
app = Flask(__name__)

# Custom filter
# Register a custom filter to format values as USD.
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# Connect the application to the SQLite database `finance.db`.
db = SQL("sqlite:///finance.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Display the user's stock portfolio or handle stock updates."""
    if request.method == "POST":
        # Handle form submission (not implemented in this snippet)
        ...
    else:
        # Retrieve user information and portfolio details
        user_data = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])
        user_name = user_data[0]["username"].upper()

        # Summarize user's stock portfolio
        summary = db.execute(
            "SELECT *, SUM(shares) FROM sell WHERE user_id = ? GROUP BY symbol",
            session["user_id"],
        )

        sum_total = 0
        for item in summary:
            if item["symbol"]:
                stock_data = lookup(item["symbol"])
                current_price = stock_data["price"]
                item["price"] = current_price
                item["total"] = current_price * item["SUM(shares)"]
                sum_total += item["total"]
                item["total"] = usd(item["total"])

        # Format financial data
        cash = usd(user_data[0]["cash"])
        wallet = usd(user_data[0]["cash"] + sum_total)
        sum_total = usd(sum_total)
        print(summary)
        # Render the portfolio template
        return render_template(
            "index.html",
            w="Welcome Mr",
            mesag=user_name,
            summary=summary,
            cash=cash,
            wallet=wallet,
        )

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Allow users to buy shares of a stock."""
    if request.method == "POST":
        # Get form inputs
        symbol = request.form.get("symbol")
        shares_num = request.form.get("shares")

        # Validate inputs
        if not symbol:
            return apology("must provide symbol", 403)
        if not shares_num:
            return apology("must provide shares_num", 403)
        symbol_value = lookup(symbol)
        if not symbol_value:
            return apology("Not valid symbol", 400)
        if not shares_num.isdigit() or int(shares_num) < 1:
            return apology("Shares not valid", 400)

        # Calculate total cost
        total_cost = symbol_value["price"] * int(shares_num)

        # Check user's available cash
        main_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )[0]["cash"]

        if total_cost > main_cash:
            return apology("Insufficient funds", 403)

        # Record the transaction in the database
        db.execute(
            """
            INSERT INTO sell (symbol, symbol_name, shares, price, total, stat, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            symbol_value["symbol"],
            symbol_value["name"],
            int(shares_num),
            symbol_value["price"],
            total_cost,
            "buy",
            session["user_id"],
        )

        # Update user's cash balance
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?",
            main_cash - total_cost,
            session["user_id"],
        )

        # Retrieve updated portfolio and financial data
        all_buys = db.execute(
            "SELECT *, SUM(shares), SUM(total) FROM sell WHERE user_id = ? GROUP BY symbol",
            session["user_id"],
        )
        new_cash = usd(db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"])
        total_wallet = usd(sum(row["SUM(total)"] for row in all_buys))

        # Format prices in USD
        for record in all_buys:
            record["price"] = usd(record["price"])

        return render_template(
            "bought.html",
            meesag="Bought",
            total_sell=all_buys,
            new_cash=new_cash,
            total_wallet=total_wallet,
        )

    else:
        # Render the buy form
        return render_template("buy.html")

@app.route("/history")
@login_required
def history():
    """Display a history of all user transactions."""
    transactions = db.execute(
        "SELECT * FROM sell WHERE user_id = ?", session["user_id"]
    )
    print(transactions)
    return render_template("history.html", history=transactions)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log in an existing user."""
    # Clear any existing user session
    session.clear()

    if request.method == "POST":
        # Validate form inputs
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            return apology("Missing username or password", 403)

        # Verify user credentials
        user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(user) != 1 or not check_password_hash(user[0]["hash"], password):
            return apology("Invalid username or password", 403)

        # Log in the user
        session["user_id"] = user[0]["id"]
        return redirect("/")

    else:
        # Render login form
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log out the current user."""
    session.clear()
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Retrieve stock quotes."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Enter symbol", 400)
        stock_data = lookup(symbol)
        if not stock_data:
            return apology("Invalid symbol", 400)
        return render_template(
            "quoted.html", symbol_value=stock_data, price=usd(stock_data["price"])
        )
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""
    if request.method == "POST":
        password = request.form.get("password")
        confiarm_password = request.form.get("confirmation")
        username = request.form.get("username")

        # Ensure required fields are provided
        if not username:
            return apology("must provide username", 400)
        elif not password:
            return apology("must provide password", 400)
        elif not confiarm_password:
            return apology(" must confirm password", 400)

        # Check if passwords match
        if password != confiarm_password:
            return apology("passwords do not match", 400)

        # Check if username already exists
        duplicate = db.execute("select * from users where username = ?", username)
        if len(duplicate) >= 1:
            return apology("Username is already taken", 400)

        # Hash the password and insert the user into the database
        password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", username, password)

        return apology("Registration successful", 200)

    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell stocks from the user's portfolio."""
    own_iteam = db.execute(
        "select * from sell where user_id=? GROUP BY symbol", session["user_id"]
    )

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Ensure symbol and shares are provided
        if not symbol:
            return apology("Select Symbol", 400)
        if not shares:
            return apology("Add Shares", 400)

        symbol_check = lookup(symbol)
        if not symbol_check:
            return apology("Not valid symbol", 400)

        # Ensure shares is a valid number
        if not shares.isdigit():
            return apology("Shares Not valid", 400)

        if int(shares) < 1:
            return apology("Shares not valid", 400)

        # Check if user has enough shares to sell
        sum_shares = db.execute(
            "select sum(shares) from sell where user_id=? and symbol=? GROUP BY symbol",
            session["user_id"],
            symbol,
        )

        if sum_shares[0]["sum(shares)"] < int(shares):
            return apology("Not enough shares", 400)

        # Calculate total sale value
        total_sell = symbol_check["price"] * int(shares)
        total_sold = -total_sell
        shares = -int(shares)

        # Insert the sale transaction
        db.execute(
            "INSERT INTO sell (symbol, symbol_name, shares, price, total, stat, user_id) VALUES (?, ?, ?, ?, ?, ?, ?);",
            symbol_check["symbol"],
            symbol_check["name"],
            shares,
            symbol_check["price"],
            total_sold,
            "sell",
            session["user_id"],
        )

        # Update user's cash balance after selling
        main_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )
        cash_update = main_cash[0]["cash"] + total_sell
        db.execute(
            "UPDATE users SET cash = ? WHERE id = ?", cash_update, session["user_id"]
        )

        return redirect("/")

    return render_template("sell.html", own_iteam=own_iteam)

@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    """Allow users to update their profile details."""
    error_meage = ""  # Initialize error message variable
    # Fetch user details from the database
    user_datieal = db.execute("select * from users where id=?", session["user_id"])
    
    if request.method == "POST":
        # Get the user inputs from the form
        password = request.form.get("password")
        user_name = request.form.get("username")
        email = request.form.get("email")

        # Check if username is provided
        if not user_name:
            error_meage = "User Name Not Add"
            return render_template(
                "update.html", error_maseg=error_meage, user_datieal=user_datieal
            )

        # Ensure the username length is between 5 and 15 characters
        if len(user_name) < 5 or len(user_name) > 15:
            return render_template(
                "update.html",
                error_maseg="User name must be at least 5 characters and no more than 15 characters",
                user_datieal=user_datieal,
            )

        # Check if email is provided
        if not email:
            error_meage = "Email Not Add"
            return render_template(
                "update.html", error_maseg=error_meage, user_datieal=user_datieal
            )

        # Check if password is provided
        if not password:
            error_meage = "Password Not Add"
            return render_template(
                "update.html", error_maseg=error_meage, user_datieal=user_datieal
            )

        # Validate the password
        check_paswoed = password_confiarm(password)
        if check_paswoed != "True":
            return render_template(
                "update.html", error_maseg=check_paswoed, user_datieal=user_datieal
            )

        # Check if the username is already taken
        username_duplicate = db.execute(
            "select * from users where username = ?", user_name
        )
        if len(username_duplicate) >= 1:
            return render_template(
                "update.html", error_maseg="User name is already taken", user_datieal=user_datieal
            )

        # Hash the new password
        password = generate_password_hash(password)
        
        # Update the user's details in the database
        db.execute(
            "UPDATE users SET email = ?, username = ?, hash = ? WHERE id = ? ",
            email,
            user_name,
            password,
            session["user_id"],
        )

        # Fetch updated user details from the database
        user_datieal = db.execute("select * from users where id=?", session["user_id"])

        # Return a success message and updated user details
        return render_template(
            "update.html", error_maseg="Profile updated successfully", user_datieal=user_datieal
        )
    else:
        # If the request method is GET, render the update page with the user's details
        return render_template("update.html", user_datieal=user_datieal)
