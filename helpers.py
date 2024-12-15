import requests
import yfinance as yf
from flask import redirect, render_template, session
from functools import wraps

# Function: apology
# This function renders an apology message to the user by displaying a template with a customizable message and status code.
def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters to make the message URL-safe.
        Reference: https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('\"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    # Render the apology.html template with the escaped message and status code
    return render_template("apology.html", top=code, bottom=escape(message)), code

# Function: login_required
# This decorator ensures that users must be logged in to access certain routes.
def login_required(f):
    """
    Decorate routes to require login.
    Reference: http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in by verifying if 'user_id' exists in the session
        if session.get("user_id") is None:
            # Redirect to the login page if the user is not logged in
            return redirect("/login")
        # Proceed to the requested route if logged in
        return f(*args, **kwargs)

    return decorated_function

# Function: lookup
# Fetches the latest stock price and related data for a given stock symbol from Yahoo Finance.
# def lookup(symbol):
    # """Look up quote for symbol."""

    # # Prepare the stock symbol in uppercase
    # symbol = symbol.upper()
    
    # # Define the time range (past 7 days)
    # end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    # start = end - datetime.timedelta(days=7)

    # # Construct the Yahoo Finance API URL
    # url = (
    #     f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
    #     f"?period1={int(start.timestamp())}"
    #     f"&period2={int(end.timestamp())}"
    #     f"&interval=1d&events=history&includeAdjustedClose=true"
    # )

    # # Query the Yahoo Finance API
    # try:
    #     response = requests.get(
    #         url,
    #         cookies={"session": str(uuid.uuid4())},
    #         headers={"User-Agent": "python-requests", "Accept": "*/*"},
    #     )
    #     response.raise_for_status()

    #     # Parse the CSV response from the API
    #     quotes = list(csv.DictReader(response.content.decode("utf-8").splitlines()))
    #     quotes.reverse()  # Reverse to get the latest quote first

    #     # Extract and return the latest adjusted close price
    #     price = round(float(quotes[0]["Adj Close"]), 2)
    #     return {"name": symbol, "price": price, "symbol": symbol}
    # except (requests.RequestException, ValueError, KeyError, IndexError):
    #     # Return None if there's an issue with the request or data parsing
    #     return None


def lookup(symbol):
    try:
        symbol = symbol.upper()
        stock = yf.Ticker(symbol)
        data = stock.history(period="5d")
        price = data["Close"].iloc[-1]  # Last closing price

        return {"name": symbol, "price": price, "symbol": symbol}
    except (requests.RequestException, ValueError, KeyError, IndexError):
        # Return None if there's an issue with the request or data parsing
        return None

# Function: usd
# Formats a given value as a USD currency string.
def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# Function: password_confiarm
# Validates a password based on length, digit, uppercase, lowercase, and special character rules.
def password_confiarm(password):
    """Validate the password and return an appropriate error message or 'True' if valid."""

    # List of allowed special characters
    pasord_special_char = ["$", "@", "#", "%", "&", "*"]
    error_maseg = ""  # Initialize an error message variable

    # Check password length constraints
    if len(password) < 8:
        error_maseg = "Length should be at least 8 and not be greater than 20"
    elif len(password) > 20:
        error_maseg = "Length should be at least 8 and not be greater than 20"

    # Check for at least one digit
    elif not any(i.isdigit() for i in password):
        error_maseg = "Password should have at least one digit"

    # Check for at least one uppercase letter
    elif not any(i.isupper() for i in password):
        error_maseg = "Password should have at least one uppercase letter"

    # Check for at least one lowercase letter
    elif not any(i.islower() for i in password):
        error_maseg = "Password should have at least one lowercase letter"

    # Check for at least one special character
    elif not any(i in pasord_special_char for i in password):
        error_maseg = "Password should have at least one of the symbols $ @ # % & *"

    else:
        # Password is valid
        error_maseg = "True"

    # Return the validation result
    return error_maseg
