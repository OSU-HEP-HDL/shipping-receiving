#!/bin/bash
pip install -r requirements/requirements.txt

read -p "Enter local username: " USERNAME 
read -s -p "Enter local password: " PASSWORD

echo "USERNAME=$USERNAME" >> .env
echo "PASSWORD=$PASSWORD" >> .env
echo "LOCAL_ADDRESS=\"docker.dhcp.okstate.edu:27017\"" >> .env
echo "LOCAL_PROXMOX_HOST="10.206.65.222"" >> .env
echo "LOCAL_PROXMOX_USER="smb"" >> .env
echo "LOCAL_PROXMOX_PASSWORD="osuhep"" >> .env
echo "LOCAL_PROXMOX_PORT="22"" >> .env