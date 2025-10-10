
import os

# Define the folder path
folder_path = 'modules'

# Check if the folder exists
if not os.path.exists(folder_path):
    print(f"Folder '{folder_path}' does not exist. Please create it and add some files.")
    exit()

# Get all file names in the folder
file_names = os.listdir(folder_path)

# Write the file names to folder_files.txt
with open('folder_files.txt', 'w') as f:
    for file_name in file_names:
        f.write(file_name + '\n')

# Read the file names from folder_files.txt
with open('folder_files.txt', 'r') as f:
    folder_files = set(line.strip() for line in f)

# Read the file names from existing_files.txt
try:
    with open('skip_json.txt', 'r') as f:
        existing_files = set(line.strip() for line in f)
except FileNotFoundError:
    print("skip_json.txt not found. Please make sure it exists in the same directory.")
    exit()

# Find missing files
missing_files = folder_files - existing_files

# Print missing files
print("Missing files:")
for file in sorted(missing_files):
    print(file)
