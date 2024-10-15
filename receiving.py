import argparse
import paramiko
import os
import stat
from datetime import datetime
from dotenv import dotenv_values
from modules.reception_module import get_vendor_name, manual_type,post_mongo,post_proxmox,ask_image_questions
from modules.db_utils import authenticate_user_mongodb, authenticate_user_proxmox

# Have it ask vendor name, part names, qty ordered, qty recvd, date automatically. Then have it ask for pic of packing slip 
# if available and pic of items received. May need to allow multiple pics. I would like it to ask for pic of lab equipment 
# to but full device with SN clear.

parser = argparse.ArgumentParser()
parser.add_argument("images",nargs="*",help="Add receiving photos")
args = vars(parser.parse_args())

def main():
  client = authenticate_user_mongodb()
  proxmox = authenticate_user_proxmox()
  now = datetime.now()
  ask_image_questions()

  vendor = get_vendor_name()
  part_name = manual_type("What is the part name? ")
  item_description = manual_type("Type an item description...")
  qty_ordered = manual_type("Quantity ordered? ")
  qty_recvd = manual_type("Quantity Received? ")
  
  date_time = now.strftime("%Y-%m-%d %H:%M:%S")
  date = now.strftime("%Y-%m-%d")

  image_path,file_pathes = post_proxmox(proxmox,args,date,part_name)
  post_mongo(client,vendor,part_name,item_description,qty_ordered,qty_recvd,date_time,date,image_path,file_pathes)
  print("Items Received!")


    
if __name__ == '__main__':
  main()
