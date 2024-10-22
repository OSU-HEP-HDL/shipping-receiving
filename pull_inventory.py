
from datetime import datetime
from dotenv import dotenv_values

import modules.pull_module as pull
from modules.db_utils import authenticate_user_mongodb, authenticate_user_proxmox
import argparse

parser = argparse.ArgumentParser(description="Register Component for UI. Takes all component info as string arguments provided from UI")
parser.add_argument('-i','--images', action='store_true', help='If this flag is set, Excel Workbook will include images')
args = vars(parser.parse_args())


def main():
  client = authenticate_user_mongodb()
  proxmox_auth = authenticate_user_proxmox()
  mongo_inventory = pull.pull_mongodb(client)

  if args['images']:
    pull.save_as_excel_images(mongo_inventory,proxmox_auth)
  else:
    pull.save_as_excel(mongo_inventory,proxmox_auth)
    
if __name__ == '__main__':
  main()
