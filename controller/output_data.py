from .strategy_sheet import SpreadsheetHandler
from model import Strategy_Output
from model import Instruction
import pickle
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import openpyxl
from openpyxl.styles import Alignment
# Define the active/current month of the project.
actual_month = date.today()


# Helper function to retrieve local database as a dictionary.
def get_local_database(data_path)->dict:
    with open(data_path,'rb') as f:
        return pickle.load(f)


# Helper function to get raw strategies from a spreadsheet.
def get_raw_stratgies(wb_path):
    handler = SpreadsheetHandler(wb_path)
    return handler.transform_data()


# Helper function to retrieve stock options from a stored file.
def get_stock_option(stocks_path):
    with open(stocks_path) as f:
        stocks = f.read().split(";")
        return stocks

    
# Function to mount strategies with zero difference strike.
def mount_zero_strategy(stock, strategy, data: dict):
    output = []
    instructions = strategy.instructions
    for instruction in instructions:
        month = (actual_month + relativedelta(months=instruction.expiration)).strftime('%Y-%m')
        key = (stock, instruction.paper_type, instruction.moneyness, month)
        if key not in data:
            continue
        values = data[key]
        for value in values:
            for match_instruction in instructions:
                if match_instruction == instruction:
                    continue
                match_month = (actual_month + relativedelta(months=match_instruction.expiration)).strftime('%Y-%m')
                match_key = (stock, match_instruction.paper_type, match_instruction.moneyness, match_month)
                if match_key not in data:
                    continue
                match_symbols = data[match_key]
                for match_symbol in match_symbols:
                    out = Strategy_Output([value,match_symbol],strategy)
                    output.append(out)
    return output


# Function to mount unique at the money (ATM) strategy.
def mount_unique_atm_strategy(stock, instructions: list[Instruction], data: dict, atm_index):
    month = (actual_month + relativedelta(months=instructions[atm_index].expiration)).strftime('%Y-%m')
    key = (stock, instructions[atm_index].paper_type, instructions[atm_index].moneyness, month)
    if key not in data:
        return
    atm_values = data[key]
    output = []

    non_atm_values_sorted = {}
    for instruction in instructions:
        if instruction.moneyness != "ATM":
            key = (stock, instruction.paper_type, instruction.moneyness, month)
            if key in data:
                non_atm_values_sorted[instruction.moneyness] = sorted(data[key], key=lambda x: x.option_strike)

    for atm in atm_values:
        atm_output = [None for _ in instructions]
        atm_output[atm_index] = atm
        for i, instruction in enumerate(instructions):
            if instruction.moneyness != "ATM" and instruction.moneyness in non_atm_values_sorted:
                matching_symbol = min((non_atm for non_atm in non_atm_values_sorted[instruction.moneyness] if non_atm.moneyness==instruction.moneyness), key=lambda x: abs(x.option_strike - atm.option_strike - instruction.diff_strike))
                if matching_symbol is not None:
                    atm_output[i] = matching_symbol
        output.append(atm_output)
    return output


# Function to mount double ATM strategy.
def mount_double_atm_strategy(stock, instructions: list[Instruction], data: dict):
    output = []
    month = (actual_month + relativedelta(months=instructions[0].expiration)).strftime('%Y-%m')
    paper_types = set(instruction.paper_type for instruction in instructions)

    if len(paper_types) > 1:
        atm_values_call_key = (stock, "CALL", "ATM", month)
        atm_values_put_key = (stock, "PUT", "ATM", month)
        if atm_values_call_key in data and atm_values_put_key in data:
            atm_values_call = data[atm_values_call_key]
            atm_values_put = data[atm_values_put_key]
            for atm_call in atm_values_call:
                for atm_put in atm_values_put:
                    if abs(atm_call.option_strike - atm_put.option_strike) <= 2:
                        new_list = []
                        for instruction in instructions:
                            if instruction.paper_type == "CALL":
                                new_list.append(atm_call)
                            else:
                                new_list.append(atm_put)
                        output.append(new_list)
        else:
            print("Unable to complete data processing:")
    return output


# Main function to generate an excel sheet of strategies.
def output_wb_strategies():
    wb = openpyxl.Workbook()
    local_database = get_local_database("./resources/symbol_database.pkl")
    raw_strategies = get_raw_stratgies('./resources/Strategies.xlsx')
    stocks = get_stock_option("./resources/custom_stocks.txt")
    for stock in stocks:
        stock_ws = wb.create_sheet(stock)
        stock_ws.append(["Choice","Strategy Name","Combination","Delta","Cost per paper on montage","Cost per paper on dismounting","Paper and Strike","Payoff CALL","Payoff PUT"])
        for strategy in raw_strategies:
            if any(i.diff_strike == 0 for i in strategy.instructions):
                strategy_data = mount_zero_strategy(stock,strategy,local_database)
                if strategy_data:
                    for symbol_list in strategy_data:
                        stock_ws.append(symbol_list.transform_in_row())
            else:
                atm_count = sum(i.moneyness=="ATM" for i in strategy.instructions)
                if atm_count==1:
                    index = [index for index, item in enumerate(strategy.instructions) if item.moneyness=="ATM"][0]
                    strategy_data = mount_unique_atm_strategy(stock,strategy.instructions,local_database,index)
                    if strategy_data:
                        for symbol_list in strategy_data:
                            data = Strategy_Output(symbol_list,strategy)
                            stock_ws.append(data.transform_in_row())
                elif atm_count==2:
                    strategy_data = mount_double_atm_strategy(stock,strategy.instructions,local_database)
                    if strategy_data:
                        for symbol_list in strategy_data:
                            data = Strategy_Output(symbol_list,strategy)
                            stock_ws.append(data.transform_in_row())
        
        stock_ws.row_dimensions[1].height = 56.7
        stock_ws.column_dimensions['D'].width = 10
        stock_ws.column_dimensions['E'].width = 12
        stock_ws.freeze_panes = "A2"
        dims = {}
        for row in stock_ws.rows:
            for cell in row:
                dims[cell.column_letter] = max((dims.get(cell.column_letter, 0), len(str(cell.value))))
                cell.alignment = Alignment(horizontal='center', vertical='center')
                if cell.coordinate in ['D1','E1']:
                    cell.alignment = Alignment(horizontal='center', vertical='center',wrap_text=True)
        for col, value in dims.items():
            if value and col not in ['D','E']:
                stock_ws.column_dimensions[col].width = value

    del wb["Sheet"]
    wb.save(f'./out/Combination-{datetime.now().strftime("%d-%m-%Y %HH%Mm")}.xlsx')