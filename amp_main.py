from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import By
from enum import Enum, IntEnum, auto
from datetime import datetime

import pytz
import os
import atexit
import time
import argparse
import json

def msgLogger(msg):
    # 取得當前時間並設置時區為台北
    date = datetime.now(pytz.timezone('Asia/Taipei'))
    
    print('--------------------------')
    print(date.strftime('%Y/%m/%d %I:%M:%S %p'))
    print(msg)
    print('--------------------------')

def close_driver(page):
	page.quit()
	print("close!")

def set_SA_value(features, li_elements):
	for key, value in features.items():
		try:	
			# for textbox
			element = li_elements[Li_SA[key]].ele('tag:input@@type:text', timeout = 0.1)
			element.clear(by_js = True)
			element.input(value)
		except:
			# for selectmenu
			try:
				li_elements[Li_SA[key]].ele('tag:button', timeout = 0.1).run_js('this.click()', timeout = 0.1)
				time.sleep(0.2)
				page.ele('@class:dropdown-menu show').ele(f'tag:a@@text():{value}').click()
				
			except:
				pass
		finally:
			time.sleep(0.1)
	if li_elements[Li_SA.ADMIN_STATE].ele("@@class:text-truncate@@class:badge-pill").text != "Product":
		li_elements[Li_SA.ADMIN_STATE].ele(".ng-star-inserted").click()


def get_SA_value():
	if len(li_elements) == len(Li_SA):
		for feature in Li_SA:
			try:	
				# for textbox
				element = li_elements[feature.value].ele('tag:input@@type:text', timeout = 0.1)
				value = element.run_js('return this.value')
				print(feature.name, ":", value)
			except:
				# for selectmenu
				try:
					element = li_elements[feature.value].ele('tag:button', timeout = 0.1)
					print(feature.name, ":", element.text)
				except:
					pass
			finally:
				pass
	else:
		print('Length is inconsistent, please fix the code.')

def set_DEPLOY_value(features, li_elements):
	is3ms = False
	for key, value in features.items():
		li_elements[Li_DEPLOY[key]].ele('tag:button', timeout = 0.1).run_js('this.click()', timeout = 0.1)
		time.sleep(0.2)
		page.ele('@class:dropdown-menu show').ele(f'tag:a@@text():{value}').click()
		if key == "TIMESLOT" and value == "DDDDDDDSUU":
			is3ms = True

	msgLogger("check 3ms timing offset...")
	time.sleep(0.5)
	offset_element = page.ele('tag:ul@class:list-group').eles('tag:li')[Li_DEPLOY.OFFSET]
	isOffset = True if offset_element.ele("@@class:text-truncate@@class:badge-pill").text == "Product" else False
	if not is3ms and isOffset:
		offset_element.ele(".ng-star-inserted").click()

class MENU(IntEnum):
	LIVE_UPDATE = 0
	PROVISIONING = auto()
	REBOOT = auto()
	UPGRADE_FIRMWARE = auto()

class TAB(IntEnum):
	SA = 2
	NEIGHBOR = auto()
	LTE_NEIGHBOR = auto()
	CONFIG_NEIGHBOR = auto()
	HO_EVENT = auto()
	DEPLOYMENT = auto()
	PM = auto()

class Li_SA(IntEnum):
	GNB_ID = 0
	GNB_ID_LENGTH = auto()
	CELL_ID = auto()
	TAC = auto()
	MCC = auto()
	MNC = auto()
	SST = auto()
	SD = auto()
	NSSAI = auto()
	AMF_IP = auto()
	PCI = auto()
	EPSFB = auto()
	MODULATION = auto()
	LAYER = auto()
	DRMS = auto()
	UE_INACTIVITY = auto()
	POWER = auto()
	ADMIN_STATE = auto()

class Li_DEPLOY(IntEnum):
	OFFSET = 0
	DEPLOYMENT_MODE = auto()
	NR_BAND = auto()
	BANDWIDTH = auto()
	NRARFCN = auto()
	TIMESLOT = auto()

class Config:
	def __init__(self,**kwargs):
		# 動態設置屬性
		for key, value in kwargs.items():
			setattr(self, key, value)

default_provision = ["BASIC.json", "QAM256_2L.json"]
default_radio = "radio.json"

parser = argparse.ArgumentParser(description="Load configuration files")
parser.add_argument("-p", "--provisions", nargs="*",default=default_provision, help="List of provision files to load")
parser.add_argument("-r", "--radio", nargs="?", default=default_radio, help="radio file to load, default is \"N78 100MHz 4:1\"")
args = parser.parse_args()

provision = {}
for file in args.provisions:
	with open(file, 'r') as f:
		provision.update(Config(**json.load(f)).__dict__)
with open(args.radio, 'r') as f:
	radio = Config(**json.load(f)).__dict__


with open("config.json", 'r') as f:
	data = json.load(f)
config = Config(**data)

download_directory = os.path.dirname(__file__)
co = ChromiumOptions()
co.set_pref('download.default_directory', download_directory)
co.set_argument('--window-size', '1920,1080')
co.ignore_certificate_errors()
co.incognito()
# co.headless()

if os.path.exists('../chrome-win/chrome.exe'):
	co.set_browser_path('../chrome-win/chrome.exe')
	
elif os.path.exists("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"):
	co.set_browser_path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")

page = ChromiumPage(co)
# atexit.register(close_driver, page)

page.get(config.login_url, timeout = 10)
msgLogger("waiting for get amp page...")

# -----------------------login-----------------------

# input user
page.ele('tag:input@formcontrolname=email').input(config.user)

# input password
page.ele('tag:input@formcontrolname=password').input(config.amp_password)

# sign in
page.ele('tag:button@@text():Sign in').click()
msgLogger("waiting for login...")


# -----------------------searchSN-----------------------
time.sleep(1)
try:
	button_device = page.ele('@class:avatar bg-light-primary p-50 m-0')
except:
	button_device = page.ele('tag:a@href=#/devices', timeout = 2)

button_device.click()
msgLogger("switch to devices page...")


serial_number = config.serial_number
try:
	tb_serial_number = page.ele('tag:datatable-header-cell@style:211.962px').ele('tag:input@type=text')
except:
	tb_serial_number = page.ele('tag:datatable-header-cell@style:204.038px').ele('tag:input@type=text')

msgLogger("searching SN...")
tb_serial_number.input(serial_number)

time.sleep(2)
# loc = (By.XPATH, f'//div[@class="text-truncate ng-star-inserted" and contains(text(), "{serial_number}")]')
# link_small_cell = page.ele(loc)
link_small_cell = page.ele(f'@@class:text-truncate ng-star-inserted@@text():{serial_number}')
link_small_cell.click()

button_menu = page.eles('@@class:btn@@class:btn-primary@@class:ng-star-inserted')
button_menu[MENU.PROVISIONING].click()
msgLogger("opening the provisoning page...")
time.sleep(2)


# tab = page.eles('@class:nav-item ng-star-inserted')

# print("before:")
# get_SA_value()
# ----------------------set feature value----------------------
msgLogger("setting the SA configs...")
tab = page.eles('@class:nav-item ng-star-inserted')
tab[TAB.SA].click()
time.sleep(0.5)
li_elements = page.ele('tag:ul@class:list-group').eles('tag:li')
set_SA_value(provision, li_elements)

msgLogger("setting the radio config...")
tab = page.eles('@class:nav-item ng-star-inserted')
tab[TAB.DEPLOYMENT].click()
time.sleep(0.5)
li_elements = page.ele('tag:ul@class:list-group').eles('tag:li')
set_DEPLOY_value(radio, li_elements)

# print("\nafter:")
# get_SA_value()

# ----------------------print feature value----------------------

# download csv
# page.ele('tag:label@for=download-default').click()
# time.sleep(2)

# save provision
msgLogger("saving the provision page...")
page.ele('tag:button@@text():Apply').click()

# close provision
# msgLogger("closing the provision page...")
# button_close = page.eles('.close')
# button_close[1].click()

time.sleep(1)
# button_menu = page.eles('@@class:btn@@class:btn-primary@@class:ng-star-inserted')
# button_menu[menu.REBOOT].click()
# page.ele('tag:button@@text():OK').click()

# time.sleep(200)