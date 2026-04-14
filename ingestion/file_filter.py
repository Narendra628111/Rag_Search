import os
SUPPORTED_EXTENSIONS = [
    ".py", ".js", ".ts", ".java", ".cpp", ".c"
]

def get_code_files(repo_path):
    code_files = []
    
    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
                code_files.append(os.path.join(root, file))
    
    return code_files