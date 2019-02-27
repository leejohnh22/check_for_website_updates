# CHECK IF WEBSITE IS UPDATED
# Author : John Lee
# Creation Start Date :  2/7/2019
# Updated : 2/25/2019
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
"3: DELETE WEBSITE TO TRACK FOR UPDATES",
"4: EXIT APPLICATION"
]

def main():
	# INITIALIZE VARIABLES
	#option_selected = 0

	# DISPLAY MENU
	print("ENTER OPTION NUMBER TO SELECT ACTION")
	print("------------------------------------")
	print(MENU[0])
	print(MENU[1])
	print(MENU[2])
	print(MENU[3])

	# GET USER INPUT
	option_selected = int(input())

	# USER INPUT VALIDATION
	while option_selected != 1 and option_selected != 2 and option_selected != 3 and option_selected != 4:
		print("Please enter valid option number: ")
		option_selected = int(input())

	# OPTION 1 - CHECK FOR WEBSITE UPDATES
	if option_selected == 1:
		check_for_website_updates()
	# OPTION 2 - ADD WEBSITE TO TRACK FOR UPDATES
	elif option_selected == 2:
		add_website()
	# OPTION 3 - DELETE WEBSITE TO TRACK FOR UPDATES
	elif option_selected == 3:
		delete_website()
	# OPTION 4 - EXIT
	elif option_selected == 4:
		print("Exiting application...")
		return 0

def check_for_website_updates():
	# INITIALIZE CONSTANTS
	THRESHOLD = 0.05

	# INITIALIZE VARIABLES
	returned_content = ''
	hdr = ''
	tmp_data = {}

	# SET VARIABLES
	tmp_data['websites'] = []
	tmp_website_list = tmp_data['websites']
	hdr = {'User-Agent': 'Mozilla/5.0'}

	# OPEN SAVE FILE AND READ IT FOR CURRENT HEADERS SAVED
	if os.path.isfile(SAVE_FILE):
		with open(SAVE_FILE) as save_file:
			saved_websites = json.load(save_file)
			website_list = saved_websites['websites']

			# FOR EACH WEBSITE SAVED, SEND GET REQUEST
			for website in website_list:
				get_request = requests.get(website['url'], headers = hdr)

				# IF GET REQUEST IS SUCCESSFUL COMPARE CONTENT
				if (get_request).status_code == 200:										
					returned_content = BeautifulSoup(get_request.content, 'html.parser')
					returned_header_content = returned_content.find_all(re.compile('^h[1-6]$'))
					str_returned_header_content = str(returned_header_content)
					len_headers = len(str_returned_header_content)

					if (str_returned_header_content != website['header_content']) and (abs(len_headers - len(website['header_content'])) / len_headers > THRESHOLD):
						tmp_website_list.append({
							'url' : website['url'],
							'header_content' : str_returned_header_content
							})
						print(website['url'], "has NEW updates.")

					# IF CONTENT IS SAME, SAVE OLD CONTENT
					else:
						tmp_website_list.append({
							'url' : website['url'],
							'header_content' : website['header_content']
							})
						print(website['url'], "has no updates.")

				# Print exceptions
				else:
					print("ERROR: Unable to check website", url)
					print(get_request)

					# SAVE OLD CONTENT
					tmp_website_list.append({
						'url' : website['url'],
						'header_content' : website['header_content']
						})
					print(website['url'], "has no updates.")

		# SAVE UP TO DATE CONTENT IN TMP
		with open(TMP_FILE, 'w') as tmp_file:
			json.dump(tmp_data, tmp_file)

		# DELETE OLD SAVE FILE
		if os.path.isfile(SAVE_FILE):
			os.remove(SAVE_FILE)

		# OVERWRITE OLD SAVE WITH TMP
		os.rename(TMP_FILE, SAVE_FILE)


	# IF NO WEBSITES EXIST YET, TELL USER TO ADD ONE
	else:
		print("No websites have been saved yet. Please add a website to track.")

def add_website():
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
	tmp_data['websites'] = []
	tmp_website_list = tmp_data['websites']
	hdr = {'User-Agent': 'Mozilla/5.0'}

	# SEND GET REQUEST TO URL INPUTTED
	get_request = requests.get(url, headers = hdr)

	# IF GET REQUEST IS SUCCESSFUL RETURN CONTENT AND SEARCH FOR HEADERS
	if (get_request).status_code == 200:										
		returned_content = BeautifulSoup(get_request.content, 'html.parser')
		returned_header_content = returned_content.find_all(re.compile('^h[1-6]$'))
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
							print(website['url'], "already exists and has recent updates.")

						# IF CONTENT IS SAME, SAVE OLD CONTENT
						else:
							tmp_website_list.append({
								'url' : website['url'],
								'header_content' : website['header_content']
								})
							print(website['url'], "already exists and has no recent updates.")
				
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

def delete_website():
	# INITIALIZE VARIABLES
	url = ''
	tmp_data = {}

	# SET VARIABLES
	url = "http://" + input("Enter website URL (do not include http:// or https://): ")	# get website url
	tmp_data['websites'] = []
	tmp_website_list = tmp_data['websites']

	# OPEN SAVE FILE AND READ IT FOR CURRENT HEADERS SAVED
	if os.path.isfile(SAVE_FILE):
		with open(SAVE_FILE) as save_file:
			saved_websites = json.load(save_file)
			website_list = saved_websites['websites']

			for website in website_list:
				# SAVE THE OTHERS THAT ARE NOT BEING REMOVED
				if url != website['url']:
					tmp_website_list.append({
						'url' : website['url'],
						'header_content' : website['header_content']
						})
				# IF WEBSITE IS THE ONE WE WANT TO REMOVE SKIP IT
				elif url == website['url']:
					print(url, "will no longer be tracked for updates.")

	# SAVE UP TO DATE CONTENT IN TMP
	with open(TMP_FILE, 'w') as tmp_file:
		json.dump(tmp_data, tmp_file)

	# DELETE OLD SAVE FILE
	if os.path.isfile(SAVE_FILE):
		os.remove(SAVE_FILE)

	# OVERWRITE OLD SAVE WITH TMP
	os.rename(TMP_FILE, SAVE_FILE)

main()