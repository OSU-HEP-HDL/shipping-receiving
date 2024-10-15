import pymongo
from dotenv import dotenv_values

def authenticate_user_mongodb():
    keys = dotenv_values(".env")
    USERNAME = keys["USERNAME"]
    PASSWORD = keys["PASSWORD"]
    LOCAL_ADDRESS = keys["LOCAL_ADDRESS"]
    client = pymongo.MongoClient('mongodb://%s:%s@%s' % (USERNAME, PASSWORD, LOCAL_ADDRESS))
    return client

def authenticate_user_proxmox():
    keys = dotenv_values(".env")
    proxmox = {}
    proxmox["host"] = keys["LOCAL_PROXMOX_HOST"]
    proxmox["user"] = keys["LOCAL_PROXMOX_USER"]
    proxmox["password"] = keys["LOCAL_PROXMOX_PASSWORD"]
    proxmox["port"] = keys["LOCAL_PROXMOX_PORT"]
 
    return proxmox