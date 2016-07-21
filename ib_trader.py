from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order

def make_contract(symbol, sec_type, exch, prim_exch, curr):
    Contract.m_symbol = symbol
    Contract.m_secType = sec_type
    Contract.m_exchange = exch
    Contract.m_primaryExch = prim_exch
    Contract.m_currency = curr
    return Contract

def make_order(action, quantity, price = None):
    if price is not None:
        order = Order()
        order.m_orderType = 'LMT'
        order.m_totalQuantity = quantity
        order.m_action = action
        order.m_lmtPrice = price

    else:
        order = Order()
        order.m_orderType = 'MKT'
        order.m_totalQuantity = quantity
        order.m_action = action

    return order


# Connects to IB Api and sends an order to the server
def make_transaction(conn, symbol, sec_type, exch, prim_exch, curr, action, oid, quantity, price = None):
    conn.connect()
    cont = make_contract(symbol, sec_type, exch, prim_exch, curr)
    offer = make_order(action, quantity)
    conn.placeOrder(oid, cont, offer)




