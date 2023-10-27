class Instruction:
    # Instantiate the Instruction class
    def __init__(self, condition: str, paper_type: str, moneyness: str, expiration: int, volume: int, diff_strike: int):
            # Description/Condition of the instruction
            self.condition = condition
            
            # Type of securities (e.g., equity, bond etc.)
            self.paper_type = paper_type
            
            # The state of an option contract (i.e., whether it is 'in the money,' 'at the money,' or 'out of the money')
            self.moneyness = moneyness
            
            # Expiration period for the derivatives
            self.expiration = expiration
            
            # Volume of the securities
            self.volume = volume
            
            # Difference from the strike price
            self.diff_strike = diff_strike