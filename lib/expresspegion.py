from django.conf import settings
import requests
import json

def EmailSendPegion(to, merage_fields, subject, template_id):
	headers = {
			'X-auth-key': settings.PEGION_TOKEN,
			'Content-type': 'application/json'
	}
	dataValues = {
		    'template_id': template_id,
		    'reply_to': 'flexsin.nodejs@gmail.com',
		    'from': 'MIMIC Trading',
		    'to': to,
		    'subject': subject,
		    'merge_fields': merage_fields,
		}
	response = requests.post(settings.PEGION_LINK+'messages', json=dataValues, headers=headers, verify=False)
	print ("response text: ", response.text)
	return True
