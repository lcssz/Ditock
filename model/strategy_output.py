from model.strategy_input import Strategy_Input
from model.symbol_data import SymbolData

class Strategy_Output:
    def __init__(self,symbols:list[SymbolData],strategy_type:Strategy_Input):
        self.symbols = symbols
        self.strategy_type = strategy_type
        self.name = None
        self.combination:str
        self.delta = 0.0
        self.cust_mount = 0.0
        self.cust_dismount = None
        self.symbol_strike = None

    def calculate_difference(self, symbol, instruction):
        """Calculate the difference between strategy instructions according to the condition"""
        if instruction.condition == 'C':
            self.delta -= symbol.option_strike * instruction.volume
            if symbol.bid:
                self.cust_mount -= symbol.bid
        else:
            self.delta += symbol.option_strike * instruction.volume
            if symbol.ask:
                self.cust_mount += symbol.ask
    
    def append_combination(self, symbol, instruction):
        """Create and append the new combination details"""
        combination = f"{instruction.condition},{symbol.name},{instruction.volume * 100}"
        return combination

    def append_symbol_strike(self, symbol):
        """Create and append the new symbol strike details"""
        symbol_strike = f"{symbol.name} R${symbol.option_strike}"
        return symbol_strike

    def transform_in_row(self)->tuple:
        """Transform the strategy output details to a tuple format"""
        self.name = self.strategy_type.name
        combinations = []
        symbols_strikes = []
        for index, symbol in enumerate(self.symbols):
            if symbol is not None:
                instruction = self.strategy_type.instructions[index]
                # Calculate the difference
                self.calculate_difference(symbol, instruction)
                # Append the new combination details to the list
                combinations.append(self.append_combination(symbol, instruction))
                # Append the new symbols strikes details to the list
                symbols_strikes.append(self.append_symbol_strike(symbol))
                if self.cust_mount:
                    self.cust_dismount = round(self.cust_mount * 1.6, 1)
                else:
                    self.cust_dismount = "Unable to get value from the book."
        self.delta = round(self.delta, 1)
        self.combination = ",".join(combinations)
        self.symbol_strike = "; ".join(symbols_strikes)
        return (self.name,self.combination,self.delta,self.cust_mount,self.cust_dismount,self.symbol_strike)