import os

class CodeAnalyzer:
    SUPPORTED_EXTENSIONS = {'.py', '.java', '.js', '.ts', '.cpp', '.c', '.go', '.rb'}

    def __init__(self, repo_path):
        self.repo_path = repo_path

    def read_codebase(self):
        file_data = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in self.SUPPORTED_EXTENSIONS:
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_data.append({
                            "filename": path,
                            "content": f.read()
                        })
        return file_data