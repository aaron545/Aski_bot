# How to use this bot

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

for example: `python web_main.py -p BASIC.json QAM256_2L.json -r ratio.json`