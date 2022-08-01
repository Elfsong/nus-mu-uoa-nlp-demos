# coding: utf-8

import re
import os
import openai
from collections import defaultdict
from flask import Blueprint, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, CarouselTemplate, CarouselColumn, PostbackAction, MessageAction, TextSendMessage, TemplateSendMessage

# Flask handler
line_bot = Blueprint('line_bot', __name__, template_folder='./templates', static_folder='./static')

# Line config & Line Messaging API handler
with open("./app/line_bot/static/password", "r") as password_f:
    lines = list(password_f.readlines())
    CHANNEL_ACCESS_TOKEN = lines[0].strip().split("\t")[1]
    CHANNEL_SECRET = lines[1].strip().split("\t")[1]
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Line managers
# TODO(mingzhe): class them
session_manager = defaultdict(list)
topic_manager = defaultdict(str)
customize_context_manager = defaultdict(str)
context_manager = {
    "Big Buddha Phuket":  """I am a Phuket tour guide. I know that Phuket Big Buddha, or The Great Buddha of Phuket, is a seated Maravija Buddha statue in Phuket, Thailand. The official name is Phra Phutta Ming Mongkol Eknakiri, shortened to Ming Mongkol Buddha. Sitting atop Nakkerd Hill (also spelt Nagakerd) near Chalong, construction began in 2004. It is the third-tallest statue in Thailand behind only the Great Buddha of Thailand and Luangpho Yai. The Buddha statue depicts Gautama in a sitting position and is 45 metres tall and 25.45 metres wide. It is made of concrete and covered with Burmese white marble. Facing towards Ao Chalong Bay the statue is the main Buddha of the Wat Kitthi Sankaram temple (Wat Kata). The statue was declared the \"Buddhist Treasure of Phuket\" by Somdet Phra Yanasangwon, the Supreme Patriarch of Thailand, in 2008. The statue cost 30 million Baht, sourced primarily from donations.""",
    "Chaithararam Temple":   """Wat Chalong, or Chalong Temple, built at the beginning on 19th century, Its real name is Wat Chaiyathararam, but you probably won't see it on any road signs. Wat Chalong ( Chalong Temple ) is the largest of Phuket's temples, and the most visited. The most recent building on the grounds of Wat Chalong is a 60 meters tall 'Chedi' sheltering a splinter of bone from Buddha. Walls and ceilings are decorated with beautiful painting illustrating the life of Buddha, as well as many donated golden statues. Wat Chalong Chedi is built on three floors so feel free to climb all the way to the top floor terrace to get a nice bird view on the entire temple grounds. Few more steps will lead you to a glass display where the fragment of bone can be contemplated.""",
    "IDS":   """I am a IDS PhD student. The Institute of Data Science (IDS) is the focal point for all data science research, education, and related activities at National University of Singapore (NUS).  Established in May 2016, IDS coordinates and supports data science research initiatives across NUS.  IDS taps into NUS’ transdisciplinary strengths in being a comprehensive university, with its own business school, medical school, affiliated acute tertiary hospital, engineering faculty, arts and social science faculty, etc. This is a massive advantage above many of the existing institutes in the world. The institute seeks to address challenging impactful real-world problems relevant to Singapore and Asia that are not present/less common in these Western world. By collaborating with public agencies and industry partners such as Grab, SingHealth, Cisco, DSTA and EZ Link, IDS aims to push the boundary of data science through transdisciplinary upstream research, and translate into real-life applications that harness the richness of data for our smart nation. For more information on IDS, please visit http://ids.nus.edu.sg/""",
    "iPhone": """The iPhone is a line of smartphones designed and marketed by Apple Inc. These devices use Apple's iOS mobile operating system. The first-generation iPhone was announced by then-Apple CEO Steve Jobs on January 9, 2007. Since then, Apple has annually released new iPhone models and iOS updates. As of November 1, 2018, more than 2.2 billion iPhones had been sold. The iPhone has a user interface built around a multi-touch screen. It connects to cellular networks or Wi-Fi, and can make calls, browse the web, take pictures, play music and send and receive emails and text messages. Since the iPhone's launch further features have been added, including larger screen sizes, shooting video, waterproofing, the ability to install third-party mobile apps through an app store, and many accessibility features. Up to iPhone 8 and 8 Plus, iPhones used a layout with a single button on the front panel that returns the user to the home screen. Since iPhone X, iPhone models have switched to a nearly bezel-less front screen design with app switching activated by gesture recognition. The older layout today is still used for Apple's currently-produced iPhone SE series. The iPhone is one of the two largest smartphone platforms in the world alongside Android, forming a large part of the luxury market. The iPhone has generated large profits for Apple, making it one of the world's most valuable publicly traded companies. """
}

# OpenAI handler
openai.api_key = os.getenv("OPENAI_API_KEY")

def openai_generate(context, session):
    try:
        # Generate Input
        session_text = "\n".join(session)
        input_text = f"{context}\n\n{session_text}\nElf:"

        response = openai.Completion.create(model="text-davinci-002", prompt=input_text, temperature=0.6, max_tokens=188)
        # print("=" * 80)
        # print(input_text)
        # print("original output:", response)

        # Parse Response
        answer = "Sorry, I don't know how to response. Try to rephrase??"
        if response.choices[0].finish_reason == "length":
            answer = ".".join(response.choices[0].text.split(".")[:-2]) + "."
        else:
            answer = response.choices[0].text.replace("\n", "")
            
        answer = answer.strip()

        return answer
    except Exception:
        return "Sorry, I have a problem. Call Mingzhe to fix me."

# MessageEvent handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message = event.message.text.strip()

    if message == "Hello":
        carousel_template_message = TemplateSendMessage(
            alt_text='Carousel, Watch it on your phone.',
            template=CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnail_image_url='https://nlp-platform.online/line_bot/static/images/BBP.jpeg',
                        title='Big Buddha Phuket',
                        text="""The most revered landmarks on the island.""",
                        actions=[
                            MessageAction(
                                label='Explore',
                                text='[Topic Selected] Big Buddha Phuket'
                            ),
                            MessageAction(
                                label='Context',
                                text='[Context] ' + f"https://nlp-platform.online/line_bot/context?uid={user_id}&topic=Big%20Buddha%20Phuket"
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://nlp-platform.online/line_bot/static/images/IPHONE.jpeg',
                        title='iPhone',
                        text="""Think Different""",
                        actions=[
                            MessageAction(
                                label='Explore',
                                text='[Topic Selected] iPhone'
                            ),
                            MessageAction(
                                label='Context',
                                text='[Context] ' + f"https://nlp-platform.online/line_bot/context?uid={user_id}&topic=iPhone"
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://nlp-platform.online/line_bot/static/images/IDS.jpeg',
                        title='NUS IDS',
                        text='Institute of Data Science',
                        actions=[
                            MessageAction(
                                label='Explore',
                                text='[Topic Selected] IDS'
                            ),
                            MessageAction(
                                label='Context',
                                text='[Context] ' + f"https://nlp-platform.online/line_bot/context?uid={user_id}&topic=IDS"
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://nlp-platform.online/line_bot/static/images/FREE.jpeg',
                        title='Custom Input',
                        text='Type anything you want with a prompt [CT]',
                        actions=[
                            MessageAction(
                                label='Explore',
                                text='[Topic Selected] Your Custom Input'
                            ),
                            MessageAction(
                                label='Context',
                                text='[Context] ' + f"https://nlp-platform.online/line_bot/context?uid={user_id}&topic=Your%20Custom%20Input"
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)
    elif message.startswith("[Topic Selected]"):
        topic = re.match("^\[Topic Selected\] (.*)$", message).groups(0)[0].strip()
        topic_manager[user_id] = topic
        session_manager[user_id] = []
        response = f"Ask me anything about {topic}!"

        if topic_manager[user_id] == "Your Custom Input":
            response += "Type anything you want with a prompt [CT]"
            
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
    elif message.startswith("[CT]"):
        ct = re.match("^\[CT\] (.*)$", message).groups(0)[0].strip()
        customize_context_manager[user_id] = ct
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Input recorded!"))
    elif message.startswith("[Context]"):
        pass
    else:
        try:
            message = message.strip()
            message = (message + ".") if not message.endswith((".", "?", "!")) else message

            session_manager[user_id] += [f"Client: {message}"]
            context_topic = topic_manager[user_id]
            context = context_manager[context_topic] if context_topic != "Your Custom Input" else customize_context_manager[user_id]
            response = openai_generate(context, session_manager[user_id])
            session_manager[user_id] += [f"Elf: {response}"]

            # Length control
            session_manager[user_id] = session_manager[user_id][-5:]

            # # Manual Control
            # print(f"Input: {message}")
            # response = input("Answer:")
            
            # Reply message 
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))
        except Exception as e:
            print(e)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="I have a problem (maybe your problem), call mingzhe to fix me."))

@line_bot.route("/context", methods=['GET'])
def context():
    context_str = "None"
    try:
        topic = request.args["topic"]
        user_id = request.args["uid"]
        if topic == "Your Custom Input":
            context_str = customize_context_manager[user_id]
        else:
            context_str = context_manager[topic]
    except:
        print("Context component error.")

    return f"<h3>{context_str}</h3>"


# Callback handler
@line_bot.route('/callback', methods=['POST'])
def callback():
    # Get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # Get request body as text
    body = request.get_data(as_text=True)

    # Handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'