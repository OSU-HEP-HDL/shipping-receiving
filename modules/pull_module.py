import paramiko
import fnmatch
from openpyxl import Workbook
from openpyxl.drawing.image import Image as OpenPyXLImage
from PIL import Image as PILImage
from db_utils import setup_ssh_client
import os


def retrieve_images(proxmox_auth,remote_path,local_path):

    try:
        ssh_client = setup_ssh_client(proxmox_auth)
        sftp = ssh_client.open_sftp()
        sftp = ssh_client.open_sftp()
        file_list = sftp.listdir(remote_path)

        # Filter files based on the pattern (e.g., '*.jpg')
        matching_files = fnmatch.filter(file_list, '*')
        downloaded_files = []

        for remote_file in matching_files:
            remote_path = os.path.join(remote_path, remote_file)
            local_path = os.path.join(local_path, remote_file)
            sftp.get(remote_path, local_path)
            downloaded_files.append(local_path)
            print(f"Downloaded: {remote_file} to {local_path}")
        
        sftp.close()
        return downloaded_files
    except Exception as e:
        print(f"Error downloading files: {e}")
        return []

def save_as_excel(data,proxmox_auth):

    wb = Workbook()
    ws = wb.active

    local_image_folder = "./downloaded_images"  # Folder to store downloaded images locally

    # Create folder if it doesn't exist
    os.makedirs(local_image_folder, exist_ok=True)

    # Adding headers
    headers = list(data[0].keys())  # Assumes all JSON entries have the same structure
    for idx, header in enumerate(headers):
        ws.cell(row=1, column=idx + 1, value=header)

    for row_idx, entry in enumerate(data, start=2):  # Start from the second row
        # Get all non-image data
        for col_idx, (key, value) in enumerate(entry.items()):
            if key != 'Images':  # If it's not the image, add the data
                ws.cell(row=row_idx, column=col_idx + 1, value=value)
            else:
                # Handle image download and insertion
                remote_image_path = value['items']
                local_image_path = os.path.join(local_image_folder, os.path.basename(remote_image_path))
                downloaded_images = retrieve_images(proxmox_auth, remote_image_path, local_image_path)

                for ind, img_path in enumerate(downloaded_images, start=1):
                    # Insert the image into the last column
                    img = PILImage.open(img_path)
                    img.save(img_path)

                    img = OpenPyXLImage(img_path)
                    img.anchor = ws.cell(row=row_idx, column=col_idx + 1).coordinate  # Place in the corresponding cell
                    ws.add_image(img)

    # Save the workbook
    wb.save("inventory.xlsx")
    print("Excel file created with images from SFTP.")

def pull_mongodb(client):
    db = client["local"]
    dates = db['inventory'].find()

    inventory = []
    for date in dates:
        inventory.append(date)
    
    print(inventory)
    
    return inventory

    

def pull_proxmox(proxmox_auth):
    host = proxmox_auth["host"]
    port = proxmox_auth["port"]
    user = proxmox_auth["user"]
    password = proxmox_auth["password"]

    inv_path = "/mnt/proxmox/images/inventory/"