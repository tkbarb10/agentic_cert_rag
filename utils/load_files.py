from pathlib import Path
from typing import List, Union

def load_files_as_list(documents_path: Union[str, Path]) -> List[str]:
    root = Path(documents_path)
    file_list = []

    # Case 1: The path is a direct file
    if root.is_file():
        # Optional: Check if the file has the right extension
        if root.suffix in ['.txt', '.md']:
            try:
                content = root.read_text(encoding='utf-8')
                file_list.append(content)
                print(f"Successfully Loaded single file: {root}")
            except Exception as e:
                print(f"Error loading {root}: {e}")
        else:
            print(f"File {root} is not a supported type (.txt or .md)")
        
        return file_list

    # Case 2: The path is a directory
    if root.is_dir():
        extensions = ('*.txt', "*.md")
        for ext in extensions:
            for file_path in root.rglob(ext):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    file_list.append(content)
                    print(f"Successfully Loaded {file_path}")
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        return file_list

    # Case 3: Path doesn't exist
    print(f"Path does not exist: {documents_path}")
    return file_list