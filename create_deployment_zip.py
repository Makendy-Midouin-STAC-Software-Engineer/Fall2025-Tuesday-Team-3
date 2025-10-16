#!/usr/bin/env python3
"""
Create a proper deployment ZIP for AWS Elastic Beanstalk
This ensures forward slashes are used in paths (Linux-compatible)
"""
import zipfile
import os
from pathlib import Path

def create_deployment_zip():
    # Files and directories to include
    items_to_include = [
        'inspections',
        'safe_eats_backend',
        '.ebextensions',
        'staticfiles',
        'manage.py',
        'requirements.txt',
        '.ebignore'
    ]
    
    output_file = 'safeeats-deploy.zip'
    
    print(f"Creating {output_file}...")
    
    with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in items_to_include:
            item_path = Path(item)
            
            if not item_path.exists():
                print(f"Warning: {item} not found, skipping...")
                continue
            
            if item_path.is_file():
                # Add single file with forward slashes
                arcname = item.replace('\\', '/')
                zipf.write(item, arcname=arcname)
                print(f"  Added: {arcname}")
            else:
                # Add directory recursively with forward slashes
                for root, dirs, files in os.walk(item):
                    # Skip __pycache__ and .pyc files
                    dirs[:] = [d for d in dirs if d != '__pycache__']
                    
                    for file in files:
                        if file.endswith('.pyc'):
                            continue
                        
                        file_path = os.path.join(root, file)
                        # Use forward slashes for ZIP archive
                        arcname = file_path.replace('\\', '/')
                        zipf.write(file_path, arcname=arcname)
                        print(f"  Added: {arcname}")
    
    # Verify the zip was created
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        print(f"\n✅ Success! Created {output_file} ({size:,} bytes)")
        print(f"\nUpload this file to AWS Elastic Beanstalk:")
        print(f"  {os.path.abspath(output_file)}")
    else:
        print("\n❌ Error: ZIP file was not created")

if __name__ == '__main__':
    create_deployment_zip()

