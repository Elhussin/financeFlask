
# Stock Trading Web Application

This is a Flask-based web application that allows users to manage their stock portfolio. It supports login functionality, buying stocks, viewing transaction history, and fetching stock quotes. The app uses SQLite for storing user data and stock transactions.

## Features

- **User Authentication**: Login and user session management.
- **Stock Portfolio Management**: View and manage a portfolio of stocks.
- **Password Validation**: Strong password policies are enforced.
- **User Authentication**: Users can register, log in, and update their account information.
- **Stock Quote Lookup**: Users can enter a stock symbol to get the latest quote for the stock.
- **Buy and Sell Shares**: Users can buy or sell shares they own,by providing the stock symbol and the number of shares.
- **Transaction History**: Users can view a history of their transactions.
- **User Profile Update**: Users can update their username, email, and password.
  
## Pages and Routes

### 1. **Home Page**
   - Displays basic information about the application and provides links to other pages like Quote, Buy, Sell, and History.

### 2. **Login Page**
   - URL: `/login`
   - Allows users to log in by entering their username and password.

### 3. **Register Page**
   - URL: `/register`
   - Allows users to create an account by providing a username, password, and password confirmation.
   
### 4. **Quote Page**
   - URL: `/quote`
   - Allows users to look up stock symbols by entering a symbol (e.g., `AAPL`) and retrieving the latest stock price.
   
### 5. **Quoted Page**
   - URL: `/quoted`
   - Displays the price of the stock corresponding to the symbol entered on the Quote page.

### 6. **Sell Page**
   - URL: `/sell`
   - Allows users to select a stock symbol and enter the number of shares to sell.
   
### 7. **Update Page**
   - URL: `/update`
   - Allows users to update their username, email, and password.



## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Elhussin/financeFlask.git
   cd stock-trading-app
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```


## Running the Application

To start the application, run:

```bash
python app.py
flask run

```

The application will be available at `http://127.0.0.1:5000/`.

## How to Use

### 1. Register and Log In
- Go to the **Register** page (`/register`) to create an account.
- After registration, you will be redirected to the **Login** page (`/login`). Enter your credentials to log in.

### 2. Look Up Stock Quotes
- Go to the **Quote** page (`/quote`) and enter a stock symbol (e.g., `AAPL`).
- View the latest stock price on the **Quoted** page (`/quoted`).

### 3. Buy/Sell Shares
- On the **Sell** page (`/sell`), select a stock symbol from your owned items and enter the number of shares you want to sell.
- The **Buy** page (`/buy`) allows you to purchase shares.

### 4. Update Your Account Information
- Go to the **Update** page (`/update`) to update your username, email, and password. Make sure to meet the password requirements.

### Error Messages
- If there is an error with form validation (e.g., empty fields, password requirements not met), the application will show an error message.


## Key Functions

### `apology(message, code=400)`
Displays an apology message to the user, typically used for error handling.

### `login_required(f)`
A decorator that ensures the user is logged in before accessing certain routes.

### `lookup(symbol)`
Fetches the latest stock price for a given stock symbol from Yahoo Finance.

### `usd(value)`
Formats a given value as USD currency (e.g., `$1,234.56`).

### `password_confiarm(password)`
Validates that the password meets the following criteria:
- Length between 8 and 20 characters.
- Contains at least one digit.
- Contains at least one uppercase letter.
- Contains at least one lowercase letter.
- Contains at least one special character from the set: `$ @ # % & *`.

## Endpoints

- **/ (Home)**: Displays the user's stock portfolio with cash balance and stock summary.
- **/buy (Buy Stocks)**: Allows users to buy stocks by providing a symbol and the number of shares.
- **/history (Transaction History)**: Displays a history of all the user's stock transactions.
- **/login (Login)**: Allows users to log into their account.
- **/logout (Logout)**: Logs out the current user.
- **/quote (Stock Quotes)**: Allows users to look up the latest stock quote for a given symbol.

## How to Use
How to Use
1. Register and Log In
Go to the Register page (/register) to create an account.
After registration, you will be redirected to the Login page (/login). Enter your credentials to log in.
2. Look Up Stock Quotes
Go to the Quote page (/quote) and enter a stock symbol (e.g., AAPL).
View the latest stock price on the Quoted page (/quoted).
3. Buy/Sell Shares
On the Sell page (/sell), select a stock symbol from your owned items and enter the number of shares you want to sell.
The Buy page (/buy) allows you to purchase shares.
4. Update Your Account Information
Go to the Update page (/update) to update your username, email, and password. Make sure to meet the password requirements.
Error Messages
If there is an error with form validation (e.g., empty fields, password requirements not met), the application will show an error message.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
