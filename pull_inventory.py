import argparse
import paramiko
import os
import stat
from datetime import datetime
from dotenv import dotenv_values

import modules.pull_module as pull
from modules.db_utils import authenticate_user_mongodb, authenticate_user_proxmox


def main():
    client = authenticate_user_mongodb()
    proxmox = authenticate_user_proxmox()
    now = datetime.now()

    mongo_inventory = pull.pull_mongodb(client)

    






    
if __name__ == '__main__':
  main()
