import os

# Define the project directory
project_dir = "."
output_file = "collect_files.txt"

# Files and directories to include (explicitly allow these)
include_dirs = ["applicaton", "templates", ".github", ""]
include_extensions = [".py", ".html", ".yml", ".md", ".txt"]

# Files and directories to ignore
ignore_dirs = [".git", "myenv", "__pycache__", "data", "static/uploads"]
ignore_files = ["database.db", "queries.active", "*.log"]

# Open a file to write the contents
with open(output_file, "w", encoding="utf-8") as outfile:
    # Walk through the directory
    for root, dirs, files in os.walk(project_dir):
        # Filter directories to only include relevant ones
        dirs[:] = [d for d in dirs if any(d in include_dirs for d in [d, os.path.basename(root)])]

        for file in files:
            # Skip ignored files and extensions
            if any(file in ignore_files or file.endswith(ext) for ext in [".db", ".pyc", ".log"]) or not any(file.endswith(ext) for ext in include_extensions):
                continue

            file_path = os.path.join(root, file)
            # Skip files in ignored directories even if extension matches
            if any(ignored in file_path for ignored in ignore_dirs):
                continue

            try:
                outfile.write(f"\n=== {file_path} ===\n")
                with open(file_path, "r", encoding="utf-8") as f:
                    outfile.write(f.read())
                outfile.write("\n\n")
            except Exception as e:
                outfile.write(f"Error reading {file_path}: {str(e)}\n\n")

print(f"All relevant file contents written to {output_file}")