import os
import shutil
import subprocess
import xml.etree.ElementTree as ET

# Set the target frame rate here
TARGET_FPS = 1000

def extract_pngs_and_rename():
    # Get current directory (where the .sup files are)
    sup_folder = os.getcwd()

    # Create the output folder in the current directory
    output_folder = os.path.join(sup_folder, 'output')
    os.makedirs(output_folder, exist_ok=True)

    # Loop through all .sup files in the current directory
    for sup_file in os.listdir(sup_folder):
        if sup_file.endswith('.sup'):
            sup_file_path = os.path.join(sup_folder, sup_file)
            folder_name = os.path.splitext(sup_file)[0]
            
            # Create a subfolder for each sup file inside the output folder
            output_subfolder = os.path.join(output_folder, folder_name, 'TXTImages')
            os.makedirs(output_subfolder, exist_ok=True)
            
            # Run BDSup2Sub command to generate the XML file with the target frame rate
            xml_file_path = os.path.join(output_subfolder, folder_name + '.xml')
            command = [
                'java', '-jar', 'BDSup2Sub.jar',
                sup_file_path, '-o', xml_file_path, 
                '-T', str(TARGET_FPS)  # Use the target frame rate variable
            ]
            subprocess.run(command)

            # Parse the XML file
            tree = ET.parse(xml_file_path)
            root = tree.getroot()

            # Extract PNG file names and their corresponding start and end times from the XML
            for event in root.findall('.//Event'):
                graphic = event.find('Graphic')
                if graphic is not None:
                    png_filename = graphic.text.strip()
                    in_time = event.get('InTC')  # Start time (InTC)
                    out_time = event.get('OutTC')  # End time (OutTC)
                    
                    # Format the times to remove colons for filename
                    in_time_formatted = in_time.replace(':', '_')
                    out_time_formatted = out_time.replace(':', '_')

                    # Create the new PNG filename
                    new_png_filename = f"{in_time_formatted}__{out_time_formatted}_{png_filename}"
                    
                    # Check the correct path where the PNG file is located
                    png_source_path = os.path.join(sup_folder, 'output', folder_name, 'TXTImages', png_filename)
                    print(f"Looking for: {png_source_path}")

                    # Ensure the PNG file exists and copy it to the output folder with the new name
                    if os.path.exists(png_source_path):
                        png_dest_path = os.path.join(output_subfolder, new_png_filename)
                        shutil.copy(png_source_path, png_dest_path)
                        os.remove(png_source_path)  # Delete the original PNG
                        print(f"Copied, renamed, and deleted: {png_filename} to {new_png_filename}")
                    else:
                        print(f"PNG file not found: {png_source_path}")

# Run the function
extract_pngs_and_rename()