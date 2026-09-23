import os
import zipfile

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        # Exclude directories
        if 'new_venv' in dirs:
            dirs.remove('new_venv')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            if file.endswith('.pyc') or file == 'savix_ai_deployment.zip':
                continue
            
            file_path = os.path.join(root, file)
            # Add file to zip archive, with relative path
            ziph.write(file_path, os.path.relpath(file_path, path))

if __name__ == '__main__':
    project_dir = r"C:\Users\Hp\OneDrive\Desktop\savix_ai (management)\savix_ai\savix_ai"
    zip_path = os.path.join(project_dir, "savix_ai_deployment.zip")
    
    print(f"Creating deployment zip at {zip_path}...")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(project_dir, zipf)
    print("Done! Ready for upload to PythonAnywhere.")
