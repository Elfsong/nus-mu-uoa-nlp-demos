# coding: utf-8

# Author: Du Mingzhe (mingzhe@nus.edu.sg)
# Date: 2022-10-02

import os
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
genre_model = GenreModel()

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

os.environ["TOKENIZERS_PARALLELISM"] = "false"

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

                    1. With the router powered off, connect the power cord to your router, and plug the power cord into your power source.
                    2. Press and hold the Reset button for 10 seconds while you power on the route
                    3. Check the lights on the router — the lights should be solid color or blink in repeating patterns.
                    4. Power off your router.
                    5. At this point, your router is reset and in its factory-default configuration.

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
    },
    "Mingzhe Du": {
        "action": "Done",
        "topics": {
            "Mingzhe Du": {
                "article": """
                    Mingzhe Du is the Creator.
                """
            },
        }
    },
    "IDS": {
        "action": "Done",
        "topics": {
            "Boss/Director": {
                "article": """
                    WWynne Hsu, See-Kiong Ng, and Lee Mong Li, Janice are directors of IDS.
                """
            },
            "location": {
                "article": """
                    IDS is located at Innovation 4.0, NUS.
                """
            }
        }
    }

}

def update_log(message: str, mode="info"):
    color = "alert-success"
    is_dialog = mode in ["user", "agent"]

    if mode == "user":
        color = "alert-primary"

    elif mode == "agent":
        color = "alert-success"

    elif mode == "info":
        color = "alert-info"

    elif mode == "warn":
        color = "alert-warning"

    elif mode == "error":
        color = "alert-danger"

    emit('update_log', {"log": message, "color": color, "is_dialog": is_dialog, "mode": mode}, broadcast=True, namespace="/whatsapp_bot")

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

    update_log(msg, mode="agent")

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

    conversation = ""
    for dialogue in history:
        conversation += f"{dialogue[0]}: {dialogue[1]}\n"
    return conversation

def restart_session(from_id, to_id):
    user_session[to_id] = dict()
    send_msg(from_id, to_id, "Session Restarted!")
    update_log(f"Session {to_id} restarted.", mode="error")

def pipeline(data):
    # Meta info
    from_id = data["metadata"]["phone_number_id"]
    to_id = data['messages'][0]["from"]
    message = data['messages'][0]["text"]["body"]
    message_id = data['messages'][0]['id']

    while True:
        # Restart
        if message.startswith("Restart"):
            restart_session(from_id, to_id)
            break
                
        # Meta info
        current_session = user_session[to_id]
        if "stage" not in current_session:
            current_session["stage"] = "small_talk"
            current_session["from_id"] = from_id
            current_session["to_id"] = to_id
            current_session["history"] = list()
            current_session["context"] = [
                """Given the context, generate a friendly repsonse to the customer.""",
                """My name is AsiA. I am a very friendly Cisco tech support team crew.\nI will try my best to help our customers solve their problems.\nIf I cannot solve the problem, suggest the customer call Cisco Tech Hotline 800 616 1356."""
            ]
            current_session["status"] = "normal"
            update_log(f"New session from {from_id} to {to_id}", mode="info")
            
        message = (message + ".") if not message.endswith((".", "?", "!")) else message
        current_session["history"] += [("Customer", message)]
        update_log(message, mode="user")

        # Initial Message Analysis
        genre_result = genre_model.generate([message])
        update_log(f"Initial Information Extraction: {genre_result}", mode="warn")

        # Manually context Update Request (without recording)
        if message.startswith("Can you help me to read this document?"):
            current_session["status"] = "update_context"
            send_msg(from_id, to_id, "Absolutely! Please sharing the document with me.")
            update_log(f"Waiting for the data callback...", mode="error")
            break

        # Manually Context Update
        if current_session["status"] == "update_context":
            current_session["context"] += [message.strip()]
            current_session["status"] = "normal"
            
            response = "Please give me one moment to pull up the instructions."
            send_msg(from_id, to_id, response)
            current_session["history"] += [("AsiA", response)]

            #TODO(mingzhe): document analysis
            update_log(f"Document analysing...", mode="info")

            # update_log(f"Document analysing finished.", mode="info")
            response = "Got it! What is your question?"
            send_msg(from_id, to_id, response)
            current_session["history"] += [("AsiA", response)]
            
            break

        # Context Update
        context_message = message
        product_name, product_score = similarity_model.product_search(list(product_dict.keys()), context_message)
        update_log(f"[Embedding search] Matching input with database...", mode="info")
        update_log(f"Category [{product_name}] -> [{product_score}]", mode="warn")
        if (product_score > 0.5) and ("topics" in product_dict[product_name]):
            topics = product_dict[product_name]["topics"]
            topic_name, topic_score = similarity_model.product_search(list(topics.keys()), context_message)
            update_log(f"Category [{product_name}] -> [{topic_name}] -> [{topic_score}]", mode="warn")
            if topic_score > 0.5:
                current_session["context"] += [topics[topic_name]["article"]]
                update_log(f"Hit category [{product_name}] -> [{topic_name}], loading knowledge into context...", mode="warn")

        # Generate response
        response = openai_model.generate_response(current_session["context"][-4:], current_session["history"][-5:])
        current_session["history"] += [("AsiA", response)]
        send_msg(from_id, to_id, response)

        break

@socketio.on('connect', namespace='/whatsapp_bot')
def on_connect():
    client_id = request.sid
    update_log(f"Found new connection: {client_id}", mode="info")

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
    # update_log(f"Raw data: {response}", mode="warn")

    try:
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
    except Exception as e:
        print(f"Failed: {e}", e)
        return 'FAILED', 200
    


