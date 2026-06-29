import base64
import os

def embed_image_in_markdown():
    workspace_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    image_path = os.path.join(workspace_root, "Agentic_AI_Platform_Submission", "02_Architecture", "platform_architecture.png")
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        return
        
    print(f"Reading image from {image_path}...")
    with open(image_path, "rb") as img_file:
        img_data = img_file.read()
        base64_data = base64.b64encode(img_data).decode("ascii")
        
    data_url = f"data:image/png;base64,{base64_data}"
    
    # Files to update
    files_to_update = [
        os.path.join(workspace_root, "ARCHITECTURE.md"),
        os.path.join(workspace_root, "Agentic_AI_Platform_Submission", "02_Architecture", "Architecture.md")
    ]
    
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            print(f"Warning: File not found at {file_path}")
            continue
            
        print(f"Embedding image in {file_path}...")
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Replace the image references with the base64 data url
        target_ref_root = "![System Architecture](Agentic_AI_Platform_Submission/02_Architecture/platform_architecture.png)"
        target_ref_sub = "![System Architecture](platform_architecture.png)"
        
        updated_content = content.replace(target_ref_root, f"![System Architecture]({data_url})")
        updated_content = updated_content.replace(target_ref_sub, f"![System Architecture]({data_url})")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
            
    print("Success! The visual diagram has been embedded directly inside the Markdown files as a Base64 data URL. They are now 100% self-contained.")

if __name__ == "__main__":
    embed_image_in_markdown()
