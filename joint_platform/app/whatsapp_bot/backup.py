# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2022-10-02

import json
import requests
from .. import socketio
from flask_socketio import emit
from . import openai_model
from .models import SimilarityModel
from collections import defaultdict
from .genre_model import GenreModel
from flask import Blueprint, request, abort, render_template

# Flask Handler
whatsapp_bot = Blueprint('wahtsapp_bot', __name__, template_folder='./templates', static_folder='./static')

# Genre Model
# genre_model = GenreModel()

# Similarity Model
similarity_model = SimilarityModel("sentence-transformers/all-MiniLM-L6-v2")

# User Session1
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
        "action": "specific Cisco product name"
    },
    "Cisco router": {
        "action": "specific Cisco router name"
    },
    "Cisco switch": {
        "action": "specific Cisco switch name"
    },
    "Cisco Access points": {
        "action": "specific Cisco Access points product name"
    },
    "Cisco 819 Series routers": {
        "action": "Done",
        "topics": {
            "resetting the router": {
                "article": """
                    # Reset Router Using Reset Button
                    To reset your router to its factory-default configuration using the Reset button:

                    With the router powered off, connect the power cord to your router, and plug the power cord into your power source.
                    Find the Reset button on the router.
                    Press and hold the Reset button while you power on the router.
                    Release the Reset button after 10 seconds.
                    Wait 5 to 10 minutes for the router to finish booting. You can check the lights on the router — when the lights are solid or blink in repeating patterns, the router is finished booting.
                    Power off your router.
                    At this point, your router is reset and will boot into its factory-default configuration the next time you power it on.

                    # Reset Router Using Router Commands
                    To reset your router to its factory-default configuration using router commands:

                    With your router powered off, connect the power cord to the router, and plug the power cord into your power source.
                    Connect your laptop to the console port on your router with the console cable.
                    Power on the router and wait 5 to 10 minutes for the router to finish booting. You can check the lights on the router — when the lights are solid or blink in repeating patterns, the router is finished booting.
                    On your laptop, start the terminal emulator program and use it to access your router’s command line interface (CLI).
                    In the router CLI, enter the commands in boldface to erase the existing configuration on your router and reload the factory-default configuration on the router: router> enable
                    router# write erase
                    Erasing the nvram filesystem will remove all configuration files! Continue? [confirm] <Press Enter key>
                    router# reload
                    Proceed with reload? [confirm] <Press Enter key>
                    -OR-
                    Would you like to enter the initial configuration dialog? [yes|no] no <Press Enter key>
                    –OR–
                    Do you want to save the configuration of the AP? [yes|no] no <Press Enter key>
                    Wait until the reload or erase finishes and a CLI prompt or completion message appears.
                    Close the terminal emulator window on your laptop.
                    Power off the router.
                    At this point, your router is reset and will boot into its factory-default configuration the next time you power it on.
                """,
                "article_link": "https://dcloud-cms.cisco.com/help/reset-router"
            },
            "Connecting an External Switch": {
                "article": """
                    To connect an external Ethernet switch to an Ethernet switch port on the router, perform these steps:
                    Step 1 Connect one end of the yellow Ethernet cable to an Ethernet switch port on the router.
                    Step 2 Connect the other end of the cable to the available port on the Ethernet switch to add additional Ethernet connections.
                    Step 3 Turn on the Ethernet switch.
                """,
                "article_link": "https://www.cisco.com/c/en/us/td/docs/routers/access/800/hardware/installation/guide/800HIG/connecting.html#pgfId-1098545"
            }
        }
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
    emit('update_log', {"log": msg, "mode": "alert-primary"}, broadcast=True, namespace="/whatsapp_bot")
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

def generate_product_sentence(product_list: list) -> str:
    if len(product_list) == 1:
        return product_list[0]
    return f'{",".join(product_list[:-1])} and {product_list[-1]}'

def generate_product_id(product_list: list) -> str:
    return "|".join(sorted(product_list))

def generate_conversation(history: list) -> str:
    conversation = ""
    for dialogue in history:
        conversation += f"{dialogue[0]}: {dialogue[1]}\n"
    return conversation

def restart_session(from_id, to_id):
    user_session[to_id] = dict()
    send_msg(from_id, to_id, "Session Restarted!")

def session_init(current_session):
    # Send a small talk
    # TODO(mingzhe): add some diversity here
    current_session["problem_description"] = current_session["history"][-1][1]
    message = openai_model.generate_greeting_sentences(current_session["problem_description"])
    send_msg(current_session["from_id"], current_session["to_id"], message)
    
    # Transit current stage to "product_location"
    current_session["stage"] = "product_location_init"

def product_location_init(current_session):
    # Solution 1: Entity Detection using GENRE
    # entity_results = genre_model.generate([message])
    # send_msg(from_id, to_id, f"Entity Result: {entity_results[0][0]}")

    # Solution 2: Entity Detection using GPT-3
    product_mentions = openai_model.product_mentions(current_session["problem_description"])
    # send_msg(current_session["from_id"], current_session["to_id"], f"Mentioned Pruduct Result: {product_mentions}")
    # print(f"Mentioned Pruduct Result: {product_mentions}")
    
    current_session["product_check_list"] = product_mentions
    current_session["product_confirmed_list"] = list()
    current_session["current_product_check"] = None

    print(current_session["product_check_list"])

    # message = "Let me check out your query. I may need some feedback to narrow down the current scope."
    # send_msg(current_session["from_id"], current_session["to_id"], message)
    current_session["stage"] = "product_location"

def product_location_backup(current_session):
    if current_session["current_product_check"]:
        answer = current_session["problem_description"].strip()
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

def product_location(current_session):
    if current_session["current_product_check"]:
        question = current_session["history"][-2][1].strip()
        answer = current_session["history"][-1][1].strip()
        entity = openai_model.understanding_production_location_answer(question, answer)
        current_session["product_check_list"] += [entity]
        current_session["current_product_check"] = None

    while current_session["product_check_list"]:
        current_session["current_product_check"] = current_session["product_check_list"].pop()
        product_name, similarity_score = similarity_model.product_search(list(product_dict.keys()), current_session["current_product_check"])
        action = product_dict[product_name]["action"]
        
        # TODO(mingzhe): check the similarity_score
        if similarity_score > 0.5 and action == "Done":
            print(product_name, similarity_score)
            current_session["product_confirmed_list"] += [product_name]
            current_session["current_product_check"] = None
        else:
            question = openai_model.ask_production_location_question(current_session["problem_description"], action)
            message = question
            send_msg(current_session["from_id"], current_session["to_id"], message)
            current_session["history"] += [("AsiA", message)]
            break

    if not current_session["product_check_list"] and not current_session["current_product_check"]:
        # message = f"Well. As far as I know, your problem is about {generate_product_sentence(current_session['product_confirmed_list'])}. Let's move on to the next stage!"
        # send_msg(current_session["from_id"], current_session["to_id"], message)
        current_session["stage"] = "situation_location_init"

def situation_location_init(current_session):
    # send_msg(current_session["from_id"], current_session["to_id"], "[situation_location] Haha, I didn't implement this function yet!")
    # Quick solution
    
    products_id = generate_product_id(current_session['product_confirmed_list'])
    context = None
    if (products_id in product_dict) and ("topics" in product_dict[products_id]):
        options = list(product_dict[products_id]["topics"].keys())
        problem_intent = openai_model.problem_intent(current_session["problem_description"], options)
        print("problem_intent: ", problem_intent)
        if problem_intent in product_dict[products_id]["topics"]:
            context = product_dict[products_id]["topics"][problem_intent]
    
    current_session["document_context"] = context

    current_session["stage"] = "situation_location"

def situation_location(current_session):
    history_str = generate_conversation(current_session["history"])

    context = "My name is AsiA. I am a very friendly Cisco tech support team crew. I will try my best to help our customers solve their problems. If I cannot solve the problem, suggest the customer call Cisco Tech Hotline 800 616 1356.\n"
    context += current_session["document_context"]["article"] if current_session["document_context"] else ""
    response = openai_model.generate_response(context, history_str)
    current_session["history"] += [("AsiA", response)]
    send_msg(current_session["from_id"], current_session["to_id"], response)

def pipeline(data):
    # Meta info
    from_id = data["metadata"]["phone_number_id"]
    to_id = data['messages'][0]["from"]
    message = data['messages'][0]["text"]["body"]
    message_id = data['messages'][0]['id']

    while True:
        # 0. Restart
        if message.startswith("RESTART"):
            print(message)
            restart_session(from_id, to_id)
            break
        
        # 1. User Session
        current_session = user_session[to_id]
        if "stage" not in current_session:
            current_session["stage"] = "small_talk"
            current_session["from_id"] = from_id
            current_session["to_id"] = to_id
            current_session["history"] = list()

        message = (message + ".") if not message.endswith((".", "?", "!")) else message
        current_session["history"] += [("Customer", message)]
        emit('update_log', {"log": message, "mode": "alert-success"}, broadcast=True, namespace="/whatsapp_bot")

        # 2. Small talk
        if current_session["stage"] == "small_talk":
            session_init(current_session)

        # 3. Product Location
        if current_session["stage"] == "product_location_init":
            # Product Location Init
            product_location_init(current_session)
        
        if current_session["stage"] == "product_location":
            # Product Location
            product_location(current_session)

        # 4. Situation Location
        if current_session["stage"] == "situation_location_init":
            # Situation Location Init
            situation_location_init(current_session)
        
        if current_session["stage"] == "situation_location":
            # Situation Location
            situation_location(current_session)

        # 5. Final message
        break

@socketio.on('connect', namespace='/whatsapp_bot')
def on_connect():
    client_id = request.sid
    print(f'new connection,id: {client_id}')

@whatsapp_bot.route('/')
def index():
    return render_template('whatsapp_bot/index.html')

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
        print("Other type message")
    
    return 'OK', 200
    # except Exception as e:
    #     print(f"Failed: {e}", e)
    #     return 'FAILED', 200
    


