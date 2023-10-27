class SymbolData:
    def __init__(self, name, option_right, option_strike, expiration_time, moneyness, bid, ask):
        # name: name of the symbol.
        self.name = name
        
        # option_right: the type of rights an options contract gives to the contract owner (call or put).
        self.option_right = option_right
        
        # option_strike: the price at which the holder of an options contract can realize their right to buy or sell the security.
        self.option_strike = option_strike
        
        # expiration_time: the date and time when the options contract expires.
        self.expiration_time = expiration_time
        
        # moneyness: the state of an option, indicating its potential profitability.
        self.moneyness = moneyness
        
        # bid: the price at which a trader is willing to purchase the option.
        self.bid = bid
        
        # ask: the price at which a trader is willing to sell the option.
        self.ask = ask