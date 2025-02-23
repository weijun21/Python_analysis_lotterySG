import os
import win32com.client
import openpyxl
import time
class excel_functions:

    def __init__(self):
        self.excel = win32com.client.Dispatch("Excel.Application")
        self.workbook_name = 'database_analysis.xlsx'
        self.workbook_path = os.path.join(os.getcwd(), self.workbook_name)
        self.workbook = self.excel.Workbooks.Open(self.workbook_path)
        self.excel.Visible = False
        self.sheet = self.workbook.ActiveSheet
    
    def open_function(self):
        
        self.workbook.Activate()
        print("Opening Excel application...")
        print("Excel application opened.")

    
    def close_function(self):
        self.workbook.Save()
        print("Saving workbook...")
        self.workbook.Close()
        self.excel.Quit()
        print("Excel application closed.")
            
        
    #def run_refreshmacro(self):
        """self.excel.Visible = False
        print("Running refresh macro...")
        self.workbook.Application.Run("refresh_test1")
        print("Refresh macro completed.")
        self.excel.Application.Wait(Timeout:=10)
        ("Waiting for Excel to finish...")"""
        
  
    def save_function(self):
        self.workbook.Save()
        self.close_function()
        
    def run_macro(self,macro_name):
        self.sheet.Run(macro_name)
        self.workbook.Save()

        
    
    def count_column_values(self, sheet_name, column_letter):
        sheet = self.workbook.Sheets(sheet_name)
        column_values = []
        for row in range(2, sheet.UsedRange.Rows.Count + 1):
            cell_value = sheet.Cells(row, ord(column_letter) - 64).Value
            if cell_value is not None:
                column_values.append(cell_value)
        counts = {}
        total_count = 0
        for value in column_values:
            if value in counts:
                counts[value] += 1
            else:
                counts[value] = 1
            total_count += 1
        
        column_values = list(set(sorted(int(float(value)) for value in column_values)))
        print(column_values)
        return column_values


    def count_column_values_range(self, sheet_name, cell_range):
        sheet = self.workbook.Sheets(sheet_name)
        column_values = []
        for cell in sheet.Range(cell_range).Cells:
            cell_value = cell.Value
            if cell_value is not None:
                column_values.append(cell_value)
        column_values = [value.replace(',', '') for value in column_values]
        counts = {}
        total_count = 0
        for value in column_values:
            if value in counts:
                counts[value] += 1
            else:
                counts[value] = 1
            total_count += 1
        
        column_values = list(set(column_values))
        print(column_values)
    
    def get_value_in_column(self, sheet_name, column_letter):
        
        sheet = self.workbook.Sheets(sheet_name)
        column_values = []
        for row in range(2, sheet.UsedRange.Rows.Count + 1):
            cell_value = sheet.Cells(row, ord(column_letter) - 64).Value
            if cell_value is not None:
                column_values.append(cell_value)
        counts = {}
        total_count = 0
        for value in column_values:
            if value in counts:
                counts[value] += 1
            else:
                counts[value] = 1
            total_count += 1
        
        column_values = list((sorted(int(float(value)) for value in column_values)))
        print(column_values)
        return column_values
    
    def detect_function(self, sheet_name, range_row, column_range):
        sheet = self.workbook.Sheets(sheet_name)
        row_count = sheet.UsedRange.Rows.Count
        data = []
        i = range_row
        start_column = ord(column_range[0])
        end_column = ord(column_range[2])
        while i <= row_count:
            all_empty = True
            for col in range(start_column, end_column + 1):
                cell_value = sheet.Cells(i, chr(col)).Value
                if cell_value is not None:
                    data.append(cell_value)
                    print(data)
                    all_empty = False
            if all_empty:
                break
            i += 3
        return data
    
        
        

    
        
    
    