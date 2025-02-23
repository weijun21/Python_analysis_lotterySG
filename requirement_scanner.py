import os
import re
import sys
import pkgutil
import importlib.util
import stdlib_list

def get_local_python_files(root):
    """Find all Python files in the folder (excluding built-in modules)."""
    local_files = set()
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                module_name = os.path.splitext(filename)[0]
                local_files.add(module_name)
    return local_files

def scan_folder_for_imports(root):
    """
    Recursively scan all .py files in the project folder and extract imported modules.
    """
    modules = set()
    pattern_import = re.compile(r'^\s*import\s+([\w\.]+)', re.MULTILINE)
    pattern_from = re.compile(r'^\s*from\s+([\w\.]+)\s+import\s+', re.MULTILINE)

    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith('.py'):
                path = os.path.join(dirpath, filename)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Find "import module" and "from module import ..."
                    imports = pattern_import.findall(content)
                    from_imports = pattern_from.findall(content)
                    for imp in imports:
                        modules.add(imp.split('.')[0])  # Get the top-level module
                    for frm in from_imports:
                        modules.add(frm.split('.')[0])  # Get the top-level module
                except Exception as e:
                    print(f"Error processing file {path}: {e}")
    return modules

def filter_third_party_modules(modules):
    """
    Remove standard library modules and local project files from the imports list.
    """
    # Get the list of standard library modules dynamically
    std_lib = set(stdlib_list.stdlib_list())

    # Get all Python files in the project folder
    local_files = get_local_python_files(os.getcwd())

    # Remove standard library and local modules
    third_party_modules = {mod for mod in modules if mod not in std_lib and mod not in local_files}

    return third_party_modules

def generate_requirements_file():
    """
    Scan for third-party dependencies and generate a requirements.txt file.
    """
    root = os.getcwd()
    all_modules = scan_folder_for_imports(root)
    required_modules = sorted(filter_third_party_modules(all_modules))

    # Write the module names to requirements.txt
    with open("requirements.txt", "w", encoding="utf-8") as f:
        for module in required_modules:
            f.write(module + "\n")

    print("✅ requirements.txt generated with the following third-party modules:")
    for module in required_modules:
        print(f"  - {module}")

if __name__ == "__main__":
    generate_requirements_file()
