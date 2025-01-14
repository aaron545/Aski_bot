# How to use this bot

## Installing Dependencies by requirements.txt

It automatically downloads and installs the specified libraries:

`pip install -r requirements.txt`

## What can you do in this bot

### **v2.1.0**
![image](https://github.com/user-attachments/assets/fa07a250-2918-4792-bb4f-9db21fa47523)

add the `ui.py` to control the bot

### **v1.5.1**

for web: You can automatically set the parameters of "RF Antenna"

### **v1.2.0**

for web: You can automatically set the parameters of "gNB customization"

### **v1.1.0**

for web: You can automatically set the parameters of "gNB configuration"

for amp: You can automatically set the provision page of "SA and Deployment"

## Config

Edit content of `sample_config.json sample_BASIC.json` and rename it as `config.json BASIC.json`.

When you want to start or switch to another gNB, please follow the steps below to modify the file.

1. Edit `web_root` in `config.json`
2. Edit `"GNB_ID", "TAC", "PCI"` in `BASIC.json`
3. Please replace the `"GNB_N3_IP"` field with your own IP address if you need GNB_N3_IP.
4. Create a .txt file containing the gNB customization you need and place it in the "**customization**" folder.

### Config detail

- login_url: the url to amp login
- dashboard_url: the url to amp main page
- user: the account with amp 
- amp_password: the password with amp 
- web_root: the url to gNB web (eg. https://1.1.1.1)
- web_password: the password to gNB web
- serial_number: you can get on your gNB sticker
- security_gateway: the ip of security_gateway
- ipsec_right_subnet: the ip of ipsec_right_subnet

## Commands

Please run `python amp_main.py --help` or `python web_main.py --help` to view the options.

or

run `ui.py` to use this bot

P.S. BASIC is **DDDSU 100MHz 256QAM 2L pos1**
