import openpyxl
from model import Instruction, Strategy_Input

class SpreadsheetHandler:
    def __init__(self, file_path) -> None:
        self.file_path = file_path

    def load_spreadsheet(self):
        """Load the workbook and return the active sheet."""
        wb = openpyxl.load_workbook(self.file_path)
        ws = wb.active
        return ws

    def get_values(self, cell):
        """Extract non-null values from a cell."""
        values = [cell_item.value for cell_item in cell if cell_item.value is not None]
        return values

    def construct_instruction_data(self, values):
        """Construct instruction data from given values."""
        instruction_data = [
            Instruction(
                values[2 + (i * 6)],
                values[3 + (i * 6)],
                values[4 + (i * 6)],
                int(values[5 + (i * 6)]),
                int(values[6 + (i * 6)]),
                float(values[7 + (i * 6)]),
            ) for i in range(int((len(values) - 2) / 6))  # The range is calculated based on the structure of the values in cells
        ]
        return instruction_data

    def append_strategy_input(self, strategies, cell, instruction_data):
        """Append new Strategy_Input instance to strategies list."""
        strategies.append(Strategy_Input(cell[1].value, instruction_data))

    def transform_data(self)->list[Strategy_Input]:
        """Transforms spreadsheet data into a list of Strategy_Input instances."""
        ws = self.load_spreadsheet()

        row = 4
        max_rows = len(list(ws.rows))
        strategies = []

        while row <= max_rows:
            cell = list(ws.rows)[row - 1]
            values = self.get_values(cell)
            instruction_data = self.construct_instruction_data(values)

            self.append_strategy_input(strategies, cell, instruction_data)
            
            row += 1
        return strategies