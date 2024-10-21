from datetime import datetime
from dotenv import dotenv_values

import modules.reception_module as rec
from modules.db_utils import authenticate_user_mongodb, authenticate_user_proxmox

def main():
  client = authenticate_user_mongodb()
  proxmox_auth = authenticate_user_proxmox()

  item_id = rec.get_item_id()
  rec.remove_item(client, proxmox_auth,item_id)
    
if __name__ == '__main__':
  main()