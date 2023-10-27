from model.instruction import Instruction

class Strategy_Input:
    # The name of the Strategy_Input
    def __init__(self, name:str, 
                 # A list of Instruction objects associated with this Strategy_Input
                 instructions: list[Instruction]):
        self.name = name
        self.instructions = instructions