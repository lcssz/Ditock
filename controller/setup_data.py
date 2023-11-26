import MetaTrader5 as mt5
from datetime import date
import time
import pickle
from model.symbol_data import SymbolData

# The days to increment value equivalent to 12 days in seconds.
INC_DAYS = 1036800 

def initialize_mt5():
    """
    Initialize MetaTrader5. This will quit the program if the initialization fails.
    """
    if not mt5.initialize():
        print("Unable to start MetaTrader5 :", mt5.last_error())
        quit()

def watch_all_symbols(stocks):
    for stock in stocks:
        if not mt5.symbol_select(stock):
            print("symbol_select({}) failed, error code={}".format(stock, mt5.last_error()))
            continue
        symbols_data = get_raw_symbols_data()
        symbols_to_watch = [s.basis for s in symbols_data if s.basis == stock or s.name.startswith(stock[:-1:])]
        for symbol in symbols_to_watch:
            if not mt5.symbol_select(symbol):
                print("symbol_select({}) failed, error code={}".format(stock, mt5.last_error()))
                continue

def get_raw_symbols_data():
    """
    Get raw symbols data from MetaTrader5.
    Returns:
        A list of symbols data.
    """  
    return mt5.symbols_get()

def write_data_to_file(dict_data):
    """
    Write symbol data to a pickle file.
    Parameters:
        dict_data: A dictionary containing symbol data.
    """
    filename = "./resources/symbol_database.pkl"
    with open(filename, "wb") as f:
        pickle.dump(dict_data, f)

def setup_symbol_data():
    """
    Set up symbol data by fetching data from MetaTrader5 and saving it to a pickle file. 
    This function also processes and modifies the data accordingly.
    Returns:
        A dictionary containing processed symbol data.
    """
    initialize_mt5()
    stocks = []
    # Fetch the stocks list from a text file.
    with open("./resources/custom_stocks.txt", 'r') as f:
        stocks = f.read().split(";")
    watch_all_symbols(stocks)
    symbols_data = get_raw_symbols_data()
    dict_data = {}
    
    # Loop over each stock and fetch its current price.
    for n_stock in stocks:
        # Fetch the current price of the stock.
        spot_price_info = mt5.symbol_info_tick(str(n_stock))
        spot_price = (spot_price_info.bid + spot_price_info.ask) / 2
        # Loop over symbols data and process each symbol.
        for data in symbols_data:
            symbol = data._asdict()
            basis = symbol["basis"]

            # Check equality on the basis field.
            if basis != n_stock and basis != n_stock.split(".")[0]:
                continue
            
            expiration_time = None
            if len(str(symbol["expiration_time"]))==10:
                expiration_time = date.fromtimestamp(symbol["expiration_time"])
            
            if int(time.time() + INC_DAYS) < symbol["expiration_time"] and symbol["option_strike"] > 5:
                moneyness = spot_price / symbol["option_strike"]
                if moneyness < 0.70 or moneyness > 1.30:
                    continue
                
                moneyness_str = ''
                if symbol["option_right"] == 1: # Put
                    if moneyness >= 1.02 and moneyness <= 1.30:
                        moneyness_str = 'ITM'
                    elif moneyness >= 0.98 and moneyness <= 1.02:
                        moneyness_str = 'ATM'
                    elif moneyness <= 0.98 and moneyness >= 0.70:
                        moneyness_str = 'OTM'
                else: # Call
                    if moneyness <= 0.98 and moneyness >= 0.70:
                        moneyness_str = 'ITM'
                    elif moneyness >= 0.98 and moneyness <= 1.02:
                        moneyness_str = 'ATM'
                    elif moneyness >= 1.02 and moneyness <= 1.30:
                        moneyness_str = 'OTM'
                
                option_right = 'CALL' if symbol["option_right"] == 0 else 'PUT'
                key_dict = (symbol["basis"],option_right,moneyness_str,expiration_time.strftime('%Y-%m'))           
                
                if key_dict not in dict_data:
                    dict_data[key_dict] = []

                mt5.market_book_add(symbol["name"])

                book_info_tuple = mt5.market_book_get(symbol["name"])
                
                book_bid_value = book_info_tuple[0].price if book_info_tuple else None
                book_ask_value = book_info_tuple[1].price if book_info_tuple and len(book_info_tuple) > 1 else None

                symbol_obj = SymbolData(symbol["name"], option_right, symbol["option_strike"], expiration_time, moneyness_str, book_bid_value, book_ask_value)

                dict_data[key_dict].append(symbol_obj)
    
    write_data_to_file(dict_data)
    mt5.shutdown()
    
    return dict_data