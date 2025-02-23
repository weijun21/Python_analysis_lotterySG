import os
from Scripwriter import BackendScriptWriter
import win32com.client
from ExcelMacroRunner import excel_functions
import openpyxl
from lib_function import Lib_functions,total_list_cal_script
from words_Main_controller import ExcelToWordConverter
from Summary_percentage_writer import summary_percentage_writer
from table_analysis import TablesAnalysis  
from Data_graph_writer import TableAnalysisExtractor
from database_analysis import TotoDataFetcher

import win32com.client

try:
    excel = win32com.client.GetActiveObject("Excel.Application")
    excel.Quit()
    print("Excel application closed.")
except Exception as e:
    print("No active Excel instance found or error closing Excel:", e)

toto_data_fetcher=TotoDataFetcher()
toto_data_fetcher.run()
excel_func=excel_functions()
startup=BackendScriptWriter()
startup.overwritelist_script('Data_Storage_Lib.py', 'C',excel_func.count_column_values('Data', 'C'))
startup.overwritelist_script('Data_Storage_Lib.py', 'D',excel_func.count_column_values('Data', 'D'))
startup.overwritelist_script('Data_Storage_Lib.py', 'E',excel_func.count_column_values('Data', 'E'))
startup.overwritelist_script('Data_Storage_Lib.py', 'F',excel_func.count_column_values('Data', 'F'))
startup.overwritelist_script('Data_Storage_Lib.py', 'G',excel_func.count_column_values('Data', 'G'))
startup.overwritelist_script('Data_Storage_Lib.py', 'H',excel_func.count_column_values('Data', 'H'))
startup.overwritelist_script('Data_Storage_Lib.py', 'I',excel_func.count_column_values('Data', 'I'))
lib_fun=Lib_functions('All')
lib_fun21=total_list_cal_script()
lib_fun21.total_list_percent_calculation()    
excel_converter=ExcelToWordConverter()
excel_converter.short_prob_scanner('database_analysis.xlsx', 'Data', 'B', 'I',5) #remember this should include date column which is B
Summary_percentage=summary_percentage_writer()
Summary_percentage.run()
TablesAnalysis_x=TablesAnalysis()
TablesAnalysis_x.run()
graph_extraction=TableAnalysisExtractor()
graph_extraction.run()


try:
    excel = win32com.client.GetActiveObject("Excel.Application")
    excel.Quit()
    print("Excel application closed.")
except Exception as e:
    print("No active Excel instance found or error closing Excel:", e)

