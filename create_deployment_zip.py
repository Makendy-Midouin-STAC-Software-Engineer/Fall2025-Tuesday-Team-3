#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create a proper deployment ZIP for AWS Elastic Beanstalk
This script:
1. Builds the frontend
2. Collects static files
3. Creates a deployment zip with only relevant files
"""
import zipfile
import os
import subprocess
import sys
import shutil
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def run_command(cmd, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        print(f"\n❌ Error: Command failed with exit code {result.returncode}")
        sys.exit(1)
    return result


def build_frontend():
    """Build the React frontend."""
    print("\n📦 Building frontend...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("❌ Error: frontend directory not found")
        sys.exit(1)
    
    # Install dependencies if node_modules doesn't exist
    if not (frontend_dir / "node_modules").exists():
        print("Installing frontend dependencies...")
        run_command("npm install", cwd=frontend_dir)
    
    # Build the frontend
    run_command("npm run build", cwd=frontend_dir)
    
    # Copy built files to staticfiles
    dist_dir = frontend_dir / "dist"
    if dist_dir.exists():
        print(f"\n📋 Copying built frontend to staticfiles...")
        staticfiles_dir = Path("staticfiles")
        staticfiles_dir.mkdir(exist_ok=True)
        
        # Copy index.html
        if (dist_dir / "index.html").exists():
            shutil.copy2(dist_dir / "index.html", staticfiles_dir / "index.html")
            print(f"  ✓ Copied index.html")
        
        # Copy assets directory
        assets_src = dist_dir / "assets"
        assets_dst = staticfiles_dir / "assets"
        if assets_src.exists():
            if assets_dst.exists():
                shutil.rmtree(assets_dst)
            shutil.copytree(assets_src, assets_dst)
            print(f"  ✓ Copied assets directory")
        
        # Copy all other files from dist root (including images from public/)
        # Vite copies files from public/ to dist root during build
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']
        for file_path in dist_dir.iterdir():
            if file_path.is_file() and file_path.name != "index.html":
                # Copy image files and any other files from public/
                if file_path.suffix.lower() in image_extensions or not file_path.suffix:
                    shutil.copy2(file_path, staticfiles_dir / file_path.name)
                    print(f"  ✓ Copied {file_path.name}")


def collect_static():
    """Collect Django static files."""
    print("\n📦 Collecting Django static files...")
    # Use the same Python interpreter that launched this script to avoid env mismatches
    run_command(f'"{sys.executable}" manage.py collectstatic --noinput')


def create_deployment_zip():
    """Create the deployment ZIP file."""
    # Files and directories to include
    items_to_include = [
        "inspections",
        "safe_eats_backend",
        "staticfiles",
        "manage.py",
        "requirements.txt",
    ]
    
    # Optional items (only include if they exist)
    optional_items = [
        ".ebextensions",
        ".ebignore",
    ]
    
    # Add optional items if they exist
    for item in optional_items:
        if Path(item).exists():
            items_to_include.append(item)

    output_file = "safeeats-deploy.zip"

    # Remove old zip if it exists
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"\n🗑️  Removed old {output_file}")

    print(f"\n📦 Creating {output_file}...")

    # Patterns to exclude
    exclude_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".DS_Store",
        "Thumbs.db",
        "*.log",
        "node_modules",
        ".git",
        "venv",
        ".venv",
        "env",
        "ENV",
        "*.sqlite3",
        "*.sqlite3-journal",
    ]

    def should_exclude(file_path):
        """Check if a file should be excluded."""
        path_str = str(file_path).replace("\\", "/")
        for pattern in exclude_patterns:
            if pattern in path_str:
                return True
        return False

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for item in items_to_include:
            item_path = Path(item)

            if not item_path.exists():
                print(f"⚠️  Warning: {item} not found, skipping...")
                continue

            if item_path.is_file():
                if not should_exclude(item_path):
                    arcname = item.replace("\\", "/")
                    zipf.write(item, arcname=arcname)
                    print(f"  ✓ Added: {arcname}")
            else:
                # Add directory recursively
                for root, dirs, files in os.walk(item):
                    # Filter out excluded directories
                    dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]

                    for file in files:
                        file_path = Path(root) / file
                        if should_exclude(file_path):
                            continue

                        # Use forward slashes for ZIP archive
                        arcname = str(file_path).replace("\\", "/")
                        zipf.write(file_path, arcname=arcname)

    # Verify the zip was created
    if os.path.exists(output_file):
        size = os.path.getsize(output_file)
        size_mb = size / (1024 * 1024)
        print(f"\n{'='*60}")
        print(f"✅ Success! Created {output_file}")
        print(f"   Size: {size_mb:.2f} MB ({size:,} bytes)")
        print(f"\n📤 Upload this file to AWS Elastic Beanstalk:")
        print(f"   {os.path.abspath(output_file)}")
        print(f"{'='*60}")
    else:
        print("\n❌ Error: ZIP file was not created")
        sys.exit(1)


def main():
    """Main deployment process."""
    print("🚀 Starting SafeEats deployment preparation...")
    print(f"   Working directory: {os.getcwd()}")
    
    # Step 1: Build frontend
    try:
        build_frontend()
    except Exception as e:
        print(f"\n❌ Error building frontend: {e}")
        sys.exit(1)
    
    # Step 2: Collect static files
    try:
        collect_static()
    except Exception as e:
        print(f"\n❌ Error collecting static files: {e}")
        sys.exit(1)
    
    # Step 3: Create deployment zip
    try:
        create_deployment_zip()
    except Exception as e:
        print(f"\n❌ Error creating deployment zip: {e}")
        sys.exit(1)
    
    print("\n🎉 Deployment package ready!")


if __name__ == "__main__":
    main()
