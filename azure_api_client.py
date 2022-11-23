#! /usr/bin/python3

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.identity import DefaultAzureCredential
#from io import BytesIO
from indexer import *
#from multiprocessing.dummy import Pool as ThreadPool
from solrLib import getLatestIds, getDocByQuery
import time

SA_NAME = "magconsonto"
CONTAINER = "ma-datashare"
#pool = ThreadPool(1000)

token_credential = DefaultAzureCredential()
service = BlobServiceClient(account_url="https://" + SA_NAME + ".blob.core.windows.net/", credential=token_credential)
container_client=service.get_container_client(CONTAINER)

def listBlob():

	blob_list = container_client.list_blobs()

	for blob in blob_list:
		print(blob.name + '\n')

def streamFile(file):

	blob_client = container_client.get_blob_client(file)
	streamdownloader=blob_client.download_blob()

	for chunk in streamdownloader.chunks():
		#for line in chunk.splitlines():
		try:
			id = chunk.splitlines()[-1].decode('utf-8').split('\t')[0]

			if getDocByQuery('id:' + str(id)):
				continue
		except:
			pass

		indexPaper(chunk)
#			time.sleep(60)

#			if getDocByQuery('id:' + str(id)):
#				continue
#		print(chunk.splitlines())
#		pool.map(indexPaper, chunk.splitlines())
#	pool.map(indexPaper, streamdownloader.chunks())
#			break
#	print(streamdownloader.readall())
#listBlob()
#streamFile('mag/2021-09-13/mag/PaperUrls.txt')

#loop = asyncio.get_event_loop()
#tasks = [streamFile('mag/2021-09-13/mag/Papers.txt')]
#loop.run_until_complete(asyncio.wait(tasks))
#loop.close()
streamFile('mag/2021-09-13/mag/Papers.txt')
