from ib.opt import Connection, message
import mysql.connector
import time
import ib_portfolio as port
import data_prices as prices
import ib_trader as trader
import datetime

# Parameters of the strategy make sure to adapt them to your account needs
initial_investment = 1000000
number_of_stocks_allowed = 50
position_size = initial_investment / number_of_stocks_allowed
holding_period = 12 * 30  # number of days each stock is held for

def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day


# Find stocks that meet the -15% change requirement
def contrarian_plays(date):
    # connects to DB
    cnx = mysql.connector.connect(host="localhost", user="root", passwd="root", db="trading")
    cursor = cnx.cursor(buffered=True)

    # fetch tickers that have fallen for more than 15%
    cursor.execute('select symbol, close_ from stock_prices where adj_change < -0.14 and date = "' + str(date) + '"')
    stocks = cursor.fetchall()

    # Finds how much cash is left in portfolio
    cursor.execute('select total_value from portfolio_holdings where secType = "cash" order by date limit 1')
    cash_available = cursor.fetchall()

    # Retrieves holdings of the portfolio and the dates they were purchased
    cursor.execute('select min(date), ticker, shares from portfolio_holdings group by ticker')
    portfolio = cursor.fetchall()

    values = (stocks, cash_available, portfolio)

    return values


# Sends trades to Interactive Brokers using ib_trader given a list of orders
def send_orders(stocks, cash_available, conn):
    x = 0
    for stock in stocks:

        symbol = stock[0]
        sec_type = 'STK'
        exch = 'SMART'
        prim_exch = 'SMART'
        curr = 'USD'
        action = 'BUY'
        oid = int(time.time() + x)
        quantity = int(position_size / float(stock[1]))
        x = x + 1

        # only makes the transaction if there is enough cash in the portfolio
        if quantity * float(stock[1]) > cash_available:
            trader.make_transaction(conn, symbol, sec_type, exch, prim_exch, curr, action, oid, quantity)
            # temporarily reduce cash_balance in order to not send too many orders, this is not saved to db
            cash_available = cash_available - (quantity * float(stock[1]))
        else:
            print ("Not enough funds to complete this transaction")


# Checks and sends sell orders whenever a stock has surpassed the holding period
def check_sells(conn, portfolio):
    purchase_date = portfolio[0]
    tickers = portfolio[1]
    shares = portfolio[2]
    x=0
    while x < tickers.len():
        if (purchase_date[x] - to_integer(datetime.date.today())) and tickers[x] != 'cash':
            symbol = tickers[x]
            sec_type = 'STK'
            exch = 'SMART'
            prim_exch = 'SMART'
            curr = 'USD'
            action = 'SELL'
            oid = int(time.time() + x)
            quantity = shares[x]

            try:
                trader.make_transaction(conn, symbol, sec_type, exch, prim_exch, curr, action, oid, quantity)

            except:
                pass

def main():
    # port.main()
    # prices.main()

    # connects to TWS-- make sure to include your port and clientID here
    conn = Connection.create(port='{YOUR PORT}', clientId='{YOUR CLIENT_ID}')
    values = contrarian_plays(to_integer(datetime.date.today()))
    send_orders(values[0], values[1], conn)
    # for some reason if there is no break between transactions it won't work
    time.sleep(5)


    portfolio = values[2]
    # checks if there are any stocks to be sold
    check_sells(conn, portfolio)

    conn.disconnect()

main()