#! /usr/bin/python3

import requests, json

BASEURL = "http://localhost:8983/solr/OAG"

def getLatestIds(query="*:*"):
	url = BASEURL + "/select"
	querystring = {"q":query, "fl": "id", "start": 1430000, "rows": 14163}
	ids_list = None

	response = requests.request("GET", url, params=querystring)
	json_data = json.loads(response.text)
	docs = json_data['response']['docs']

	if docs:
		ids_list = [doc['id'] for doc in docs]

	return ids_list


def getDocByQuery(query):
	url = BASEURL + "/select"
	querystring = {"q":query, "fl": "id"}
	id = None

	response = requests.request("GET", url, params=querystring)
	json_data = json.loads(response.text)
	doc = json_data['response']['docs']

	if doc:
		id = doc[0]['id']

	return id
