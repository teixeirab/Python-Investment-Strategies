import csv
import mysql.connector
import requests, zipfile, io
from datetime import datetime
import time

# CHANGE TO INCLUDE YOUR API KEY
last_day_url = 'https://www.quandl.com/api/v3/databases/WIKI/data?api_key={ADD_YOUR_API_KEY_HERE}&download_type=partial'

def to_integer(dt_time):
    return 10000*dt_time.year + 100*dt_time.month + dt_time.day

def to_datetime(string):
    return datetime.strptime(string, '%Y-%m-%d')

# DEFINE a basic function to request prices from quanld API
def quandl_prices_request():
    r = requests.get(last_day_url)

    z = zipfile.ZipFile(io.BytesIO(r.content))

    # CHANGE TO INCLUDE YOUR Directory Location
    z.extractall('{PATH HERE}/data')
    for name in z.namelist():
        return '/Data/' + name
    time.sleep(5)

# DEFINE a method to insert data from a csv file into a pre defined stock_data table
def import_data_db(path):
    cnx = mysql.connector.connect(host="localhost", user="", passwd="", db="trading")
    cursor = cnx.cursor(buffered=True)

    with open ('{PATH HERE}/git' + path, 'rt') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            try:
                change = float(row[9]) / float(row[12]) - 1
            except ValueError:
                change = 0
                pass

            id = '' + row[0] + row[1]
            date = to_integer(to_datetime(row[1]))
            row.append(change)
            row.append(id)
            row.append(date)

            try:
                cursor.execute(
                        'INSERT INTO stock_prices(symbol, date_, open_, high_, low_, close_, volume_, ex_dividend, '
                        'split_ratio, adj_open, adj_high, adj_low, adj_close, adj_volume, adj_change, id, date) '
                        'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        row)
            except mysql.connector.errors.IntegrityError:
                print ('Data Already Inserted into database due to duplicated primary key ID')
                pass

    cnx.commit()
    cursor.close()
    cnx.close()

def main():
    path = quandl_prices_request()
    import_data_db(path)
