from time import sleep
import mysql.connector
import datetime
from ib.opt import ibConnection, message


# DEFINE a basic function to capture error messages
def error_handler(msg):
    print ("Error", msg)


# DEFINE a basic function to print the "raw" server replies
def replies_handler(msg):
    print ("Server Reply:", msg)


# DEFINE a basic function to print the "parsed" server replies for an IB Request of "Portfolio Update" to list an IB
# portfolio position
def print_portfolio_position(msg):
    print (msg)


def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day


# Define function to receive a updateAccountValue message and extract the cash value of portfolio. It further stores
# that value into the SQL database
def add_cash_to_db(msg):
    cnx = mysql.connector.connect(host="localhost", user="", passwd="", db="trading")
    cursor = cnx.cursor(buffered=True)

    if msg.key == "CashBalance" and msg.currency == "BASE":

        query = """INSERT INTO portfolio_holdings (id, date, ticker, total_value, shares, current_price, currency, secType, unrealizedPNL, averageCost, p_return) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        id = 'cash ' + datetime.date.today().strftime("%B %d, %Y")
        date = to_integer(datetime.date.today())
        ticker = 'cash'
        shares = 0
        current_price = 0
        total_value = msg.value
        currency = 'USD'
        secType = 'cash'
        unrealizedPNL = 0
        average_cost = 0
        p_return = 0

        values = (id, date, ticker, total_value, shares, current_price, currency, secType, unrealizedPNL, average_cost, p_return)

        # Tries to execute sql Query if it has not been included in the db yet
        try:
            cursor.execute(query, values)
        except mysql.connector.errors.IntegrityError:
            print('Data Already Inserted into database due to duplicated primary key ID')
            pass

        cursor.close()

        # Commit the transaction
        cnx.commit()

    cnx.close()


# Define function to receive a UpdatePortfolio message and extract the holdings of portfolio. It further stores
# that value into the SQL database
def add_position_to_db(msg):
    cnx = mysql.connector.connect(host="localhost", user="", passwd="", db="trading")
    cursor = cnx.cursor(buffered=True)

    query = """INSERT INTO portfolio_holdings (id, date, ticker, total_value, shares, current_price, currency, secType, unrealizedPNL, averageCost, p_return) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    id =  msg.contract.m_symbol + datetime.date.today().strftime("%B %d, %Y")
    date = to_integer(datetime.date.today())
    ticker = msg.contract.m_symbol
    shares = msg.position
    current_price = msg.marketPrice,
    total_value = current_price[0] * shares
    currency = msg.contract.m_currency,
    secType = msg.contract.m_secType
    unrealizedPNL = msg.unrealizedPNL
    averageCost = msg.averageCost
    p_return = current_price[0] / averageCost - 1

    values = (id, date, ticker, total_value, shares, current_price[0], currency[0], secType, unrealizedPNL, averageCost, p_return)

    # Tries to execute sql Query if it has not been included in the db yet
    try:
        cursor.execute(query, values)
    except mysql.connector.errors.IntegrityError:
        print('Data Already Inserted into database due to duplicated primary key ID')
        pass

    cursor.close()

    # Commit the transaction
    cnx.commit()
    cnx.close()


# Runs the program
def main():
    # Create the connection to IBGW with a client socket
    ibgw_conChannel = ibConnection(port='{YOUR PORT}', clientId='{YOUR CLIENT_ID}')
    ibgw_conChannel.connect()

    # Map server replies to "add position to db" function for "UpdatePortfolio" client requests
    ibgw_conChannel.register(add_position_to_db, 'UpdatePortfolio')

    # Adds cash balance positions to the db
    ibgw_conChannel.register(add_cash_to_db, message.updateAccountValue)

    # Make client request for AccountUpdates (includes request for Portfolio positions)
    ibgw_conChannel.reqAccountUpdates(1, '')

    # Stop client request for AccountUpdates
    ibgw_conChannel.reqAccountUpdates(0, '')

    ibgw_conChannel.reqAccountUpdates(True, 'DU000000')
    sleep(5)

    # Disconnect - optional
    ibgw_conChannel.disconnect()
