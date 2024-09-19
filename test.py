import os, json
from colorama import init, Fore, Style

init()

def getErrorsInFile(file: str) -> int:
    if file.endswith('.html'):
        os.system(f'java -jar vnu.jar --errors-only "{file}" > tmp/out.txt 2>&1')

        with open('tmp/out.txt', 'rb') as f:
            CONTENT = f.read()

        errors = CONTENT.strip().split(b'\n')
        return [stripNonAscii(error).strip(" \"") for error in errors if error.strip() != b'']

    # handling for CSS files
    os.system(f'java -jar css-validator.jar file:///{os.path.abspath(file)} --output=json > tmp/out.txt 2>&1')
    with open('tmp/out.txt', 'r') as f:
        data = '{"cssvalidation' + (f.read().split('cssvalidation')[1])
        jsondata = json.loads(data)
        return [f"{error['source']}: {error['message']} on line {error['line']}" for error in jsondata['cssvalidation']['errors']]

def stripNonAscii(data: bytes) -> str:
    decoded_str = data.decode('utf-8', errors='ignore')
    return ''.join(char for char in decoded_str if ord(char) < 128)

data: dict[str, dict[int, list]] = {}


for root, dirs, files in os.walk('auto-validator'):
    for file in files:
        if file.endswith(('.html', '.css')):
            file_path = os.path.join(root, file)
            errors = getErrorsInFile(file_path)

            # VERY JANK CODE
            project_name = file_path.split('auto-validator\\')[1].split('\\')[0]
            student_name = file_path.split(f'{project_name}\\')[1].split('\\')[0]
            student_name = student_name.replace(project_name.replace('-submissions', ''), '').strip('- ').split('-student')[0]
            # ==============

            if student_name not in data:
                print(f"Creating student {student_name}")
                data[student_name] = {
                    'files': [],
                    'total_errors': 0
                }

            data[student_name]['files'].append({
                'type': '.html' if file.endswith('.html') else '.css',
                'errors': errors
            })
            data[student_name]['total_errors'] += len(errors)
            print(f'File: {file_path}, Errors: {len(errors)} {data[student_name]['total_errors']} ({student_name})')

print('-'*50)
print(f"\nParsed {len(data)} projects!")

for s in data:
    student = data[s]
    print(f"{Fore.CYAN}{s}{Style.RESET_ALL}")
    print(f"{Fore.RED}  - Errors ({student['total_errors']}): {Style.RESET_ALL}")
    for file in student['files']:
        for error in file['errors']:
            print(f"    - {error}")
