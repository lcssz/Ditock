# Ditock: Derivative Analysis with Python and MT5

This is a personal project that utilizes Python and MetaTrader 5 (MT5) for data analysis of desired stock derivatives. The project takes an Excel spreadsheet of strategies as input and outputs another spreadsheet with parameters defined in the "strategy_output.py" model.

## Project Structure

The project has the following structure:

```
.
├── .gitignore
├── ditock.py
├── README.md
├── controller
│   ├── output_data.py
│   ├── setup_data.py
│   ├── strategy_sheet.py
│   └── __init__.py
├── model
│   ├── instruction.py
│   ├── strategy_input.py
│   ├── strategy_output.py
│   ├── symbol_data.py
│   └── __init__.py
├── out
└── resources
    ├── custom_stocks.txt
    ├── Strategies.xlsx
    └── symbol_database.pkl
```

## Usage

1. Update the `Strategies.xlsx` file in the `resources` directory with your desired strategies.
2. Run the `ditock.py` script.
3. The script will generate an output spreadsheet in the `out` directory with the parameters defined in the "strategy_output.py" model.

Please note that this project is still under development, so some features may not be fully functional yet. Contributions are welcome!
