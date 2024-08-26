from binance.um_futures import UMFutures
from binance.error import ClientError
import math

# API credentials
api_key = 'ddVVElJ8PoxL1MXDVI9MjwoSnJwcnaCxs0IPw4f9Q2LZ1GEB4L6DNwUwX9dmTD0R'
api_secret = '1ERwBBaX6nmCdzfcEpyiSETX3XU8z8Fzq0fmSBRGNILTM3nDMobJB4lMJRL2OKpi'

# Initialize the UMFutures client
client = UMFutures(key=api_key, secret=api_secret)

# Trading parameters
symbol = 'FILUSDT'
usdt_amount = 2.5
leverage = 20
take_profit_percent = 0.4
stop_loss_percent = 0.4

def get_symbol_info(symbol):
    exchange_info = client.exchange_info()
    for s in exchange_info['symbols']:
        if s['symbol'] == symbol:
            return s
    raise ValueError(f"Symbol {symbol} not found")

def round_step_size(quantity, step_size):
    precision = int(round(-math.log(step_size, 10), 0))
    return round(quantity, precision)

def place_short_trade():
    try:
        symbol_info = get_symbol_info(symbol)
        quantity_precision = next(filter(lambda f: f['filterType'] == 'LOT_SIZE', symbol_info['filters']))['stepSize']
        price_precision = next(filter(lambda f: f['filterType'] == 'PRICE_FILTER', symbol_info['filters']))['tickSize']

        client.change_leverage(symbol=symbol, leverage=leverage)

        ticker = client.ticker_price(symbol)
        entry_price = float(ticker['price'])

        quantity = (usdt_amount * leverage) / entry_price
        rounded_quantity = round_step_size(quantity, float(quantity_precision))

        take_profit_price = round_step_size(entry_price * (1 - take_profit_percent / 100), float(price_precision))
        stop_loss_price = round_step_size(entry_price * (1 + stop_loss_percent / 100), float(price_precision))

        order = client.new_order(
            symbol=symbol,
            side="SELL",
            type="MARKET",
            quantity=rounded_quantity
        )

        tp_order = client.new_order(
            symbol=symbol,
            side="BUY",
            type="TAKE_PROFIT_MARKET",
            timeInForce="GTC",
            quantity=rounded_quantity,
            stopPrice=take_profit_price,
            workingType="MARK_PRICE"
        )

        sl_order = client.new_order(
            symbol=symbol,
            side="BUY",
            type="STOP_MARKET",
            timeInForce="GTC",
            quantity=rounded_quantity,
            stopPrice=stop_loss_price,
            workingType="MARK_PRICE"
        )

        print(f"Short position opened for {symbol}")
        print(f"Entry Price: {entry_price}")
        print(f"Quantity: {rounded_quantity}")
        print(f"Take Profit Price: {take_profit_price}")
        print(f"Stop Loss Price: {stop_loss_price}")

    except ClientError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    place_short_trade()
    
