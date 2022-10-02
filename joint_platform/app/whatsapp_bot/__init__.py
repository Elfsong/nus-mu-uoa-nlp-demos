# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2022-10-02

from email import message
import os
import json
import openai
import requests
from . import openai_model
from . models import SimilarityModel
from collections import defaultdict
from . genre_model import GenreModel
from flask import Blueprint, request, abort

# Flask Handler
whatsapp_bot = Blueprint('wahtsapp_bot', __name__, template_folder='./templates', static_folder='./static')

# Genre Model
# genre_model = GenreModel()

# Similarity Model
similarity_model = SimilarityModel("sentence-transformers/all-MiniLM-L6-v2")

# User Session
user_session = defaultdict(dict)

# Message ID manager
seen_message_id_set = set()

# WhatsApp Token
with open("./app/whatsapp_bot/static/password") as password_f:
    passwords = json.load(password_f)
    whatsapp_token = passwords["WHATSAPP_TOKEN"]

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

def reply_msg(from_id, to_id, message_id, msg):
    headers = {
        'Authorization': f'Bearer {whatsapp_token}',
    }
    json_data = {
        'messaging_product': 'whatsapp',
        'to': to_id,
        'type': 'text',
        "context": {
            "message_id": message_id
        },
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
    current_session["stage"] = "product_location_init"

def product_location_init(current_session):
    # Solution 1: Entity Detection using GENRE
    # entity_results = genre_model.generate([message])
    # send_msg(from_id, to_id, f"Entity Result: {entity_results[0][0]}")

    # Solution 2: Entity Detection using GPT-3
    product_mentions = openai_model.product_mentions(current_session["history"][-1])
    send_msg(current_session["from_id"], current_session["to_id"], f"Mentioned Pruduct Result: {product_mentions}")
    current_session["product_check_list"] = product_mentions
    current_session["problem_description"] = current_session["history"][-1]
    current_session["product_confirmed_list"] = list()
    current_session["current_product_check"] = None

    message = "Let me check out your query. I may need some feedback to narrow down the current scope."
    send_msg(current_session["from_id"], current_session["to_id"], message)
    current_session["stage"] = "product_location"

def product_location(current_session):
    if current_session["current_product_check"]:
        answer = current_session["history"][-1].strip()
        if answer == "Confirm":
            send_msg(current_session["from_id"], current_session["to_id"], f"Confirmed! Added [{current_session['current_product_check']}] to confirmed product list.")
            current_session["product_confirmed_list"] += [current_session["current_product_check"]]
        elif answer == "Ignore":
            send_msg(current_session["from_id"], current_session["to_id"], "Ignored!")
        elif answer.startswith("Update"):
            updated_name = " ".join(answer.split(' ')[1:])
            current_session["product_check_list"] += [updated_name]
            send_msg(current_session["from_id"], current_session["to_id"], f"Add the term [{updated_name}] to checking list.")
        current_session["current_product_check"] = None

    while current_session["product_check_list"]:
        current_session["current_product_check"] = current_session["product_check_list"].pop()
        product_name, similarity_score = similarity_model.product_search(list(product_dict.keys()), current_session["current_product_check"])
        action = product_dict[product_name]["action"]
        
        if action == "Done":
            message = f'For the term [{current_session["current_product_check"]}], I found it is {similarity_score} similar with {product_name}, What do you think? \n\
            You can reply:\nConfirm - to confirm the result\nIgnore - to ignore the result\nUpdate product_name - to update the result\n'
            send_msg(current_session["from_id"], current_session["to_id"], message)
        else:
            question = openai_model.ask_production_location_question(current_session["problem_description"], action)
            message = f'For the term [{current_session["current_product_check"]}], I found it is {similarity_score} similar with {product_name}.\n\
            However, it is unclear to me. {question} Could you use the command "Update product_name" to provide the specifc product number?'
            send_msg(current_session["from_id"], current_session["to_id"], message)
        break

    if not current_session["product_check_list"] and not current_session["current_product_check"]:
        message = f"Well. As far as I know, your problem is about {current_session['product_confirmed_list']}. \n Let's move on to the next stage!"
        send_msg(current_session["from_id"], current_session["to_id"], message)
        current_session["stage"] = "situation_location"

def situation_location(current_session):
    send_msg(current_session["from_id"], current_session["to_id"], "[situation_location] Haha, I didn't implement this function yet!")


def pipeline(data):
    # Meta info
    from_id = data["metadata"]["phone_number_id"]
    to_id = data['messages'][0]["from"]
    message = data['messages'][0]["text"]["body"]
    message_id = data['messages'][0]['id']

    # 0. Restart
    if message.startswith("restart"):
        user_session[to_id] = dict()
    
    # 1. User Session
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

    # 3. Product Location
    if current_session["stage"] == "product_location_init":
        # Product Location Init
        product_location_init(current_session)
    
    if current_session["stage"] == "product_location":
        # Product Location
        product_location(current_session)

    # 4. Situation Location
    if current_session["stage"] == "situation_location":
        # Situation Location
        situation_location(current_session)

    # 4. Status Transition


# Callback handler
@whatsapp_bot.route('/callback', methods=['GET', 'POST'])
def callback():
    # Callback Validation
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token missmatch", 403
        return request.args['hub.challenge'], 200

    # Handle message
    response = request.get_json()
    # print("=" * 80)
    # print(response)

    # try:
    data = response['entry'][0]['changes'][0]['value']
    # message callback filter
    if "messages" in data:
        message_id = data['messages'][0]['id']
        # repeat message callback filter
        if message_id not in seen_message_id_set:
            seen_message_id_set.add(message_id)
            pipeline(data)
        else:
            print("Repeat Message")
    else:
        pass
        print("Other Message")
    
    return 'OK', 200
    # except Exception as e:
    #     print(f"Failed: {e}", e)
    #     return 'FAILED', 400
    


