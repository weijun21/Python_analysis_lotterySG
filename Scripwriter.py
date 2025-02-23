import os
import ast
import re
class BackendScriptWriter:

    def write_script(self, script_name, script_content):
        self.script_content = script_content           
        script_path = os.path.join(os.getcwd(),script_name)
        with open(script_path, "w") as f:
            f.write(self.script_content)
        print("Script written successfully!")
     #replace old code in new code
    def replace_script(self, target_script_name, target_code, new_code):
        
        target_script_path = os.path.join(os.getcwd(), target_script_name)
        with open(target_script_path, "r") as f:
            target_script_content = f.read()
        updated_script_content = target_script_content.replace(target_code, new_code)
        with open(target_script_path, "w") as f:
            f.write(updated_script_content)

        if target_script_name not in os.listdir(os.getcwd()):
            print("Script not found.")
        if target_code in updated_script_content:
            print("Code updated successfully!")
        else:
            print("Code not found.")
        
        
        return updated_script_content
    #use ast module, update content in variable


    def overwritelist_script(self,target_script_name, variable_name, values):
        """
    Overwrite the values of a variable in a Python script, specifically for lists.

    Arguments:
    - target_script_name: The name of the script to modify (including file extension).
    - variable_name: The name of the variable (list) to overwrite.
    - values: A list of values to assign to the variable.
    """
        target_script_path = os.path.join(os.getcwd(), target_script_name)
    
    # Ensure the script exists
        if not os.path.exists(target_script_path):
            raise FileNotFoundError(f"Script {target_script_name} not found in the current directory.")
    
    # Read the existing content of the target script
        with open(target_script_path, "r") as f:
            target_script_content = f.read()
    
    # Parse the script into an AST
        tree = ast.parse(target_script_content)
    
    # Flag to track if we find the variable assignment
        variable_found = False
    
    # Traverse the AST and modify the list variable
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.targets[0], ast.Name) and node.targets[0].id == variable_name:
                    variable_found = True
                # Check if the assigned value is a list
                    if isinstance(node.value, ast.List):
                    # Create new list elements with the provided values
                        node.value.elts = [ast.Constant(value=v) for v in values]
                    else:
                    # Handle non-list assignments (e.g., strings, integers, etc.)
                        node.value = ast.Constant(value=values)  # Convert values to a constant
                    break  # Exit the loop once we've modified the variable
    
        if not variable_found:
            raise ValueError(f"Variable '{variable_name}' not found in the script.")
    
    # Write the modified AST back to the file
        with open(target_script_path, "w") as f:
            f.write(ast.unparse(tree))  # Ensure you're using Python 3.9+ for ast.unparse
            print(f"Variable '{variable_name}' overwritten successfully with new values!")


    #list_append_script with ast module, update content in list variable
    def list_update_script(self, target_script_name, variable_name, new_value):
        if not isinstance(new_value, list):
            raise ValueError("new_value must be a list")
        
    
        target_script_path = os.path.join(os.getcwd(), target_script_name)
        with open(target_script_path, "r") as f:
            target_script_content = f.read()
    
        tree = ast.parse(target_script_content)
    
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if node.targets[0].id == variable_name:
                    node.value.elts.extend([ast.Num(n=x) for x in new_value])
                    break
    
        updated_script_content = ast.unparse(tree)
    
        with open(target_script_path, "w") as f:
            f.write(updated_script_content)
    
        print("Variable list updated successfully!")

    
    def delete_script(self, script_name):
        script_path = os.path.join(os.getcwd(), script_name)
        if script_name in os.listdir(os.getcwd()):
            os.remove(script_path)
            print("Script deleted successfully!")
        else:
            print("Script not found.")

    def extract_value_from_ast(self, node):
        """
        Extracts the value from an AST node (supports both literals and variables).
        """
        if isinstance(node, ast.Constant):  # Python 3.9+
            return node.value
        elif isinstance(node, ast.Num):  # Older Python versions (<3.9)
            return node.n
        else:
            print(f"Unsupported AST Node Type: {type(node)}")
            return None





    def get_values_from_list(self, script_name, list_name):
        """
    Load a Python script, parse it using the ast module, and extract values from the given list.
    Prints the values found in the list directly from this function.
    
    Arguments:
    - script_name: The name of the Python script file (relative to the current working directory).
    - list_name: The name of the list variable to extract values from.
    """
    # Get the current working directory and construct script path
        script_path = os.path.join(os.getcwd(), script_name)
    
    # Check if the file exists
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script {script_name} not found in the current directory.")
    
    # Read and parse the script content
        with open(script_path, 'r') as f:
            script_content = f.read()
        tree = ast.parse(script_content)
    
    # Search for the list variable in the AST
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == list_name:
                        value_list = node.value
                        if isinstance(value_list, ast.List):
                            print(f"Values in {list_name}:")
                            for element in value_list.elts:
                                if isinstance(element, ast.Constant):  # Handle constant elements (e.g., 1, 'a', 5.5)
                                    print(element.value)
                                elif isinstance(element, ast.Name):  # Handle variable names (e.g., x, my_var)
                                    print(f"Variable: {element.id}")
                                else:
                                    print(f"Expression: {ast.dump(element)}")  # Handle complex expressions
                            return  # Exit after processing the list
    
        print(f"List '{list_name}' not found in the script.")


    def get_total_list_value(self, script_name, variable_name):
        target_script_path = os.path.join(os.getcwd(), script_name)
        
        with open(target_script_path, "r") as f:
            target_script_content = f.read()
        
        # Parse the content into an AST (Abstract Syntax Tree)
        tree = ast.parse(target_script_content)
        
        # Step 1: Retrieve the list assigned to the variable_name
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.targets[0], ast.Name) and node.targets[0].id == variable_name:
                    if isinstance(node.value, (ast.List, ast.Tuple)):  # Handle both list and tuple types
                        # Extract values from the list or tuple
                        values = [self.resolve_value_from_ast(element, tree) for element in node.value.elts]
                        print(f"Values in list {variable_name}: {values}")
                        return values
        
        print(f"Variable {variable_name} not found or not a list in {script_name}.")
        return []

    def resolve_value_from_ast(self, node, tree):
        """
        Resolves the value from an AST node.
        If the node is a variable (ast.Name), we find its value in the script.
        If the value is another list, we resolve it recursively.
        """
        if isinstance(node, ast.Constant):  # Python 3.9+
            return node.value
        elif isinstance(node, ast.Num):  # Older Python versions (<3.9)
            return node.n
        elif isinstance(node, ast.Name):  # If it's a variable, find its value
            variable_value = self.get_variable_value(node.id, tree)
            return variable_value
        else:
            print(f"Unsupported AST Node Type: {type(node)}")
            return None

    def get_variable_value(self, variable_name, tree):
        """
        Finds the value assigned to the variable_name in the AST tree.
        If the variable is a list, it resolves it recursively.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.targets[0], ast.Name) and node.targets[0].id == variable_name:
                    if isinstance(node.value, (ast.List, ast.Tuple)):  # Check if it's a list
                        return [self.resolve_value_from_ast(el, tree) for el in node.value.elts]
                    elif isinstance(node.value, ast.Name):  # If it's another variable, resolve its value
                        return self.get_variable_value(node.value.id, tree)
                    else:
                        return self.resolve_value_from_ast(node.value, tree)  # Handle other types of assignments
        print(f"Variable {variable_name} not found.")
        return []


                                 
    def readlist_script(self,script_name, list_name):
        with open(script_name, 'r') as f:
            script = f.read()
        script = ast.parse(script)
        print("Script parsed successfully!")
        print(script)
        for node in ast.walk(script):
            if isinstance(node, ast.Assign):
             if node.targets[0].id == list_name:
                return ast.literal_eval(node.value)
        print("List not found.")
        return None
    def extract_percentage_from_string(value_str):
        """
    Extract the percentage value from a string in the format 'Value X: (Y%)'.
    
    Arguments:
    - value_str: A string in the format 'Value X: (Y%)'.
    
    Returns:
    - The numeric value of the percentage (as float).
    """
    # Use regex to extract the number inside the parentheses
        match = re.search(r'\((\d+\.\d+)%\)', value_str)
        if match:
            return float(match.group(1))  # Return the extracted percentage as a float
        return 0.0  # Return 0 if no match is found

    def variable_count_list(self, script_name, list_name):
        """
    Load a Python script, parse it using the ast module, and count occurrences of variable references inside the given list.
    
    Arguments:
    - script_name: The name of the Python script file.
    - list_name: The name of the list variable to analyze.
    
    Returns:
    - Count of variable references (element.id occurrences) inside the list.
    """
        script_path = os.path.join(os.getcwd(), script_name)
    
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script {script_name} not found in the current directory.")
    
        with open(script_path, 'r') as f:
            script_content = f.read()
    
        tree = ast.parse(script_content)
        variable_count = 0  # Counter for element.id occurrences
    
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == list_name:
                        value_list = node.value
                        if isinstance(value_list, ast.List):
                            for element in value_list.elts:
                                if isinstance(element, ast.Name):  # Count occurrences of variable names
                                    variable_count += 1
    
        print(f"Number of variable references (element.id) inside '{list_name}': {variable_count}")
        return variable_count

    def variable_get_count(self, script_name, list_name):
        """
    A shorter function to count variable references in a list.
    
    Arguments:
    - script_name: The Python script file name.
    - list_name: The list variable name to analyze.
    
    Returns:
    - Count of variable references.
    """
        script_path = os.path.join(os.getcwd(), script_name)
        if not os.path.exists(script_path):
            return 0
    
        with open(script_path, 'r') as f:
            tree = ast.parse(f.read())
    
        return sum(1 for node in ast.walk(tree) if isinstance(node, ast.Assign) 
               for target in node.targets if isinstance(target, ast.Name) and target.id == list_name 
               for element in getattr(node.value, 'elts', []) if isinstance(element, ast.Name))
