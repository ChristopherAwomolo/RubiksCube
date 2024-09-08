import os

# Define the directory containing the files
directory = "."

# Loop through all files in the directory
for filename in os.listdir(directory):
    # Check if the file starts with "1-"
    if filename.startswith("1-"):
        # Create the new filename
        new_filename = filename.replace("1-", "21-", 1)
        # Get the full path for the old and new filenames
        old_file = os.path.join(directory, filename)
        new_file = os.path.join(directory, new_filename)
        # Rename the file
        os.rename(old_file, new_file)

print("Renaming completed.")
