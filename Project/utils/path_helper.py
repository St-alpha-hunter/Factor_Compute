import os 

def get_project_root() -> str:
    try:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    except NameError:
        return os.path.abspath(os.path.join(os.getcwd(), ".."))
    
def get_data_path(filename):
    return os.path.join(get_project_root(), "data", filename)

