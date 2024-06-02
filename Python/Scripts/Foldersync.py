import os
from openpyxl import load_workbook

# Defining the source and destination paths
source_path = r"\\LNCSynoFS01\FileShare\SALES-MARKETING\Price Update Emails (Acctg)\AX Docs"
destination_path = r"C:\Users\mrice\OneDrive - Kalas Manufacturing Inc\_DataSources\AX_exports\AX_Sync"

# Function to rename and move Excel files based on cell value
def rename_and_move_excel_files(source_folder, destination_folder, cell_reference):
    for filename in os.listdir(source_folder):
        # Check if the file is an Excel file
        if filename.endswith('.xlsx'):
            try:
                # Construct full file path
                file_path = os.path.join(source_folder, filename)
                # Load the workbook and select the first sheet
                workbook = load_workbook(file_path)
                first_sheet = workbook.active
                # Read the value from the desired cell
                cell_value = first_sheet[cell_reference].value
                # Construct the new filename based on cell value
                new_filename = "{}.xlsx".format(cell_value)
                # Construct new file path
                new_file_path = os.path.join(destination_folder, new_filename)
                # Check if a file with the new name already exists in the destination folder
                if not os.path.exists(new_file_path):
                    # Move and rename the file to the new path
                    os.replace(file_path, new_file_path)
                else:
                    print("File with name {} already exists in the destination folder.".format(new_filename))
            except Exception as e:
                print("An error occurred with file {}: {}".format(filename, e))
