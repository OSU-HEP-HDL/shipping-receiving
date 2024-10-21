import paramiko
import stat
import json
import re
from modules.db_utils import setup_ssh_client

# Have it ask vendor name, part names, qty ordered, qty recvd, date automatically. Then have it ask for pic of packing slip 
# if available and pic of items received. May need to allow multiple pics. I would like it to ask for pic of lab equipment 
# to but full device with SN clear.

def post_mongo(client,vendor,part_name,item_description,qty_ordered,qty_recvd,date_time,date,image_path,file_pathes):

    sn_strings = ["sn","SN","serial_number","serialNumber","serialnumber","Serial_Number"]
    slip_strings = ["slip","slp"]
    
    img_sn_path = image_path
    img_slip_path = image_path

    for path in file_pathes:
        sp = path.split("/")
        if any(sn_strings in sp[-1] for sn_strings in sn_strings):
            img_sn_path = path
            
        if any(slip_strings in sp[-1] for slip_strings in slip_strings):
            img_slip_path = path
       
    db = client["local"]["inventory"]
    new_id = date_time.replace(" ","-")

    upload_reception = {
                '_id': new_id,
                'NameorModelNo': part_name,
                'Properties': 
                    {
                    'Vendor': vendor,
                    'ItemDescription':item_description,
                    'QuantityOrdered': qty_ordered,
                    'QuantityReceived': qty_recvd,
                    'DateandTimeReceived': date_time,
                    'Images': {
                        'Directory': image_path,
                        'PackingSlip': img_slip_path,
                        'SerialNumber': img_sn_path
                        }
                    }
                }
    
    existing_file = db.find_one({"_id": new_id})

    try:
        if existing_file:
            raise ValueError
        else:       
            db.insert_one(upload_reception) 
  
    except ValueError:
        print("Part already exists!")




def post_proxmox(proxmox_auth, args, date,part_name):
    host = proxmox_auth["host"]
    port = proxmox_auth["port"]
    user = proxmox_auth["user"]
    password = proxmox_auth["password"]

    part_name = part_name.replace(" ","-")

    remote_path = "/mnt/proxmox/images/inventory/" + date
    nested_remote_path = remote_path + "/" + part_name

    for arg_key, value in args.items():
       key = arg_key

    try:
        # Initialize the SSH client
        ssh = setup_ssh_client(proxmox_auth)
        
        files = []
        file_pathes = []
        if "/" in args[key][0]:
            for image in args[key]:
                g = image.split("/")
                files.append(g[-1])
        
        # Open an SCP session
        with ssh.open_sftp() as sftp:
            #Create directory for component
            create_remote_directory(sftp,remote_path)
            create_remote_directory(sftp,nested_remote_path)
            for image,file in zip(args[key],files):
            # Upload the local file to the remote server
                
                remote_file_path = nested_remote_path + "/" + file
                #print(f"Uploading {image} to {user}:{host}:{remote_file_path}")
                sftp.put(image, remote_file_path)
                file_pathes.append(remote_file_path)

        
        print("Uploaded images.")

        # Close the connection
        ssh.close()
        total_remote_path = str(user)+"@"+str(host)+":"+nested_remote_path
    
    except Exception as e:
        print(f"An error occurred: {e}")
       
    
    return total_remote_path,file_pathes

def remove_item(mongo_client,proxmox_auth, id):
    host = proxmox_auth["host"]
    port = proxmox_auth["port"]
    user = proxmox_auth["user"]
    password = proxmox_auth["password"]

    db = mongo_client['local']['inventory']

    existing_file = db.find_one({"_id": id})
 
    image_directory = existing_file['Properties']['Images']['Directory']
    image_directory = re.sub(r'^.*?:', '', image_directory)

    try:
        # Convert the string ID to an ObjectId
        result = db.delete_one({"_id": id})

        # Check if a document was deleted
        if result.deleted_count > 0:
            print(f"Document with ID {id} deleted successfully.")
        else:
            print(f"No document found with ID {id}.")

    except Exception as e:
        print(f"An error occurred: {e}")


    # Initialize the SSH client
    ssh = setup_ssh_client(proxmox_auth)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add untrusted hosts
    try:
        command = f'rm -rf {image_directory}'
        stdin, stdout, stderr = ssh.exec_command(command)

        # Check for errors
        error = stderr.read().decode()
        if error:
            print(f"Error removing directory: {error.strip()}")
        else:
            print(f"Directory '{image_directory}' removed successfully.")
        
       
    finally:
        # Close the SSH connection
        ssh.close()


def get_item_id():
    print("Enter Item ID")
    item_id = input("\nID: ")

    return item_id

def create_remote_directory(sftp, remote_directory):
    """Create a remote directory if it does not exist."""
    try:
        sftp.chdir(remote_directory)  # Try to change to the remote directory
    except IOError:
        sftp.mkdir(remote_directory)   # Create the directory if it does not exist
        sftp.chdir(remote_directory)    # Change into the newly created directory

def remove_remote_directory(sftp, remote_directory):
    """Recursively remove a remote directory and its contents."""
    for file_attr in sftp.listdir_attr(remote_directory):
        remote_file_path = f"{remote_directory}/{file_attr.filename}"
        if stat.S_ISDIR(file_attr.st_mode):  # If it's a directory
            remove_remote_directory(sftp, remote_file_path)  # Recursively remove subdirectories
        else:
            sftp.remove(remote_file_path)  # Remove files
    sftp.rmdir(remote_directory)  # Finally, remove the empty directory

def check_directory_exists(sftp, remote_directory,serialNumber):
    """Check if a remote directory exists."""
    try:
        sftp.stat(remote_directory)  # Try to retrieve directory attributes
        return True
    except FileNotFoundError:
        print("Component with serial number",serialNumber,"not found on proxmox!")
        return False


def get_vendor_name():
    '''
    Prompts user to select the flavor of component.
    '''
    print("\nWho is their vendor?")
    vendor_list = ["Altaflex","PFC","Cirexx","EPEC","Vector","Summit","Other"]
    for k, v in enumerate(vendor_list):
        print(f"For {v}, press {k}")
    while True:
        try:
            vendor = input("\nInput Selection: ")
            selection = vendor_list[int(vendor)]
            if selection == "Other":
                print("\nPlease enter the vendor manually.")
                selection = input("\nVendor: ")
            break
        except (ValueError, IndexError):
            print("Invalid Input. Try again.")
        
    return selection

def manual_type(text):
    print(f"\n{text}")
    answer = input("Answer: ")
    
    return answer

def ask_image_questions():
    print("\nHave you included an image of the packing slip?")
    ans1 = input("Answer: ")
    print("\nHave you included an image of the items?")
    ans2 = input("Answer: ")
    print("\nHave you included an image of the item's Serial Number?")
    ans3 = input("Answer: ")
    no_list = ["no","n"]
    yes_list = ["yes","y"]
    if ans1 in no_list and ans2 in no_list and ans3 in no_list:
        print("No images included...Are you sure you want to continue? (y or n)")
        ans = input("\nAnswer: ")
        if ans in no_list:
            exit            