import inspect

def debug_print(message):
    frame = inspect.currentframe().f_back
    path_to_file = frame.f_code.co_filename
    filename = path_to_file.split('/')[-1]
    
    line_number = frame.f_lineno
    print(f"[DEBUG] {filename}:{line_number} {message}")