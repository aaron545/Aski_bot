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

def loading(page, target):
	loadingBar = page.ele("#loadingBar")
	loadingBar.attr("style")
	while "display: none" not in loadingBar.attr("style"):
		msgLogger(f"{target} is loading......")
		time.sleep(1)

def set_SNSSAI(page, value):
	while True:
		time.sleep(0.5)
		tbody = page.ele("#modal_edit_plmn_list").eles("tag:tbody")
		snssai_length = len(tbody)-1
		print(f'value length = {len(value)}, SNSSAI length = {snssai_length}')
		if len(value) < snssai_length:
			tbody[1].ele("#id_Delete").click()
			page.ele("#cfm_box").ele("tag:a@@name:box_ok").click()
			time.sleep(0.5)
		elif len(value) > snssai_length:
			tbody[-1].ele("#id_Add").click()
			time.sleep(0.5)
		else:
			break

	print("start to set snssai")
	for i in range(snssai_length):
		tbody[i].ele("@@id:sst").clear()
		tbody[i].ele("@@id:sst").input(value[i]["SST"])
		tbody[i].ele("#edit_sd_disable").click()
		if value[i]["SD"] == "16777215":
			page.ele(". css-q5jbor-menu").ele(f"text:Disabled").click()
		else:
			page.ele(". css-q5jbor-menu").ele(f"text:Enabled").click()
			tbody[i].eles("@@id:sd")[1].clear()
			tbody[i].eles("@@id:sd")[1].input(value[i]["SD"])
	page.ele("#modal_edit_plmn_list").ele("#id_Save").click()

def set_PLMN(page,value):
	while True:
		tbody = page.ele("#modal_edit_plmn_list").eles("tag:tbody")
		plmn_length = len(tbody)-1
		print(f'value length = {len(value)}, plmn length = {plmn_length}')
		if len(value) < plmn_length:
			tbody[1].ele("#id_Delete").click()
			page.ele("#cfm_box").ele("tag:a@@name:box_ok").click()
			time.sleep(0.5)
		elif len(value) > plmn_length:
			tbody[-1].ele("#id_Add").click()
			time.sleep(0.5)
		else:
			break
	print("start to set plmn")
	for i in range(plmn_length):
		tbody = page.ele("#modal_edit_plmn_list").eles("tag:tbody")
		tbody[i].ele("@@id:mcc").clear()
		tbody[i].ele("@@id:mcc").input(value[i]["MCC"])
		tbody[i].ele("@@id:mnc").clear()
		tbody[i].ele("@@id:mnc").input(value[i]["MNC"])
		tbody[i].ele("#id_SNSSAI").click()
		set_SNSSAI(page, value[i]["SNSSAI"])
	page.ele("#modal_edit_plmn_list").ele("#id_Save").click()

def set_AMF_IP(page, value):
	amf_ip_concat = ", ".join(value)
	print(amf_ip_concat)
	if amf_ip_concat != page.ele("#amf_ip").attr("value"):
		page.ele("#amf_ip").click()
		while True:
			tbody = page.ele("#modal_edit_amf_ip").eles("tag:tbody")
			amf_ip_number = len(tbody)-1
			print(f'value length = {len(value)}, amf_ip_number length = {amf_ip_number}')
			if len(value) < amf_ip_number:
				tbody[1].ele("#id_Delete").click()
				page.ele("#cfm_box").ele("tag:a@@name:box_ok").click()
				time.sleep(0.5)
			elif len(value) > amf_ip_number:
				tbody[-1].ele("#id_Add").click()
				time.sleep(0.5)
			else:
				break
		for i in range(amf_ip_number):
			tbody[i].ele("@@type:text").clear()
			tbody[i].ele("@@type:text").input(value[i])
		page.ele("#modal_edit_amf_ip").ele("#id_OK").click()
		time.sleep(0.5)

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

class RF(IntEnum):
	RFPower = 0
	AntennaPath = auto()

def main(args=None):
	if args is None:
		parser = argparse.ArgumentParser(description="Load configuration files")
		parser.add_argument("-p", "--provision", nargs="?",default="", help="additional provision file to load")
		parser.add_argument("-c", "--custom", nargs="?", default="", help="customization config to load")
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

	uplink_list = ['MODULATION', 'LAYER', 'DRMS']
	uplink = {key: provision.pop(key) for key in uplink_list}
	provision.update(uplink)

	with open("config.json", 'r') as f:
		config = Config(**json.load(f))

	if args.custom is not "":
		with open("customization/"+args.custom, 'r') as f:
			text = f.read()
		isCustom = True
	else:
		isCustom = False

	CU_list = ["gnb_n2_ip", "gnb_n3_ip", "gnb_id", "gnb_id_length", "cell_id", "tac", "plmn", "amf_ip"]
	DU_list = ["nr_band", "physical_cell_id", "modulation", "layer", "drms","bandwidth", "nrarfcn", "timeslot"]

	textbox_list = ["gnb_n2_ip", "gnb_n3_ip", "gnb_id", "gnb_id_length", "cell_id", "tac", "physical_cell_id"]
	checkbox_list = ["modulation", "layer", "drms"]
	selectmenu_list = ["nr_band"]
	selectmenu_profile_list = ["bandwidth", "nrarfcn", "timeslot"]

	N3_targets = ["SCE2200", "SCU2050", "SCU2060", "SCU2070", "SCU5000"]

	co = ChromiumOptions()
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

	root = config.web_root

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
	loading(page, "home page")

	msgLogger("try to close reminderBlock...")

	if len(page.ele("#popup_clone").eles("tag:div",timeout=1)) == 0:
		msgLogger("not need to close")
	else:
		reminderBlock = page.ele("#popup_clone").ele(".wrap_pop1 modal-content", timeout=5)
		reminderBlock.ele("tag:a@@text():OK").click()
		msgLogger("OK")
		time.sleep(1)
	# ----------------------get software_version----------------------
	msgLogger("get software version info...")
	software_version_info = page.ele("#software_version").text
	isN3 = True if any(target in software_version_info for target in N3_targets) else False

	# ----------------------Customization config----------------------
	if isCustom:
		msgLogger("ready to setting customization config")
		if "configuration" not in page.url:
			page.ele("tag:a@@href=/configuration/gNB").click()
			loading(page, "gNB page")
		page.ele("tag:a@@href=/configuration/gNBCustomization").click()
		loading(page, "gNBCustomization page")
		page.ele("#id_Edit").click()

		textbox = page.ele("#customization_content")
		if textbox.text is not None:
			textbox.clear()
		textbox.input(text)
		
		page.ele("#id_Save").click()
		page.ele("#cfm_box").ele("tag:a@@name:box_ok").click()
		time.sleep(1)
		loading(page, "cfm_box block")
		msgLogger("cfm_box is visible...")

		page.ele("#cfm_box").ele("tag:a@@name:box_x").click()
		time.sleep(1)
	else :
		msgLogger("Not need to add customization config...")
	# ----------------------Set RF----------------------
	msgLogger("ready to setting RF Antenna")
	if "configuration" not in page.url:
		page.ele("tag:a@@href=/configuration/gNB").click()
		loading(page, "gNB page")
		page.ele(".modal fade show").ele("tag:a@@name:box_ok").click()
		time.sleep(0.5)

	msgLogger("switch to RF Antenna...")
	page.ele("tag:a@@href=/configuration/rf").click()
	time.sleep(1)
	loading(page, "RF Antenna page")

	saveRF = False

	RFSelectmenu = page.eles(". css-b62m3t-container")
	if RFSelectmenu[RF.RFPower].text == "OFF":
		RFSelectmenu[RF.RFPower].click()
		page.ele(". css-4o2p2z-menu").ele("text:ON").click()
		time.sleep(0.5)
		saveRF = True

	TXPower = page.ele("#max_tx_power")
	if float(provision["POWER"])/10 != float(TXPower.attr("value")):
		TXPower.clear()
		TXPower.input(float(provision["POWER"])/10)
		saveRF = True

	if RFSelectmenu[RF.AntennaPath].text == "External":
		RFSelectmenu[RF.AntennaPath].click()
		page.ele(". css-4o2p2z-menu").ele("text:Internal").click()
		time.sleep(0.5)
		saveRF = True

	if saveRF:
		msgLogger("save RF Antenna...")
		page.ele("#id_Save").click()
		page.ele("#cfm_box").ele("tag:a@@name:box_ok").click()
		time.sleep(1)
		loading(page, "msg_box block")
		msgLogger("msg_box is visible...")

		page.ele("@class:modal fade show").ele("tag:a@@name:box_ok").click()
		time.sleep(1)
		loading(page, "setting change")
	else:
		msgLogger("Not need to modify RF Antenna...")

	# ----------------------Switch to configuration----------------------
	msgLogger("switch to gNB configuration...")
	page.ele("tag:a@@href=/configuration/gNB").click()
	time.sleep(1)
	loading(page, "gNB page")
	page.ele(".modal fade show").ele("tag:a@@name:box_ok").click()
	time.sleep(0.5)

	# ----------------------Modify parameters----------------------
	msgLogger("ready to start modifying parameters")

	# current is CU or DU page
	styleAttr = page.ele("tag:div@@class:switchBtn").attr("style")
	styleValue = re.search(r"left:\s*(\d+)px", styleAttr).group(1)
	isCU = True if int(styleValue) > 50 else False # CU: 217px / DU 3px

	# switch between remote and local
	Method = "local"
	page.ele(f"tag:label@@for:{Method}").click()

	isIPsec = ''
	# isASK = False if len(page.eles(".SD_select css-b62m3t-container")) == 1 else True
	isASK = False
	print("isASK =", isASK)
	if isASK:
		# isIPsec = True if page.eles(".SD_select css-b62m3t-container")[0].text == "Enabled" else False
		# print("isIPsec =", isIPsec)
		if page.eles(".SD_select css-b62m3t-container")[0].text != "Enabled":
			page.eles(".SD_select css-b62m3t-container")[0].click()
			page.ele(". css-4o2p2z-menu").ele("text:Enabled").click()
			time.sleep(0.5)

		page.ele("#security_gateway").clear()
		page.ele("#security_gateway").input(config.security_gateway)
		page.ele("#ipsec_right_subnet").clear()
		page.ele("#ipsec_right_subnet").input(config.ipsec_right_subnet)


	for key, value in provision.items():
		if key == "EPSFB" or key == "POWER":
			continue

		# switch gNB CU and DU
		if (key.lower() in CU_list) != isCU:
			page.ele("tag:div@@class:switchBtn").click()
			isCU = not isCU

		if key == "PLMN":
			page.ele("#plmn_list").click()
			set_PLMN(page, value)

		if key == "AMF_IP":
			page.ele("#amf_ip").click()
			set_AMF_IP(page, value)

		if key.lower() in textbox_list:
			print(key.lower(), "=", value)
			if key == "GNB_N3_IP" and not isN3:
				continue
			if key == "GNB_N3_IP" and page.ele("#gnb_n3_ip").attr("disabled") is not None:
				page.ele("tag:label@@for:specific_n3_ip").click()

			textbox = page.ele(f"#{key.lower()}")
			textbox.clear()
			textbox.input(value)

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
	page.ele("#cfm_box").ele("tag:a@@name:box_ok").click()
	time.sleep(1)
	loading(page, "cfm_box block")
	msgLogger("cfm_box is visible...")

	page.ele("#cfm_box").ele("tag:a@@name:box_ok").click()
	msgLogger("finish! reboot now...")

if __name__ == "__main__":
    main()