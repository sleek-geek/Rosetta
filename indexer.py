#! /usr/bin/python3

import sys
import json
import subprocess
import xml.etree.ElementTree as ET
import time
import requests
import datetime

index_dir = "/tmp/solr/index_files"
solr_home = "/opt/solr/"
scripts_dir = "/home/azureuser/scripts/"
collection = "OAG"


def indexPaper(chunk):

	top = ET.Element('add')

	for doc in chunk.splitlines():
		try:
			doc = doc.decode('utf-8').split('\t')
			id = doc[0]
			title = doc[5]
		except Exception as e:
			print(e)
			continue

		if not id or not title:
			continue

		venue = None
		date = None
		n_citation = None
		publisher = None
		doc_type = None
		volume = None
		issue = None
		year = None

		try:
			doc_type = doc[3]
			year = doc[7]
			date = doc[8]
			publisher = doc[10]
			volume = doc[14]
			issue = doc[15]
			n_citation = doc[19]
			venue = doc[21]
		except Exception as e:
			pass

		doc = ET.SubElement(top, 'doc')
		id_field = ET.SubElement(doc, 'field',  {'name': 'id'})
		id_field.text = id
		title_field = ET.SubElement(doc, 'field',  {'name': 'title'})
		title_field.text = title

		if venue:
			venue_field = ET.SubElement(doc, 'field',  {'name': 'venue'})
			venue_field.text = venue

		if year:
			year_field = ET.SubElement(doc, 'field',  {'name': 'year'})
			year_field.text = year

		if n_citation:
			n_citation_field = ET.SubElement(doc, 'field',  {'name': 'n_citation'})
			n_citation_field.text = n_citation

		if publisher:
			publisher_field = ET.SubElement(doc, 'field',  {'name': 'publisher'})
			publisher_field.text = publisher

		if doc_type:
			doc_type_field = ET.SubElement(doc, 'field',  {'name': 'doc_type'})
			doc_type_field.text = doc_type

		if volume:
			volume_field = ET.SubElement(doc, 'field',  {'name': 'volume'})
			volume_field.text = volume

		if issue:
			issue_field = ET.SubElement(doc, 'field',  {'name': 'issue'})
			issue_field.text = issue

		if date:
			try:
				datetime.datetime.strptime(date, '%Y-%m-%d')
				date_field = ET.SubElement(doc, 'field',  {'name': 'date'})
				date_field.text = str(date)
			except:
				pass

	data = str(ET.tostring(top, 'utf-8').decode())
	url='http://localhost:8983/solr/OAG/update'
	headers =  { "content-type" : "text/xml" }

	response = requests.post(url, headers=headers, data=data.encode('utf-8'))
	commit_res = requests.post(url, headers=headers, data="<commit/>")
	print(response.text)
	print(commit_res.text)
#	f = open(scripts_dir + 'doc.xml'  , 'a')
#	f.write(str(xmlcontent))
#	f.close()

#	try:
#		output = subprocess.check_call([scripts_dir + 'store_doc.sh', solr_home + 'bin/post', collection, xmlcontent]) #, scripts_dir + 'doc.xml'])

#		if '404' in output:
#			time.sleep(60)
#			subprocess.check_call([scripts_dir + 'store_doc.sh', solr_home + 'bin/post', collection, xmlcontent])

#	except:
#		time.sleep(60)
#		subprocess.check_call([scripts_dir + 'store_doc.sh', solr_home + 'bin/post', collection, xmlcontent])
