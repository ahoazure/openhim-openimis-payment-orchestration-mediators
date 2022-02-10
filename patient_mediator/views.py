from django.shortcuts import render
from requests.exceptions import ConnectionError

"""
Settings for openhim Patient mediator developed in Django.

The python-based Patient mediator implements python-utils 
from https://github.com/de-laz/openhim-mediator-utils-py.git.

For more information on this file, contact the Python developer
Stephen Mburu:ahoazure@gmail.com

"""

from django.shortcuts import render

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import http.client

import urllib3
import requests
from datetime import date
from datetime import datetime
from openhim_mediator_utils.main import Main
from time import sleep
import json

from mainconfigs.models import configs
from mainconfigs.views import configview
import http.client
import base64


@api_view(['GET', 'POST'])
def getClient(request):
	result = configview()
	configurations = result.__dict__
	authvars = configurations["data"]["openimis_user"]+":"+configurations["data"]["openimis_passkey"]
	# Encode openIMIS user credentials using Base64 Encoding scheme
	encodedBytes = base64.b64encode(authvars.encode("utf-8"))
	encodedStr = str(encodedBytes, "utf-8")
	auth_openimis = "Basic " + encodedStr
	
	"""
	Hit the openIMIS upstream server and load the endpoints via port 8000
	If run on dev server, url returns https://localhost:8443/fineract-provider/api/v1/clients/
	Invalid endpoint returns JSONDecodeError at /api/api_fhir_r4/Claim (value ecpected at row1,col1) 
	Caution: To secure the endpoint with SSL certificate,FQDN is required 
	"""	

	if request.method == 'GET':
		openimisurl = configurations["data"]["openimis_url"]+"/api/api_fhir_r4/Patient"
		# import pdb; pdb.set_trace()	
		querystring = {"":""}
		payload = "Nothing to Show!"
		headers = { # modified headers to pass tenant header specific to MIFOS
			'Authorization': auth_openimis,
			'Accept': "application/json",
			'Fineract-Platform-TenantId':'default',
			} 

		# to by-pass self-signed certificate, add verify=false in the response parameters 
		response = requests.request("GET", openimisurl, data=payload, headers=headers, params=querystring,verify=False) #by-pass Cert verificartion
		try: # this try block captures JSON decode exception caused by invalid API endpoint
			json_data = json.loads(response.text) # Convert string into JSON object to facilitate selecting dataset to be rendered
			payload = json_data # returns raw data retrieved from openIMIS			
		except ValueError:
			 pass
		
		return Response(payload)
	
	elif request.method == 'POST':
		mifosauth = configurations["data"]["mifos_user"]+":"+configurations["data"]["mifos_passkey"]
		tenant = configurations["data"]["mifos_tenant"]
		mifosurl = configurations["data"]["mifos_url"]+"/fineract-provider/api/v1/clients" #mifos endpoint
   
		# Encode openIMIS user credentials using Base64 Encoding scheme
		encodedBytes = base64.b64encode(mifosauth.encode("utf-8"))
		encodedStr = str(encodedBytes, "utf-8")
		auth_mifos = "Basic " + encodedStr
		querystring = {"":""}
		try: # this captures JSON decode exception caused by invalid API endpoint
			data = json.dumps(request.data) # Convert request data into JSON
			data_dict = json.loads(data) # Convert JSON into Python Dict
			
			keymap = {  # openIMIS Patient to MIFOS Client mapping dictionary
						'id':'externalId',
						'name':'fullname',
						'given':'firstname',
						'family':'lastname',
						'use':'official'
						}

			"""
			The following statemements are responsible for calling transformations recursive functions responsible for mapping FHIR R4
			Patient attributes to MIFOS X attributes. The first task is to call transform_merged_subdictionaries that slices the nested 
			JSON object into subdictionaries function to replace the old keys with keys from the mapping dict 
			"""
			merge_payload = transform_merged_subdictionaries(data_dict)

			transformed_payload = replace_keys(merge_payload, keymap) # call the recursive function to replace the old keys with keys from the mapping dict     	
			payload = json.dumps(transformed_payload) #Reconvert Python object into string to avoid invalid format
			
			headers = { # append authorization headers to the post request. tenant is compulsory
				'Authorization': auth_mifos,
				'Content-Type': "application/json",
				'Fineract-Platform-TenantId':tenant,
				}
			
			response = requests.request("POST", mifosurl, data=payload, headers=headers, params=querystring,verify=False)			
			data_dict = json.loads(response.text) # assign response data to python dictionary
		except ValueError:
			pass
		
		return Response(data_dict) # return the dataset to openHIM mediator


"""
This function receives dict from getClient JSON POST that has been transformed into Python dict
and the transforms the OpenIMIS attributes to match those defined in MIFOS client API endpoint.
Check on https://www.youtube.com/watch?v=1vrQIdMF4LY to develop apscheduler that may be used to
post GET response to our MIFOS database using this transformation function
"""
def transform_merged_subdictionaries(data_dict):
    def update_name_list(lst): # extract  valued fron the dictionary list
        dct = {}
        for item in lst:
            dct.update(item)
        return dct

    for  k in list(data_dict.keys()): # iterate to find dict keys labeled fullname or name
        if k == 'name' or k == 'fullname': # It took me long to sort out empty dict returned
            lst =data_dict[k] # grab the name list from the name array and save it as list 
            flatlist=update_name_list(lst) # call update functio to populate name subdictionary
            try:
               firstname =flatlist['given'][0]+ " "+flatlist['given'][1]# concatenate names from sublist
            except IndexError:
               firstname =flatlist['given'][0]# if only one, take the given name and assign to firstname				

            lastname =flatlist['family']
            names_dict={'firstname':firstname,'lastname':lastname}            
           
            """
            Remove the following attributes from the payload coz they are not supported by MIFOS
            """
			
            data_dict.pop(k) #remove the name dictionary list from transformed payload
            # data_dict['dateOfBirth'] = data_dict.pop('birthDate') #transform date of birth

            key_to_lookup = 'birthDate'
            if key_to_lookup in data_dict:
               data_dict['dateOfBirth']=data_dict.pop(key_to_lookup)	

            key_to_lookup = 'resourceType'
            if key_to_lookup in data_dict:
               data_dict.pop(key_to_lookup)	

            key_to_lookup = 'gender'
            if key_to_lookup in data_dict:
               data_dict.pop(key_to_lookup)				

            key_to_lookup = 'identifier'
            if key_to_lookup in data_dict:
               data_dict.pop(key_to_lookup)	

            key_to_lookup = 'extension'
            if key_to_lookup in data_dict:
               data_dict.pop(key_to_lookup)	

            key_to_lookup = 'address'
            if key_to_lookup in data_dict:				
               data_dict[key_to_lookup][0].pop('extension')
               data_dict[key_to_lookup][0].pop('use')	
               data_dict[key_to_lookup][0].pop('type')	
               data_dict[key_to_lookup][0].pop('text')	  
               data_dict[key_to_lookup][0].pop('city') 
               data_dict[key_to_lookup][0].pop('district')
               data_dict[key_to_lookup][0].pop('state')
               data_dict[key_to_lookup][0]['addressTypeId']=1
            #    data_dict[key_to_lookup][0]['street']='Nairobi'

            key_to_lookup = 'photo'
            if key_to_lookup in data_dict:
               data_dict.pop(key_to_lookup)

            key_to_lookup = 'maritalStatus'
            if key_to_lookup in data_dict:
               data_dict.pop(key_to_lookup)

            key_to_lookup = 'contact'			   
            if  key_to_lookup in data_dict:
               data_dict.pop(key_to_lookup)

            key_to_lookup = 'telecom'			   
            if  key_to_lookup in data_dict:
               data_dict.pop(key_to_lookup)
           
            """
            This statement uses Python 3.5+ vocabulary represented by ** to merge the two transfomed (data_dict and names_dict)
			sub-dictionaries before calling the rename function that does the final job of converting FHIR R4 attributes
			into MIFOS x compliant dictionary (json payload)
            """
            chained_dict = {**data_dict,**names_dict} # use Python3 vocabulary (**) to merge transformed subdictionaries
            
            """ 
            These attributes have been added to transformed Python dictionary because they are mandatory
			fields required when registering a client with MIFOS X. Good practice is to grab specific
			office id, locale and activation date from MIFOS client and/or openIMIS Patient endpoints
            """
            defaultdate = datetime.today().strftime('%Y-%m-%d') #grab default date 
            chained_dict['officeId'] = '1'
            chained_dict['dateFormat'] = 'yyyy-M-d' # recheck to conform to mifos format
            chained_dict['locale'] = 'en'
            chained_dict['active'] = 'true'
            chained_dict['activationDate'] = defaultdate 		
    return chained_dict 

"""
This is a recursive function that receives transformed dict from transform_merged_subdictionaries and replaces the 
openIMIS Patient keys with those defined in the keymap. The keymap is a dictionary that maps Patient keys to MIFOS 
client attributes exposed by register client API endpoint.
"""
def replace_keys(data_dict, key_dict):
    new_dict = { }
    if isinstance(data_dict, list): # check whether the object is an array [list]
        dict_value_list = list() # if true, assign the list to dict value list
        for inner_dict in data_dict:
            dict_value_list.append(replace_keys(inner_dict, key_dict)) # recurse to replace keys in he list
        return dict_value_list # return the modified list with replaced keys
    elif isinstance(data_dict, dict): # otherwise if the object is a dictionary closed in {dict} 
        for key in list(data_dict.keys()):
            value = data_dict[key] # assign the key to temp value 				        
            new_key = key_dict.get(key, key)
            if isinstance(value, dict) or isinstance(value, list):
                new_dict[new_key] = replace_keys(value, key_dict) # recursive call to replace the old key with key from mapping dict
            else:
                new_dict[new_key] = value # no recursion if the key is at root node
        return new_dict	
    return new_dict

	
def registerClientMediator():
	result = configview()
	configurations = result.__dict__
	try: 
		# allow the app to run even if the mediator has noy been registered 
		API_URL = configurations["data"]["openhim_url"]
		
		# import pdb; pdb.set_trace()

		USERNAME = configurations["data"]["openhim_user"]
		PASSWORD = configurations["data"]["openhim_passkey"]

		options = {
		'verify_cert': False,
		'apiURL': API_URL,
		'username': USERNAME,
		'password': PASSWORD,
		'force_config': False,
		'interval': 10,
		}

		conf = {
		"urn": "urn:mediator:openhim-mediator-python-mifos-Client",
		"version": "1.0.1",
		"name": "FHIR R4 Patient Mediator",
		"description": "Python Fhir R4 Client Mediator",

		"defaultChannelConfig": [
			{
				"name": "FHIR R4 Client Mediator",
				"urlPattern": "^/fineract-provider/api/v1/clients$",
				"routes": [
					{
						"name": "FHIR R4 Client Mediator Route",
						"host": configurations["data"]["mediator_url"],
						"path": "/fineract-provider/api/v1/clients",
						"port": configurations["data"]["mediator_port"],
						"primary": True,
						"type": "http"
					}
				],
				"allow": ["admin"],
				"methods": ["GET", "POST"],
				"type": "http"
			}
		],

		"endpoints": [
			{
				"name": "Patient FHIR R4 Mediator",
				"host": configurations["data"]["mediator_url"],
				"path": "/fineract-provider/api/v1/clients",
				"port": configurations["data"]["mediator_port"],
				"primary": True,
				"type": "http"
			}
		]
		}
		openhim_mediator_utils = Main(
			options=options,
			conf=conf
			)
		openhim_mediator_utils.register_mediator() # Register python mediator with openHIM core 
		checkHeartbeat(openhim_mediator_utils) # Monitor mediator health on the console
	except ConnectionError:
		pass


# Morning the health status of the client on the console
def checkHeartbeat(openhim_mediator_utils):
	openhim_mediator_utils.activate_heartbeat()