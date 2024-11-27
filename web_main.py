from DrissionPage import ChromiumPage, ChromiumOptions
from enum import Enum, IntEnum, auto
from datetime import datetime

import pytz
import os
import atexit
import time
import argparse
import json
import re

def msgLogger(msg):
    # 取得當前時間並設置時區為台北
    date = datetime.now(pytz.timezone('Asia/Taipei'))
    
    print('--------------------------')
    print(date.strftime('%Y/%m/%d %I:%M:%S %p'))
    print(msg)
    print('--------------------------')


class Config:
	def __init__(self,**kwargs):
		# 動態設置屬性
		for key, value in kwargs.items():
			setattr(self, key, value)

class ASK_nonIPSEC_SD_select(IntEnum):
	IPSecTunnel = 0
	SD = auto()

class ASK_IPSEC_SD_select(IntEnum):
	IPSecTunnel = 0
	AuthenticationType = auto()
	SD = auto()

default_provision = ["BASIC.json", "QAM256_2L.json"]
default_radio = ["radio.json"]

parser = argparse.ArgumentParser(description="Load configuration files")
parser.add_argument("-p", "--provisions", nargs="*",default=default_provision, help="List of provision files to load")
parser.add_argument("-r", "--radio", nargs="?", default=default_radio, help="radio file to load, default is \"N78 100MHz 4:1\"")
args = parser.parse_args()

qam_file = [file for file in args.provisions if "QAM" in file]
other_files = [file for file in args.provisions if "QAM" not in file]

provision = {}
for file in other_files:
    with open(file, 'r') as f:
        provision.update(Config(**json.load(f)).__dict__)
with open(args.radio, 'r') as f:
	provision.update(Config(**json.load(f)).__dict__)
if qam_file:
	with open(qam_file[0], 'r') as f:
		provision.update(Config(**json.load(f)).__dict__)

with open("config.json", 'r') as f:
	config = Config(**json.load(f))

CU_list = ["gnb_n2_ip", "gnb_n3_ip", "gnb_id", "gnb_id_length", "cell_id", "tac", "mcc", "mnc", "amf_ip"]
DU_list = ["sst", "sd", "nr_band", "physical_cell_id", "modulation", "layer", "drms","bandwidth", "nrarfcn", "timeslot"]

textbox_list = ["gnb_n2_ip", "gnb_n3_ip", "gnb_id", "gnb_id_length", "cell_id", "tac", "mcc", "mnc", "amf_ip", "sst", "physical_cell_id"]
checkbox_list = ["modulation", "layer", "drms"]
selectmenu_list = ["nr_band"]
selectmenu_profile_list = ["bandwidth", "nrarfcn", "timeslot"]

co = ChromiumOptions()
co.set_argument('--window-size', '1920,1080')
co.set_browser_path('../chrome-win/chrome.exe')
# co.set_browser_path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
co.set_timeouts(base=10)
co.ignore_certificate_errors()
co.incognito()
# co.headless()

page = ChromiumPage(co)
root = config.web_root
# root = "https://10.1.108.129"

if page.url != root:
	page.get(root)
	time.sleep(1)

# ----------------------Login----------------------
msgLogger("waiting for login...")
try:
	page.ele('#password').input(config.web_password)
	page.ele("#btn_login").click()
except:
	msgLogger("already logined")

# ----------------------ReminderBlock----------------------
msgLogger(f"waiting for get {root}/home...")
while page.url != root+"/home":
	time.sleep(1)
time.sleep(4)

msgLogger("try to close reminderBlock...")

if len(page.ele("#popup_clone").eles("tag:div",timeout=1)) == 0:
	msgLogger("not need to close")
else:
	reminderBlock = page.ele("#popup_clone").ele(".wrap_pop1 modal-content", timeout=5)
	reminderBlock.ele("tag:a@@text():OK").click()
	msgLogger("OK")

# ----------------------Switch to configuration----------------------
msgLogger("switch to gNB configuration...")
while page.url != root+"/configuration/gNB":
	page.ele("tag:a@@href=/configuration/gNB").click()
	time.sleep(2)

# ----------------------Configuration----------------------
# switch gNB CU and DU
# page.ele("tag:div@@class:switchBtn").click()


# selectmenu 
# SD = "66051"
# SD = "Disabled"

# page.eles(".SD_select css-b62m3t-container")[SD_select.SD].click()
# if SD != "Disabled":
# 	page.ele(". css-4o2p2z-menu").ele("text:Enabled").click()
# 	page.ele("#sd").clear()
# 	page.ele("#sd").input(SD)
# else:
# 	page.ele(". css-4o2p2z-menu").ele("text:Disabled").click()

# textbox
# gnb_id = page.ele("#gnb_id")
# gnb_id.clear()
# gnb_id.input("7128")

# checkbox
# modulation = "QAM256"
# layer = "2"
# drms = "pos2"
# page.ele(f"tag:label@@for:{modulation}").click()

# if layer == "1":
# 	page.ele(f"tag:label@@for:One layer").click()
# else:
# 	page.ele(f"tag:label@@for:Two layer").click()

# if drms == "pos1":
# 	page.ele(f"tag:label@@for:Pos1").click()
# else:
# 	page.ele(f"tag:label@@for:Pos2").click()


# ----------------------Modify parameters----------------------

msgLogger("ready to start modifying parameters")
time.sleep(10)

# current is CU or DU page
styleAttr = page.ele("tag:div@@class:switchBtn").attr("style")
styleValue = re.search(r"left:\s*(\d+)px", styleAttr).group(1)
isCU = True if int(styleValue) > 50 else False

# switch between remote and local
Method = "local"
page.ele(f"tag:label@@for:{Method}").click()

isIPsec = ''
isASK = False if len(page.eles(".SD_select css-b62m3t-container")) == 1 else True
print("isASK =", isASK)
if isASK:
	# isIPsec = True if page.eles(".SD_select css-b62m3t-container")[0].text == "Enabled" else False
	# print("isIPsec =", isIPsec)
	if page.eles(".SD_select css-b62m3t-container")[0].text != "Enabled":
		page.eles(".SD_select css-b62m3t-container")[0].click()
		page.ele(". css-4o2p2z-menu").ele("text:Enabled").click()
		time.sleep(0.5)

	page.ele("#security_gateway").clear()
	page.ele("#security_gateway").input("211.75.141.110")
	page.ele("#ipsec_right_subnet").clear()
	page.ele("#ipsec_right_subnet").input("172.29.0.0/22")


for key, value in provision.items():
	if key != "EPSFB" and key != "POWER":
		if (key.lower() in CU_list) != isCU:
			page.ele("tag:div@@class:switchBtn").click()
			isCU = not isCU

		if key.lower() in textbox_list:
			print(key.lower(), "=", value)
			gnb_id = page.ele(f"#{key.lower()}")
			gnb_id.clear()
			gnb_id.input(value)

		elif key == "SD":
			if not isASK:
				page.ele("@@class:SD_select").click()
			# elif isIPsec:
			# 	page.eles("@@class:SD_select")[ASK_IPSEC_SD_select.SD].click()
			# else:
			# 	page.eles("@@class:SD_select")[ASK_nonIPSEC_SD_select.SD].click()
			else :
				page.eles("@@class:SD_select")[ASK_IPSEC_SD_select.SD].click()

			if value != "16777215": 
				print(key.lower(), "= Enabled,", value)
				page.ele(". css-4o2p2z-menu").ele("text:Enabled").click()
				page.ele("#sd").clear()
				page.ele("#sd").input(value)
			else: # disable
				print(key.lower(), "= Disabled")
				page.ele(". css-4o2p2z-menu").ele("text:Disabled").click()

		elif key == "PCI":
			print("physical_cell_id =", value)
			gnb_id = page.ele(f"#physical_cell_id")
			gnb_id.clear()
			gnb_id.input(value)

		elif key.lower() in checkbox_list:
			if key.lower() == "modulation":
				print("modulation =", value)
				page.ele(f"tag:label@@for:{value}").click()
			elif key.lower() == "layer":
				print("layer =", value)
				if value == "1":
					page.ele(f"tag:label@@for:One layer").click()
				else:
					page.ele(f"tag:label@@for:Two layer").click()
			elif key.lower() == "drms":
				print("drms =", value)
				if value == "pos1":
					page.ele(f"tag:label@@for:Pos1").click()
				else:
					page.ele(f"tag:label@@for:Pos2").click()

		elif key.lower() in selectmenu_list:
			print(key.lower(), "=", value)
			page.ele(f"@@class:{key.lower()}").click()
			page.ele(". css-4o2p2z-menu").ele(f"text:{value}").click()

		elif key.lower() in selectmenu_profile_list:
			print(key.lower(), "=", value)
			if key.lower() == "nrarfcn":
				page.ele(f"@@class:nrArfcn_profile").click()
			elif key.lower() == "timeslot":
				page.ele(f"@@class:timeSlot_profile").click()
			else:
				page.ele(f"@@class:{key.lower()}_profile").click()
			page.ele(". css-4o2p2z-menu").ele(f"text:{value}").click()	
msgLogger("finish!!!")

# save config
msgLogger("save config...")
page.ele("#id_Save").click()
time.sleep(1)

cfm_box = page.ele("#cfm_box")
if cfm_box.attr("aria-hidden") != "true":
	cfm_box.ele("tag:a@@name:box_ok").click()
	time.sleep(1)
msgLogger("waiting for cfm_box visible...")

cfm_box = page.ele("#cfm_box")
while cfm_box.attr("aria-hidden") == "true":
	cfm_box = page.ele("#cfm_box")
	time.sleep(1)
msgLogger("cfm_box is visible...")

cfm_box.ele("tag:a@@name:box_ok").click()
msgLogger("finish! reboot now...")