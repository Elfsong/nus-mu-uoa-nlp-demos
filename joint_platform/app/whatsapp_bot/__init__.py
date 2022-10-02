# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2022-10-02

from email import message
import os
import json
import openai
import requests
from . import openai_model
from collections import defaultdict
from . genre_model import GenreModel
from flask import Blueprint, request, abort

# Flask Handler
whatsapp_bot = Blueprint('wahtsapp_bot', __name__, template_folder='./templates', static_folder='./static')

# Genre Model
# genre_model = GenreModel()

# User Session
user_session = defaultdict(dict)

# WhatsApp Token
with open("./app/whatsapp_bot/static/password", "r") as password_f:
    passwords = json.load(password_f)
    whatsapp_token = passwords["whatsapp_token"]

# Product List
product_dict = {
    "Cisco product": {
        "action": "Cisco product number"
    },
    "Cisco router": {
        "action": "Cisco router number"
    },
    "Cisco switch": {
        "action": "Cisco switch number"
    },
    "Cisco Access points": {
        "action": "Cisco Access points product number"
    },
    "Cisco Catalyst 9400 Series Switches": {
        "action": "Done"
    },
    "Cisco Catalyst 9200 Series Switches": {
        "action": "Done"
    },
    "Cisco Catalyst 9300 Series Switches": {
        "action": "Done"
    },
    "Cisco Meraki MS390 Series Switches": {
        "action": "Done"
    },
    "Cisco Catalyst 8300 Series Routers": {
        "action": "Done"
    },
    "Cisco Catalyst 8200 Series Routers": {
        "action": "Done"
    },
    "Cisco ISR 4000 Series Routers": {
        "action": "Done"
    },
    "Cisco NCS 500 Series Routers": {
        "action": "Done"
    }
}


def send_msg(from_id, to_id, msg):
    headers = {
        'Authorization': f'Bearer {whatsapp_token}',
    }
    json_data = {
        'messaging_product': 'whatsapp',
        'to': to_id,
        'type': 'text',
        "text": {
            "body": msg
        }
    }
    response = requests.post(f'https://graph.facebook.com/v13.0/{from_id}/messages', headers=headers, json=json_data)
    return response

def small_talk(current_session):
    # Send a small talk
    # TODO(mingzhe): add some diversity here
    message = "Hi! I am AsiA. I will try my best to help you:)"
    send_msg(current_session["from_id"], current_session["to_id"], message)
    
    # Transit current stage to "product_location"
    message = "Let me check out your query. I may need some feedback to narrow down the current scope."
    send_msg(current_session["from_id"], current_session["to_id"], message)
    current_session["stage"] = "product_location"

def product_location(current_session):
    # Solution 1: Entity Detection using GENRE
    # entity_results = genre_model.generate([message])
    # send_msg(from_id, to_id, f"Entity Result: {entity_results[0][0]}")

    # Solution 2: Entity Detection using GPT-3
    product_mentions = openai_model.product_mentions(current_session["history"][-1])
    send_msg(current_session["from_id"], current_session["to_id"], f"Mentioned Pruduct Result: {product_mentions}")

def pipeline(data):
    # Meta info
    from_id = data["metadata"]["phone_number_id"]
    to_id = data['messages'][0]["from"]
    message = data['messages'][0]["text"]["body"]
    
    # 0. User Session
    current_session = user_session[to_id]
    if "stage" not in current_session:
        current_session["stage"] = "small_talk"
        current_session["from_id"] = from_id
        current_session["to_id"] = to_id
        current_session["history"] = list()
    current_session["history"] += [message]

    # 2. Small talk
    if current_session["stage"] == "small_talk":
        small_talk(current_session)

    if current_session["stage"] == "product_location":
        # Product Location
        product_location(current_session)

    # 2. Product Location

    # 3. Situation Location

    # 4. Status Transition


# Callback handler
@whatsapp_bot.route('/callback', methods=['GET', 'POST'])
def callback():
    # Callback Validation
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token")== "hello":
            return "Verification token missmatch", 403
        return request.args['hub.challenge'], 200

    # Handle message
    res = request.get_json()
    try:
        data = res['entry'][0]['changes'][0]['value']
        if data['messages'][0]['id']:
            pipeline(data)
            return 'OK', 200
        return 'FAILED', 400
    except:
        return 'FAILED', 400
    


