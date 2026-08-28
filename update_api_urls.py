import os
import re

ui_dir = r"c:\Users\ldgd2\OneDrive\Documentos\Proyectos_lider\python\Cotizador\src\web\UI"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements
    # fetch('/api/...
    content = re.sub(r"fetch\('/api/", r"fetch((window.ENV?.API_BASE_URL || '') + '/api/", content)
    
    # fetch(`/api/...
    content = re.sub(r"fetch\(`/api/", r"fetch(`${window.ENV?.API_BASE_URL || ''}/api/", content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

for root, dirs, files in os.walk(ui_dir):
    for file in files:
        if file.endswith('.js'):
            filepath = os.path.join(root, file)
            process_file(filepath)
            
print("Done!")
