import os
import openpyxl

def start_file():
    with open("./resources/preset.txt",'r',encoding='utf-8') as f:
        return f.readlines()

def get_workbook_from_user():
    xlsx_files = [f for f in os.listdir("./out") if f.endswith(".xlsx")]
    print("Files available for reading:")
    for i, file in enumerate(xlsx_files):
        print(i, file)
    selected_file_index = int(input("Choose a file by its number:"))
    selected_file = xlsx_files[selected_file_index]
    return openpyxl.load_workbook("./out/" + selected_file)

def process_workbook(workbook, file_data):
    counter = 1
    file_counter = 1
    file = open(f'./out/sets/combinations-{file_counter}.set', 'w',encoding='utf-8')
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows(min_row=1, min_col=1, max_col=6):
            if row[0].value == 'x' and row[5].value != "-":
                update_file_data(file_data, counter, row)
                counter += 1
                if counter > 10:
                    write_to_file(file, file_data)
                    file_counter += 1
                    file_data = start_file()
                    file = open_new_file(file_counter)
                    counter = 1
    write_to_file(file, file_data)
    file.close()

def update_file_data(file_data, counter, row):

    file_data[counter*6] = f"operationalName{counter}={row[1].value}\n"
    file_data[counter*6+1] = f"operationalCombination{counter}={row[2].value}\n"
    file_data[counter*6+2] = f"operationalFinanceToOpen{counter}={round(float(row[4].value),2)}\n"
    file_data[counter*6+3] = f"operationalFinanceToClose{counter}={round(float(row[5].value),2)}\n"
    file_data[counter*6+4] = f"operationalFinanceDelta{counter}={round(float(row[4].value*0.05,),2)}\n"

def write_to_file(file, file_data):
    file.writelines(file_data)

def open_new_file(file_counter):
    return open(f'./out/sets/combinations-{file_counter}.set', 'w',encoding='utf-8')

if __name__ == "__main__":
    file_data = start_file()
    workbook = get_workbook_from_user()
    process_workbook(workbook, file_data)