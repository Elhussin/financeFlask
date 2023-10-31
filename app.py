import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, password_confiarm

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        ...
    else:
        """Show portfolio of stocks"""
        name = db.execute("select * from users where id=?", session["user_id"])

        user_name = name[0]["username"].upper()

        summary = db.execute(
            "SELECT *,sum(shares) FROM sell where   user_id = ?  GROUP BY symbol",
            session["user_id"],
        )
        sum_total = 0
        for iteam in summary:
            if iteam["symbol"]:
                symbol = lookup(iteam["symbol"])

                symbol_pric = symbol["price"]
                iteam["price"] = symbol_pric
                iteam["total"] = symbol_pric * iteam["sum(shares)"]
                sum_total += iteam["total"]
                iteam["total"] = usd(iteam["total"])

        cash = usd(name[0]["cash"])
        wallet = usd(name[0]["cash"] + sum_total)
        sum_total = usd(sum_total)

        return render_template(
            "index.html",
            w="Welcom MR",
            mesag=user_name,
            summary=summary,
            cash=cash,
            wallet=wallet,
        )


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares_num = request.form.get("shares")
        if not symbol:
            return apology("must provide symbol", 403)
        if not shares_num:
            return apology("must provide shares_num", 403)
        symbol_value = lookup(symbol)
        if not symbol_value:
            return apology("Not valid symbol", 400)
        # if int(shares_num)

        if not shares_num.isdigit():
            return apology("shares Not valid ", 400)

        if int(shares_num) < 1:
            return apology("S shares not valid", 400)
        # to callcolet all amount expend to bay
        tota_cost = symbol_value["price"] * int(shares_num)
        # sheck main cash in the  wallt
        main_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )

        # confiarm wallet  amount with =  totat buy
        if tota_cost > main_cash[0]["cash"]:
            return apology("cash not inf", 403)
        #  insert transicitan in systeam
        db.execute(
            "INSERT INTO sell (symbol ,symbol_name,shares,price,total,stat,user_id)VALUES (?,?,?,?,?,?,?);",
            symbol_value["symbol"],
            symbol_value["name"],
            int(shares_num),
            symbol_value["price"],
            tota_cost,
            "buy",
            session["user_id"],
        )
        #  updat wealt amount
        cash_update = main_cash[0]["cash"] - tota_cost
        n = db.execute(
            "UPDATE users SET cash = ? where id = ? ", cash_update, session["user_id"]
        )

        # select total shares for each itaem and total sympoly bought and total amount expend
        all_bay = db.execute(
            "SELECT *,sum(shares),sum (total) FROM sell where   user_id = ?  GROUP BY symbol",
            session["user_id"],
        )
        #
        # get welat balnce
        new_cash = db.execute("select cash from users where id=?", session["user_id"])
        #  schek  total amount for sympoel
        many_expend = db.execute(
            "select sum(total)  from sell  where  user_id=?", session["user_id"]
        )
        # print(new_cash)
        total_walet = many_expend[0]["sum(total)"] + new_cash[0]["cash"]
        # transfer to usd fromat
        new_cash = usd(new_cash[0]["cash"])
        total_walet = usd(total_walet)
        # updat pric with usd
        # updat pric with usd
        for date in all_bay:
            if date["price"]:
                date["price"] = usd(date["price"])
            if date["total"]:
                date["sum (total)"] = usd(date["sum (total)"])
        stat = "Bought"

        return render_template(
            "bought.html",
            meesag=stat,
            total_sell=all_bay,
            new_cash=new_cash,
            total_walet=total_walet,
        )
    else:
        return render_template("buy.html")
    # return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # select total shares for each itaem and total sympoly bought and total amount expend
    hisory = db.execute(
        "SELECT *FROM sell where   user_id = ?",
        session["user_id"],
    )
    return render_template("history.html", hisory=hisory)


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
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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
    if request.method == "POST":
        """Get stock quote."""
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Enter symbol", 400)
        #    return lookup(symbol)
        symbol_value = lookup(symbol)
        print("s", symbol_value)
        if not symbol_value:
            return apology("invilald symbol ", 400)
        print(usd(symbol_value["price"]))
        return render_template(
            "quoted.html", symbol_value=symbol_value, price=usd(symbol_value["price"])
        )

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # get datieal from post form
        password = request.form.get("password")
        confiarm_password = request.form.get("confirmation")
        username = request.form.get("username")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)
        elif not confiarm_password:
            return apology(" must confiarm password", 400)
        if password != confiarm_password:
            return apology("  password do not much", 400)

        duplicate = db.execute("select * from users where username = ?", username)
        if len(duplicate) >= 1:
            return apology("User name Used ", 400)

        # if len(username) < 5 or len(username) >15:
        #      return apology("user name at let 5 mix 15 digit", 400)
        # pasord_special_char =['$', '@', '#', '%' ,'&' ,'*']
        # if len(password) <8:

        #     return apology("length should be at least 8 and not be greater than 20", 400)
        #     # return render_template("register.html", error_maseg=error_maseg)
        # elif  len(password) > 20:
        #     return apology( "length should be at least 8 and not be greater than 20", 400)

        # elif not any(i.isdigit() for i in password):
        #     return apology( "Password should have at least one digit", 400)

        # elif not any(i.isupper() for i in password):
        #     return apology( "Password should have at least one uppercase letter", 400)

        # elif not any(i.islower() for i in password):
        #     return apology( "Password should have at least one lowercase letter", 400)

        # elif not any(i in pasord_special_char for i in password):
        #      return apology( "Password should have at least one of the symbols $ @ # % & *" , 400)
        #     # return render_template("register.html", error_maseg=error_maseg)

        password = generate_password_hash(password)
        db.execute("INSERT INTO users (username,hash)VALUES (?,?);", username, password)
        return apology("  Register done ", 200)
        # return redirect("/")
    else:
        return render_template("register.html")
    # return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # """Sell shares of stock"""
    own_iteam = db.execute(
        "select * from sell  where user_id=? GROUP BY symbol", session["user_id"]
    )

    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        if not symbol:
            return apology("Select Symbol", 400)
        if not shares:
            return apology("Add  Shares", 400)

        symbol_check = lookup(symbol)
        if not symbol_check:
            return apology("Not valid symbol", 400)

        if not shares.isdigit():
            return apology("Shares Not valid ", 400)

        if int(shares) < 1:
            return apology(" Shares not valid", 400)

        sum_shares = db.execute(
            "select sum(shares) from sell  where  user_id=? and symbol=?  GROUP BY symbol ",
            session["user_id"],
            symbol,
        )

        if sum_shares[0]["sum(shares)"] < int(shares):
            return apology("Not inf  Shares", 400)
        # total cost for ympol sell
        total_sell = symbol_check["price"] * int(shares)
        total_sold = -total_sell
        shares = -int(shares)
        db.execute(
            "INSERT INTO sell (symbol ,symbol_name,shares,price,total,stat,user_id)VALUES (?,?,?,?,?,?,?);",
            symbol_check["symbol"],
            symbol_check["name"],
            shares,
            symbol_check["price"],
            total_sold,
            "sell",
            session["user_id"],
        )

        #  updat wealt amount
        main_cash = db.execute(
            "SELECT cash FROM users WHERE id = ?", session["user_id"]
        )
        cash_update = main_cash[0]["cash"] + total_sell

        db.execute(
            "UPDATE users SET cash = ? where id = ? ", cash_update, session["user_id"]
        )

        # select total shares for each itaem and total sympoly bought and total amount expend
        all_sell = db.execute(
            "SELECT *,sum(shares),sum (total) FROM sell where  user_id = ?  GROUP BY symbol",
            session["user_id"],
        )
        # print(all_sell)
        #
        # get welat balnce
        new_cash = db.execute("select cash from users where id=?", session["user_id"])
        #  schek  total amount for sympoel
        many_expend = db.execute(
            "select sum(total)  from sell  where user_id=?", session["user_id"]
        )
        total_walet = many_expend[0]["sum(total)"] + new_cash[0]["cash"]

        total_walet = usd(total_walet)
        new_cash = usd(new_cash[0]["cash"])

        # updat pric with usd
        for date in all_sell:
            if date["price"]:
                date["price"] = usd(date["price"])
            if date["total"]:
                date["sum (total)"] = usd(date["sum (total)"])

        # return render_template("sold.html",)
        stat = "Sold"
        return render_template(
            "bought.html",
            meesag=stat,
            total_sell=all_sell,
            new_cash=new_cash,
            total_walet=total_walet,
        )

    else:
        return render_template("sell.html", own_iteam=own_iteam)


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    error_meage = ""
    user_datieal = db.execute("select * from users where id=?", session["user_id"])
    if request.method == "POST":
        password = request.form.get("password")
        user_name = request.form.get("username")
        email = request.form.get("email")

        if not (user_name):
            error_meage = "User Name Not Add"
            return render_template(
                "update.html", error_maseg=error_meage, user_datieal=user_datieal
            )
        if len(user_name) < 5 or len(user_name) > 15:
            return render_template(
                "update.html",
                error_maseg="user name at let 5 mix 15 digit",
                user_datieal=user_datieal,
            )

        if not (email):
            error_meage = "Email Not Add"
            return render_template(
                "update.html", error_maseg=error_meage, user_datieal=user_datieal
            )
        if not (password):
            error_meage = "Password Not Add"
            return render_template(
                "update.html", error_maseg=error_meage, user_datieal=user_datieal
            )

        check_paswoed = password_confiarm(password)
        if check_paswoed != "True":
            return render_template(
                "update.html", error_maseg=check_paswoed, user_datieal=user_datieal
            )

        username_duplicate = db.execute(
            "select * from users where username = ?", user_name
        )
        if len(username_duplicate) >= 1:
            return render_template(
                "update.html", error_maseg="User name Used", user_datieal=user_datieal
            )

        password = generate_password_hash(password)
        db.execute(
            "UPDATE users SET email = ?, username = ?,hash = ? where id = ? ",
            email,
            user_name,
            password,
            session["user_id"],
        )

        user_datieal = db.execute("select * from users where id=?", session["user_id"])
        return render_template(
            "update.html", error_maseg="done", user_datieal=user_datieal
        )
    else:
        return render_template("update.html", user_datieal=user_datieal)
