from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import Keys
from enum import Enum, IntEnum, auto
from datetime import datetime

import pytz
import os
import atexit
import time
import argparse
import json

textbox_list = ["GNB_ID", "GNB_ID_LENGTH", "CELL_ID", "TAC", "AMF_IP", "PCI", "EPSFB", "POWER"]
selectmenu_list = ["MODULATION", "LAYER", "DRMS", "NR_BAND", "BANDWIDTH", "TIMESLOT", "TIMING_OFFSET"]

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

def set_SA_value(page, features, li_elements):
	for key, value in features.items():
		print(key, ":", value)
		if key in textbox_list:
			element = li_elements[Li_SA[key]].ele('tag:input@@type:text', timeout = 0.1)
			element.clear(by_js = True)
			if key == "AMF_IP":
				element.input(value[0])
			else:
				element.input(value)

		elif key == "PLMN":
			MCC = li_elements[Li_SA.MCC].ele('tag:input@@type:text', timeout = 0.1)
			MCC.clear(by_js = True)
			MCC.input(value[0]["MCC"])
			MNC = li_elements[Li_SA.MNC].ele('tag:input@@type:text', timeout = 0.1)
			MNC.clear(by_js = True)
			MNC.input(value[0]["MNC"])
			SST = li_elements[Li_SA.SST].ele('tag:input@@type:text', timeout = 0.1)
			SST.clear(by_js = True)
			SST.input(value[0]["SNSSAI"][0]["SST"])
			SD = li_elements[Li_SA.SD].ele('tag:input@@type:text', timeout = 0.1)
			SD.clear(by_js = True)
			SD.input(value[0]["SNSSAI"][0]["SD"])

		elif key in selectmenu_list:
			li_elements[Li_SA[key]].ele('tag:button', timeout = 0.1).run_js('this.click()', timeout = 0.1)
			time.sleep(0.2)
			page.ele('@class:dropdown-menu show').ele(f'tag:a@@text():{value}').click()
		else:
			print(f'{key} is not in any list, skip it...')

	if li_elements[Li_SA.ADMIN_STATE].ele("@@class:text-truncate@@class:badge-pill").text != "Product":
		li_elements[Li_SA.ADMIN_STATE].ele(".ng-star-inserted").click()


def get_SA_value():
	if len(li_elements) != len(Li_SA):
		print('Length is inconsistent, please fix the code.')
		
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
def checkmultiPLMN(page, PLMN):
	if len(PLMN) != 1 or len(PLMN[0]["SNSSAI"]) != 1:
		return True
	else:
		return False

def set_MULTI_PLMN_value(page, PLMN):
	plmn_labels = page.eles("#cuconfig")[1].ele("@@name:indexSwitch").eles("tag:label")
	for plmnIdx, plmn in enumerate(PLMN):
		plmn_labels[plmnIdx].click()
		print(f'{plmnIdx}: plmn')
		print(f'MCC = {plmn["MCC"]}, MNC = {plmn["MNC"]}')

		MCC = page.eles("#cuconfig")[1].ele("tag:ul").eles("tag:li")[0].ele("tag:input")
		MCC.clear(by_js = True)
		MCC.input(plmn["MCC"])

		MNC = page.eles("#cuconfig")[1].ele("tag:ul").eles("tag:li")[1].ele("tag:input")
		MNC.clear(by_js = True)
		MNC.input(plmn["MNC"])
		snssai_labels = page.eles("#cuconfig")[1].ele("@@name:subIndexSwitch").eles("tag:label")
		for snssaiIdx, snssai in enumerate(plmn["SNSSAI"]):
			snssai_labels[snssaiIdx].click()
			print(f'SST = {snssai["SST"]}, SD = {snssai["SD"]}')
			SST = page.eles("#cuconfig")[1].ele("tag:ul").eles("tag:li")[2].ele("tag:ul").eles("tag:li")[0].ele("tag:input")
			SST.clear(by_js = True)
			SST.input(snssai["SST"])
			SST.input(Keys.ENTER)

			SD = page.eles("#cuconfig")[1].ele("tag:ul").eles("tag:li")[2].ele("tag:ul").eles("tag:li")[1].ele("tag:input")
			SD.clear(by_js = True)
			SD.input(snssai["SD"])
			SD.input(Keys.ENTER)

def set_DEPLOY_value(page, features, li_elements):
	timingOffset = ["0s", "3ms", "1.94896ms"]
	for key, value in features.items():
		print(key, ":", value)
		li_elements[Li_DEPLOY[key]].ele('tag:button', timeout = 0.1).click()
		# li_elements[Li_DEPLOY[key]].ele('tag:button', timeout = 0.1).run_js('this.click()', timeout = 0.1)
		time.sleep(0.2)
		page.ele('@class:dropdown-menu show').ele(f'tag:a@@text():{value}').click()
		if key == "TIMESLOT" and value == "DDDDDDDSUU":
			tOIdx = 1
		elif key == "TIMESLOT" and value != "DDDDDDDSUU":
			tOIdx = 0

	msgLogger("check 3ms timing offset...")
	time.sleep(0.2)
	li_elements[Li_DEPLOY.TIMING_OFFSET].ele('tag:button', timeout = 0.1).click()
	time.sleep(0.2)
	page.ele('@class:dropdown-menu show').ele(f'tag:a@@text():{timingOffset[tOIdx]}').click()

class MENU(IntEnum):
	LIVE_UPDATE = 0
	PROVISIONING = auto()
	REBOOT = auto()
	UPGRADE_FIRMWARE = auto()

class TAB(IntEnum):
	SA = 2
	MULTI_PLMN = auto()
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
	TIMING_OFFSET = 0
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

def main(args=None):
	if args is None:
		parser = argparse.ArgumentParser(description="Load configuration files")
		parser.add_argument("-p", "--provision", nargs="?",default="", help="additional provision file to load")
		args = parser.parse_args()
	else:
		# print(args)
		args = argparse.Namespace(**args)
		print(args.provision)

	provision = {}
	with open("BASIC.json", 'r') as f:
		provision.update(Config(**json.load(f)).__dict__)

	if args.provision is not "":
		with open("unit_test/"+args.provision, 'r') as f:
			provision.update(Config(**json.load(f)).__dict__)

	radio_list = ['NR_BAND', 'BANDWIDTH', 'TIMESLOT']
	radio = {key: provision.pop(key) for key in radio_list}

	with open("config.json", 'r') as f:
		data = json.load(f)
	config = Config(**data)

	download_directory = os.path.dirname(__file__)
	co = ChromiumOptions()
	co.set_pref('download.default_directory', download_directory)
	co.set_argument('--window-size', '1920,1080')
	co.set_timeouts(base=10)
	co.ignore_certificate_errors()
	co.incognito()
	# co.headless()

	if os.path.exists('../chrome-win/chrome.exe'):
		co.set_browser_path('../chrome-win/chrome.exe')
		
	elif os.path.exists("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"):
		co.set_browser_path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")

	page = ChromiumPage(co)
	# atexit.register(close_driver, page)

	page.get(config.login_url)
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
	columnheader = page.eles("@@class:datatable-header-cell resizeable ng-star-inserted")
	tb_serial_number = columnheader[0].ele('tag:input@type=text')

	msgLogger("searching SN...")
	tb_serial_number.input(serial_number)

	time.sleep(2)
	# loc = (By.XPATH, f'//div[@class="text-truncate ng-star-inserted" and contains(text(), "{serial_number}")]')
	# link_small_cell = page.ele(loc)
	link_small_cell = page.ele(f'@@class:text-truncate ng-star-inserted@@text():{serial_number}')
	link_small_cell.click()
	time.sleep(1)

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
	set_SA_value(page, provision, li_elements)

	msgLogger("setting the multi PLMN configs...")
	tab = page.eles('@class:nav-item ng-star-inserted')
	tab[TAB.MULTI_PLMN].click()
	time.sleep(0.5)
	ismultiPLMN = checkmultiPLMN(page, provision["PLMN"])
	status = page.eles("#cuconfig")[0].ele("@@class:text-truncate@@class:badge-pill").text
	if ismultiPLMN and status == "Product":
		page.ele("tag:app-default-provisioning").ele(".ng-star-inserted").click()
	if ismultiPLMN:
		set_MULTI_PLMN_value(page, provision["PLMN"])

	msgLogger("setting the radio configs...")
	tab = page.eles('@class:nav-item ng-star-inserted')
	tab[TAB.DEPLOYMENT].click()
	time.sleep(0.5)
	li_elements = page.ele('tag:ul@class:list-group').eles('tag:li')
	set_DEPLOY_value(page, radio, li_elements)

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
	button_menu = page.eles('@@class:btn@@class:btn-primary@@class:ng-star-inserted')
	button_menu[MENU.REBOOT].click()
	page.ele('tag:button@@text():OK').click()
	msgLogger("finish! reboot now...")

	# time.sleep(200)

if __name__ == "__main__":
    main()