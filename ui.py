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
import threading

import sys
import importlib
import customtkinter as ctk

class UI(ctk.CTk):
	def __init__(self):
		super().__init__()

		# 設定 UI 外觀和主題
		root = os.path.join(os.path.dirname(os.path.abspath(__file__)))
		theme_path = os.path.join(root, "blue_16.json")

		UT = ["default"]
		for f in os.listdir(os.path.join(root,"unit_test")):
			# print(os.path.splitext(f)[0])
			res = re.search(r"(.*)\.json$", f)
			if res:
				UT.append(res.group(1))

		Custom = ["none"]
		for f in os.listdir(os.path.join(root,"customization")):
			# print(os.path.splitext(f)[0])
			res = re.search(r"(.*)\.txt$", f)
			if res:
				Custom.append(res.group(1))


		ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
		ctk.set_default_color_theme(theme_path)  # Themes: blue (default), dark-blue, green

		def optionmenu_UT_callback(choice):
			print("unit test:", choice)

		def optionmenu_custom_callback(choice):
			print("customization:", choice)

		def button_event(selected_button):
			self.button_mode_var.set(selected_button)
			print(f"Current selection: {self.button_mode_var.get()}") 
			if selected_button == "web":
				self.button_mode1.configure(fg_color="#3B8ED0", text_color="#DCE4EE", hover_color="#36719F")
				self.button_mode2.configure(fg_color="#DCE4EE", text_color="#3B8ED0", hover_color="#C0C0C3")  
			elif selected_button == "amp":
				self.button_mode1.configure(fg_color="#DCE4EE", text_color="#3B8ED0", hover_color="#C0C0C3")  
				self.button_mode2.configure(fg_color="#3B8ED0", text_color="#DCE4EE", hover_color="#36719F")

		def run_module(module_name, args):
			try:
				module = importlib.import_module(module_name)
				if hasattr(module, "main"):
					print(f"Starting {module_name}.main with args: {args}")
					module.main(args)
				else:
					print(f"The module {module_name} does not have a main function!")
			except ImportError as e:
				print(f"Error importing module {module_name}: {e}")

		def button_start_event():
			self.button_start.configure(state="disabled")
			button_mode = self.button_mode_var.get()
			unit_test = self.optionmenu_UT.get()
			customization = self.optionmenu_custom.get()

			print(f'button_mode_var = {self.button_mode_var.get()}')
			print(f'unit_test = {self.optionmenu_UT.get()}')
			print(f'customization = {self.optionmenu_custom.get()}')

			args = {}
			if unit_test != "default":
				args["provision"] = f"{unit_test}.json"
			else:
				args["provision"] = ""

			if customization != "none":
				args["custom"] = f"{customization}.txt"
			else:
				args["custom"] = ""


			module_name = "web_main" if button_mode == "web" else "amp_main"
			
			def threaded_task():
				run_module(module_name, args)
				self.button_start.configure(state="normal")
			thread = threading.Thread(target=threaded_task)
			thread.start()
			
		class DualOutputRedirector:
			def __init__(self, textbox, original_stdout):
				self.textbox = textbox  # Textbox 控件
				self.original_stdout = original_stdout  # 原始的 stdout

			def write(self, text):
				# 輸出到 Textbox
				self.textbox.insert("end", text)
				self.textbox.see("end")  # roll to bottom
				# 輸出到 CMD
				self.original_stdout.write(text)

			def flush(self):
				self.original_stdout.flush()	

        # 設置主視窗
		self.geometry("1000x600")
		self.grid_columnconfigure((0, 1), weight=1)
		self.title("Aski Bot")
		self.grid_columnconfigure(0, weight=1)  
		self.grid_columnconfigure(1, weight=2)  
		self.grid_columnconfigure(2, weight=2)  

		self.grid_rowconfigure(0, weight=1) 

		btn_width = 85
		btn_height = 40
		opm_width = 180

		self.frame1 = ctk.CTkFrame(master=self)
		self.frame1.grid(row=0, column=0, padx=(20,10), pady=(10,10), sticky="ewsn")
		self.frame1.grid_columnconfigure(0, weight=1)  
		self.frame1.grid_columnconfigure(1, weight=1)  

		self.label_mode = ctk.CTkLabel(self.frame1, text='web/amp', anchor="center")
		self.label_mode.grid(row=0, column=0, padx=20, pady=(50,30),)
		self.frame_button = ctk.CTkFrame(self.frame1, fg_color='#DBDBDB')
		self.frame_button.grid(row=0, column=1, padx=20, pady=(50,30),)
		self.button_mode_var = ctk.StringVar(value="web")
		self.button_mode1 = ctk.CTkButton(self.frame_button, text="web", width=btn_width, height=btn_height, command=lambda: button_event("web"))
		self.button_mode1.grid(row=0, column=0, padx=(0,5), pady=(0,0), sticky="w")
		self.button_mode2 = ctk.CTkButton(self.frame_button, text="amp", width=btn_width, height=btn_height, command=lambda: button_event("amp"))
		self.button_mode2.grid(row=0, column=1, padx=(5,0), pady=(0,0), sticky="w")

		self.button_mode1.configure(fg_color="#3B8ED0", text_color="#DCE4EE", hover_color="#36719F")
		self.button_mode2.configure(fg_color="#DCE4EE", text_color="#3B8ED0", hover_color="#C0C0C3") 

		self.label_UT = ctk.CTkLabel(self.frame1, text='unit test', anchor="center")
		self.label_UT.grid(row=1, column=0, padx=20, pady=(30,30),)
		self.optionmenu_UT = ctk.CTkOptionMenu(self.frame1, values=UT, width=opm_width, command=optionmenu_UT_callback)
		self.optionmenu_UT.grid(row=1, column=1, padx=20, pady=(30,30),)

		self.label_custom = ctk.CTkLabel(self.frame1, text='customization', anchor="center")
		self.label_custom.grid(row=2, column=0, padx=20, pady=(30,30),)
		self.optionmenu_custom = ctk.CTkOptionMenu(self.frame1, values=Custom, width=opm_width, command=optionmenu_custom_callback)
		self.optionmenu_custom.grid(row=2, column=1, padx=20, pady=(30,30),)

		self.button_start = ctk.CTkButton(self.frame1, text="start", width=btn_width*2, height=btn_height, command=button_start_event)
		self.button_start.grid(row=3, column=0, columnspan=2, padx=(0,0), pady=(80,20),)

		self.frame2 = ctk.CTkFrame(master=self)
		self.frame2.grid(row=0, column=1, columnspan=2, padx=(10,20), pady=(10,10), sticky="sn")
		self.output_textbox = ctk.CTkTextbox(self.frame2, width=500, height=560)
		self.output_textbox.grid(row=0, column=0, padx=(20,20), pady=(10,10), sticky="ew")

		original_stdout = sys.stdout  # 保存原始 stdout
		sys.stdout = DualOutputRedirector(self.output_textbox, original_stdout)

	def show_frame(self, frame):
		frame.grid()

	def hide_frame(self, frame):
		frame.grid_remove()

if __name__ == "__main__":
	ui = UI()
	ui.mainloop()