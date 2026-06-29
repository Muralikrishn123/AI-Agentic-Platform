import os
import shutil
import zipfile

def create_source_zip(workspace_root, zip_output_path):
    print(f"Zipping source code directly to {zip_output_path}...")
    excludes_dirs = {'node_modules', '.venv', 'venv', '__pycache__', '.git', 'dist', '.system_generated', '.tempmediaStorage'}
    excludes_files = {'agentic_platform.db', '.env', 'platform_architecture.png'}
    excludes_extensions = {'.pyc', '.pyo', '.log'}
    
    with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for folder_name in ['backend', 'frontend']:
            folder_path = os.path.join(workspace_root, folder_name)
            if not os.path.exists(folder_path):
                continue
                
            for root, dirs, files in os.walk(folder_path):
                # Filter out excluded directories in-place
                dirs[:] = [d for d in dirs if d not in excludes_dirs]
                
                for file in files:
                    if file in excludes_files or any(file.endswith(ext) for ext in excludes_extensions):
                        continue
                        
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, workspace_root)
                    zip_file.write(full_path, rel_path)

def create_submission_package():
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    submission_dir = os.path.join(workspace_root, "Agentic_AI_Platform_Submission")
    
    print(f"Creating submission folder structure at: {submission_dir}")
    
    # 1. Create Folder Structure
    dirs_to_create = [
        os.path.join(submission_dir, "01_Demo_Video"),
        os.path.join(submission_dir, "02_Architecture"),
        os.path.join(submission_dir, "03_Code"),
        os.path.join(submission_dir, "04_Documentation")
    ]
    
    for d in dirs_to_create:
        os.makedirs(d, exist_ok=True)
        
    # 2. Add placeholder in Demo Video directory
    with open(os.path.join(submission_dir, "01_Demo_Video", "PLACEHOLDER.txt"), "w") as f:
        f.write("Place your 5-minute Demo.mp4 video file in this directory.\nEnsure it is strictly less than 5 MB.\n")

    # 3. Copy Architecture files
    src_arch_md = os.path.join(workspace_root, "ARCHITECTURE.md")
    dest_arch_md = os.path.join(submission_dir, "02_Architecture", "Architecture.md")
    if os.path.exists(src_arch_md):
        shutil.copy(src_arch_md, dest_arch_md)
        print("Copied ARCHITECTURE.md to 02_Architecture/Architecture.md")
        
    src_arch_png = os.path.join(workspace_root, "platform_architecture.png")
    dest_arch_png = os.path.join(submission_dir, "02_Architecture", "platform_architecture.png")
    if os.path.exists(src_arch_png):
        shutil.copy(src_arch_png, dest_arch_png)
        print("Copied platform_architecture.png to 02_Architecture/platform_architecture.png")
        
    # 4. Copy README documentation
    src_readme = os.path.join(workspace_root, "README.md")
    dest_readme = os.path.join(submission_dir, "04_Documentation", "README.md")
    if os.path.exists(src_readme):
        with open(src_readme, "r", encoding="utf-8") as f:
            content = f.read()
            
        hackathon_header = """# 🏆 Hackathon Submission Details

## 👥 Team Information
*   **Team Name**: [Fill in your Team Name]
*   **Team Members**: 
    1. [Member 1 Name] - [Role/Email]
    2. [Member 2 Name] - [Role/Email]
*   **Submission Date**: Monday, 29 June 2026

## 🌐 GitHub Repository Link
*   **Repository URL**: https://github.com/Muralikrishn123/AI-Agentic-Platform/

---

"""
        with open(dest_readme, "w", encoding="utf-8") as f:
            f.write(hackathon_header + content)
        print("Created README.md in 04_Documentation/README.md with Hackathon headers.")

    # 5. Zip Source Code directly
    zip_output_path = os.path.join(submission_dir, "03_Code", "SourceCode.zip")
    create_source_zip(workspace_root, zip_output_path)
    print("Source code successfully zipped into 03_Code/SourceCode.zip")

    # Get size of zip file
    zip_size_mb = os.path.getsize(zip_output_path) / (1024 * 1024)
    print(f"Zip File Size: {zip_size_mb:.2f} MB (Must be < 10 MB)")
    
if __name__ == "__main__":
    create_submission_package()
