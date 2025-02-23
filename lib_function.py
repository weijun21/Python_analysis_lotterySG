import os
from Scripwriter import BackendScriptWriter
import ast
from ExcelMacroRunner import excel_functions
import matplotlib.pyplot as plt
import openpyxl
import win32com.client
import docx 
import re
from collections import defaultdict
from Math_util import MathUtils
      

class Lib_functions:
    def __init__(self,list_activation):
        self.Lib_list_name = {
            'list1': ['C', 'list_percent1', 'list_highest1','list_lowest1'],
            'list2': ['D', 'list_percent2', 'list_highest2','list_lowest2'],
            'list3': ['E', 'list_percent3', 'list_highest3','list_lowest3'],
            'list4': ['F', 'list_percent4', 'list_highest4','list_lowest4'],
            'list5': ['G', 'list_percent5', 'list_highest5','list_lowest5'], # Add more lists as needed],
            'list6': ['H', 'list_percent6', 'list_highest6','list_lowest6'],
            'list7': ['I', 'list_percent7', 'list_highest7','list_lowest7'],
        }
        self.filename = "Data_storage_Lib.py"  # Replace with your filename
        self.list_activation = list_activation
        keys = list(self.Lib_list_name.keys())
        for key in keys:
                self.list_name = self.Lib_list_name[key][0]
                self.store_data_list = self.Lib_list_name[key][1]
                self.store_list_highest = self.Lib_list_name[key][2]
                self.store_list_lowest = self.Lib_list_name[key][3]
        

    def list_percent_function(self):
        scriptcalculator = BackendScriptWriter()
        excel_activation = excel_functions()

        if self.list_activation == "All":
            keys = list(self.Lib_list_name.keys())
            for key in keys:
                self.list_name = self.Lib_list_name[key][0]
                self.store_data_list = self.Lib_list_name[key][1]
                self.store_list_highest = self.Lib_list_name[key][2]
                self.store_list_lowest = self.Lib_list_name[key][3]

                list_values = excel_activation.get_value_in_column('Data', self.list_name)

                total_sum = len(list_values)  # Calculate the total sum correctly
                print(total_sum)
                print("Total sum:", total_sum)
                i = 0
                percent_list = []
                percent_highest = {}
                percent_lowest={}
                count_value = excel_activation.get_value_in_column('Data', self.list_name)

                value_counts = {}  # Create a dictionary to store the count of each value
                for value in count_value:
                    if value in value_counts:
                        value_counts[value] += 1
                    else:
                        value_counts[value] = 1

                for value, count in value_counts.items():
                    percent = (count / len(count_value)) * 100  # Calculate the percentage for each group
                    print(f"Value {value}: ({percent:.2f}%)")
                    percent_list.append(f"Value {value}: ({percent:.2f}%)")
                    percent_highest[value] = percent
                    percent_lowest [value]=percent

                percent_2 = percent_list
                top_3_percent_highest = sorted(percent_highest.items(), key=lambda x: x[1], reverse=True)[:3]
                top_3_percent_lowest = sorted(percent_highest.items(), key=lambda x: x[1])[:3]
                scriptcalculator.overwritelist_script(self.filename, self.store_data_list, percent_2)
                scriptcalculator.overwritelist_script(self.filename, self.store_list_highest, top_3_percent_highest)
                scriptcalculator.overwritelist_script(self.filename, self.store_list_lowest, top_3_percent_lowest)
                
                print("Percentages calculated and stored in the list.")

        else:
            self.list_name = self.Lib_list_name[self.list_activation][0]
            self.store_data_list = self.Lib_list_name[self.list_activation][1]
            self.store_list_highest = self.Lib_list_name[self.list_activation][2]

            list_values = excel_activation.get_value_in_column('Data', self.list_name)

            total_sum = len(list_values)  # Calculate the total sum correctly
            print(total_sum)
            print("Total sum:", total_sum)
            i = 0
            percent_list = []
            percent_highest = {}
            percent_lowest={}
            count_value = excel_activation.get_value_in_column('Data', self.list_name)

            value_counts = {}  # Create a dictionary to store the count of each value
            for value in count_value:
                if value in value_counts:
                    value_counts[value] += 1
                else:
                    value_counts[value] = 1

            for value, count in value_counts.items():
                percent = (count / len(count_value)) * 100  # Calculate the percentage for each group
                print(f"Value {value}: ({percent:.2f}%)")
                percent_list.append(f"Value {value}: ({percent:.2f}%)")
                percent_highest[value] = percent
                percent_lowest [value]=percent

            percent_2 = percent_list
            top_3_percent_highest = sorted(percent_highest.items(), key=lambda x: x[1], reverse=True)[:3]
            top_3_percent_lowest = sorted(percent_highest.items(), key=lambda x: x[1])[:3]
            scriptcalculator.overwritelist_script(self.filename, self.store_data_list, percent_2)
            scriptcalculator.overwritelist_script(self.filename, self.store_list_highest, top_3_percent_highest)
            scriptcalculator.overwritelist_script(self.filename, self.store_list_lowest, top_3_percent_lowest)
            
            print("Percentages calculated and stored in the list.")

            return percent_2, top_3_percent_highest, top_3_percent_lowest
        
        
    def plot_graph(self):
                scriptcalculator = BackendScriptWriter()
                list_highest = scriptcalculator.readlist_script(self.filename , self.store_list_highest)
                list_lowest = scriptcalculator.readlist_script(self.filename , self.store_list_lowest)
            
                x_highest = [value for value, _ in list_highest]
                y_highest = [percent for _, percent in list_highest]
            
                x_lowest = [value for value, _ in list_lowest]
                y_lowest = [percent for _, percent in list_lowest]
            
                plt.plot(x_highest, y_highest, color='blue', label='Highest')
                plt.plot(x_lowest, y_lowest, color='red', label='Lowest')
                #line style
                plt.plot(x_highest, y_highest, 'o', color='blue')
                plt.plot(x_lowest, y_lowest, 'o', color='red')
    
                # Calculate the middle line
                y_middle = [(y_highest[i] + y_lowest[i]) / 2 for i in range(len(y_highest))]
    
                # Plot the middle line
                plt.plot(x_highest, y_middle, color='black', label='Middle')
    
                # Formula for the middle line
                print("Formula for the middle line: y = (y_highest + y_lowest) / 2")
    
                plt.xlabel('Value')
                plt.ylabel('Percentage')
                plt.title('Highest and Lowest Percentages')
                plt.legend()
                plt.show()



class total_list_cal_script:
    def total_list_percent_calculation(self):
        """
    Calculate the total percentage sum for each list (from list1 to list7).
    The sum of the percentages is then divided by 7 to normalize it (since there are 7 lists).
    """
        x = BackendScriptWriter()
        Math=MathUtils()
        L = x.get_total_list_value('Data_storage_Lib.py', 'list_percent_call_all')
    
        lists = Math.extract_and_combine_percentages(L)
        if not lists:
            print("No lists found in the script.")
            return []
    
        total_percent = x.variable_get_count('Data_storage_Lib.py', 'list_percent_call_all')
        if total_percent == 0:
            print("Total percentage count is zero, cannot normalize.")
            return []
    
        final_percentages = [f'{value_name}: ({(total / total_percent) :.2f}%)' for value_name, total in lists]
        sorted_percentage = sorted(final_percentages, key=lambda x: float(x.split(':')[1].strip().replace('(', '').replace(')', '').replace('%', '')), reverse=True)
        sorted_highest_three = sorted_percentage[:3]
        sorted_lowest_three = sorted_percentage[-3:]
        x.overwritelist_script('Data_storage_Lib.py', 'total_percent_list', sorted_percentage)
        x.overwritelist_script('Data_storage_Lib.py', 'total_percent_highest3', sorted_highest_three)
        x.overwritelist_script('Data_storage_Lib.py', 'total_percent_lowest3', sorted_lowest_three)
    
        print("Normalized Percentages for all lists:")
        for percentage in final_percentages:
            print(percentage)
    
    
    
        return final_percentages