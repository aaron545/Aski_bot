# How to use this bot

## Installing Dependencies by requirements.txt

It automatically downloads and installs the specified libraries:

`pip install -r requirements.txt`

## What can you do in this bot

### **v1.2.0**

for web: You can automatically set the parameters of "gNB customization"

### **v1.1.0**

for web: You can automatically set the parameters of "gNB configuration"

for amp: You can automatically set the provision page of "SA and Deployment"

## Config

Edit content of `sample_config.json` and rename it as `config.json`.

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

P.S. BASIC is **DDDSU 100MHz 256QAM 2L pos1**
