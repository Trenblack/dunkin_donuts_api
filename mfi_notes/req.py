import requests
import uuid

url = "http://127.0.0.1:8000/"

# import hashlib
# import time

# print()


# response = requests.post(url, data={'kappa':2})

def createIdempId():
    print(uuid.uuid4())


# files = {'upload_file': open('dunkin.xml','rb')}
# print(files)
# values = {'DB': 'photcat', 'OUT': 'csv', 'SHORT': 'short'}


# r = requests.post(url, files=files, data=values)
# print(r.text)

# r = requests.get(url)
# print(r.text)

r = requests.get(url+"approve/")
print(r.text)