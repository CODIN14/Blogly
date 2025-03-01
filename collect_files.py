import os

# Define the project directory
project_dir = "."
output_file = "project_files.txt"

# Files/folders to ignore
ignore_dirs = ["myenv", "__pycache__"]
ignore_extensions = [".db", ".pyc"]

# Open a file to write the contents
with open(output_file, "w", encoding="utf-8") as outfile:
    # Walk through the directory
    for root, dirs, files in os.walk(project_dir):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            # Skip ignored file extensions
            if any(file.endswith(ext) for ext in ignore_extensions):
                continue

            file_path = os.path.join(root, file)
            try:
                outfile.write(f"\n=== {file_path} ===\n")
                with open(file_path, "r", encoding="utf-8") as f:
                    outfile.write(f.read())
                outfile.write("\n\n")
            except Exception as e:
                outfile.write(f"Error reading {file_path}: {str(e)}\n\n")

print(f"All file contents written to {output_file}")