import ast
import os

def get_imports_from_file(file_path):
    """Extract imports from a single Python file."""
    with open(file_path, "r") as f:
        tree = ast.parse(f.read())

    return sorted({
        node.names[0].name.split('.')[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)
    })

def get_all_python_files(directory):
    """Recursively get all Python files in a directory."""
    py_files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.py'):
                py_files.append(os.path.join(dirpath, filename))
    return py_files

def generate_requirements(directory, output_file="requirements.txt"):
    """Generate a requirements.txt from all Python files in the directory."""
    all_imports = set()
    
    # Get all Python files in the directory
    python_files = get_all_python_files(directory)

    # Extract imports from each file
    for py_file in python_files:
        imports = get_imports_from_file(py_file)
        all_imports.update(imports)

    # Write the sorted imports to the requirements.txt file
    with open(output_file, "w") as f:
        for package in sorted(all_imports):
            f.write(package + "\n")

    print(f"requirements.txt generated in {output_file}")

# Specify your product directory
product_directory = r"C:\Users\sachi\python\3-DAT-dont-open\assigment\product"

# Generate the requirements.txt file
generate_requirements(product_directory)
