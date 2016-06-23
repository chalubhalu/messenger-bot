## Filename: server.py 
 
import requests
import json
import os
import sys
from flask import Flask, request

app = Flask(__name__)
 
@app.route('/webhook', methods=['GET'])
def handle_verification():
	if request.args['hub.mode'] == 'subscribe' and request.args['hub.verify_token'] == 'chalubhalu':
		print 'Validating webhook.'
		return request.args['hub.challenge']
	else:
		print 'Failed validation. Make sure the validation tokens match.'
		return 'Token Mismatch.'
	return "ok", 200

ACCESS_TOKEN = "" #Add access token



def reply(user_id, msg):
	data = {
		"recipient": {"id": user_id},
		"message": {"text": msg}
	}
	resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
	print(resp.content)


def get_status(message_text, flag):
	url = "http://api.railwayapi.com/pnr_status/pnr/" + message_text + "/apikey/<API_KEY>/" # Add API key
	r = json.loads(requests.get(url).content)
	if r['response_code'] == 410:
		return "PNR Flushed."
	elif r['response_code'] == 404:
		return "Service Down."
	elif r['response_code'] == 204:
			return "Indian Railways Server Not Responding."
	elif r['response_code'] == 200:
		return str("Train Name: " + r['train_name'] + "\nDate of Journey: " + r['doj'])
	print str(r)


def get_result(message_text):
	if message_text.isdigit():
		return get_status(message_text, 0)
	else:
		return "Invalid input! Please Enter a correct PNR!"


@app.route('/webhook', methods=['POST'])
def handle_incoming_messages():
	
	# Endpoint for processing incoming messaging events
	data = request.get_json()
	
	if data["object"] == "page":
		for entry in data["entry"]:
			for messaging_event in entry["messaging"]:
				if messaging_event.get("message"):  # someone sent us a message
					
					sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
					recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
					message_text = messaging_event["message"]["text"]  # the message's text
					
					reply_content = get_result(message_text)
					reply(sender_id, reply_content)
	return "ok", 200

 	
@app.route('/')
def index():
	return "Hello Heroku!"


if __name__ == '__main__':
    app.run(debug=True)