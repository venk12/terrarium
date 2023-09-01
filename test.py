import re

def remove_comments_and_descriptions(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    cleaned_lines = []
    inside_docstring = False
    
    for line in lines:
        stripped_line = line.strip()

        # For multi-line comments starting/ending
        if stripped_line.startswith('"""') or stripped_line.startswith("'''"):
            inside_docstring = not inside_docstring
            cleaned_lines.append('\n')  # Preserve the line number by appending a newline
            continue

        # If we are inside a multi-line comment, skip this line but keep the newline for line number preservation
        if inside_docstring:
            cleaned_lines.append('\n')
            continue

        # Remove inline comments but keep the line's original indentation
        line_without_comments = re.sub(r'#.*$', '', line)
        
        # Add the cleaned line to the results
        cleaned_lines.append(line_without_comments)

    return ''.join(cleaned_lines)

# For testing purposes:
# file_path = "your_file_path_here"
# print(remove_comments_and_descriptions(file_path))




temp_file = '/Users/giovannichiementin/Desktop/Terra/terra-monorepo/temp.py'
cleaned_code = remove_comments_and_descriptions('/Users/giovannichiementin/Desktop/Terra/terra-monorepo/ESP32_repo/ESP32/utils.py')
with open(temp_file, 'w') as file:
    file.write(cleaned_code)
