# CHECK IF WEBSITE IS UPDATED
# Author : John Lee
# Creation Start Date :  2/7/2019
# Updated : 2/16/2019
# Version 1.2

import json
import os
import re
import requests
from bs4 import BeautifulSoup

# INITIALIZE CONSTANTS
SAVE_FILE = 'saved_websites.json'
TMP_FILE = 'tmp_websites.json'
MENU = [ 
"1: CHECK FOR UPDATES",
"2: ADD WEBSITE TO TRACK FOR UPDATES",
"3: DELETE WEBSITE TO TRACK FOR UPDATES"
]

def request_update():
	# INITIALIZE CONSTANTS
	THRESHOLD = 0.05

	# INITIALIZE VARIABLES
	returned_content = ''
	counter = 0
	url = ''
	hdr = ''
	tmp_data = {}

	# SET VARIABLES
	url = "http://" + input("Enter website URL (do not include http:// or https://): ")	# get website url
	hdr = {'User-Agent': 'Mozilla/5.0'}
	tmp_data['websites'] = []
	tmp_website_list = tmp_data['websites']

	# SEND GET REQUEST TO URL INPUTTED
	get_request = requests.get(url, headers=hdr)								

	# IF GET REQUEST IS SUCCESSFUL RETURN CONTENT AND SEARCH FOR HEADERS
	if (get_request).status_code == 200:										
		returned_content = BeautifulSoup(get_request.content, 'html.parser')
		returned_header_content = returned_content.find_all(re.compile('^h[1-6]$'))
		#returned_icon = returned_content.find("link", rel="shortcut icon")		# Find Icon (this will be used in the GUI)
		#str_returned_content = str(returned_content)
		str_returned_header_content = str(returned_header_content)
		len_headers = len(str_returned_header_content)

		# OPEN SAVE FILE AND READ IT FOR CURRENT HEADERS SAVED
		if os.path.isfile(SAVE_FILE):
			with open(SAVE_FILE) as save_file:
				saved_websites = json.load(save_file)
				website_list = saved_websites['websites']

				for website in website_list:
					# IF WEBSITE IS NOT THE ONE QUERIED, SAVE THE CURRENT VERSION
					if url != website['url']:
						tmp_website_list.append({
							'url' : website['url'],
							'header_content' : website['header_content']
							})

						counter += 1

					# IF WEBSITE IS THE ONE SEARCHED FOR, COMPARE CONTENT, IF NEW SAVE THE NEW CONTENT
					elif url == website['url']:
						if (str_returned_header_content != website['header_content']) and (abs(len_headers - len(website['header_content'])) / len_headers > THRESHOLD):
							tmp_website_list.append({
								'url' : website['url'],
								'header_content' : str_returned_header_content
								})
							print(website['url'], "has been updated.")

						# IF CONTENT IS SAME, SAVE OLD CONTENT
						else:
							tmp_website_list.append({
								'url' : website['url'],
								'header_content' : website['header_content']
								})
							print(website['url'], "has no updates.")
				
				# IF WEBSITE HAS NOT BEEN ADDED TO APP BEFORE, ADD TO TMP FILE AND SAVE
				if url != website['url'] and counter == len(website_list):
					tmp_website_list.append({
						'url' : url,
						'header_content' : str_returned_header_content
						})
					print(url, "will be monitored for updates.")
					
		# IF FILE DOES NOT EXIST, JUST ADD IT
		elif not os.path.isfile(SAVE_FILE):
			tmp_website_list.append({
				'url' : url,
				'header_content' : str_returned_header_content
				})

			print(url, "will be monitored for updates.")

		# SAVE UP TO DATE CONTENT IN TMP
		with open(TMP_FILE, 'w') as tmp_file:
			json.dump(tmp_data, tmp_file)

		# DELETE OLD SAVE FILE
		if os.path.isfile(SAVE_FILE):
			os.remove(SAVE_FILE)

		# OVERWRITE OLD SAVE WITH TMP
		os.rename(TMP_FILE, SAVE_FILE)

	# Print exceptions
	else:
		print("ERROR: Unable to check website", url)
		print(get_request)