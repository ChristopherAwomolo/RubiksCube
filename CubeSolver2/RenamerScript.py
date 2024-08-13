import os
def rename_files():
    for filename in os.listdir('.'):
        if filename.startswith('1-') and filename.endswith('.png'):
            new_filename = '11-' + filename[2:]  # Replace '3-' with '7-'
            os.rename(filename, new_filename)
            print(f'Renamed: {filename} to {new_filename}')

rename_files()