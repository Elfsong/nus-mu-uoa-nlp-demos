# coding: utf-8
import re
import json
from collections import defaultdict
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, CarouselTemplate, CarouselColumn, PostbackAction, MessageAction, TextSendMessage, TemplateSendMessage

from flask import Blueprint, render_template, request, abort

# Flask handler
line_bot = Blueprint('line_bot', __name__, template_folder='./templates', static_folder='./static')

# Line config & Line Messaging API handler
with open("./app/line_bot/static/password", "r") as password_f:
    lines = list(password_f.readlines())
    CHANNEL_ACCESS_TOKEN = lines[0].strip().split("\t")[1]
    CHANNEL_SECRET = lines[1].strip().split("\t")[1]
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Line session manager
# TODO(mingzhe): fancy one -> class
session_manager = defaultdict(list)

topic_manager = defaultdict(str)

# Get artquest model
print("Requiring artquest_model...")
from .. artquest import artquest_model
print("Got artquest_model!")

# Line context
# TODO(mingzhe): Carousel
context_manager = {
    "BBP": """Phuket's Big Buddha is one of the most important and revered landmarks on the island. The huge image sits on top of the Nakkerd Hills between Chalong and Kata and, at 45 metres tall, can be seen from as far away as Phuket Town and Karon Beach. The lofty site offers the best 360-degree views of the island, with sweeping vistas of Phuket Town, Kata, Karon, Chalong Bay and more. Reachable via a winding, 6-km road leading from Phuket's main roads, it's a must-visit island destination.""",
    "CT": """Wat Chalong, or Chalong Temple, built at the beginning on 19th century, Its real name is Wat Chaiyathararam, but you probably won't see it on any road signs. Wat Chalong ( Chalong Temple ) is the largest of Phuket's temples, and the most visited. The most recent building on the grounds of Wat Chalong is a 60 meters tall 'Chedi' sheltering a splinter of bone from Buddha. Walls and ceilings are decorated with beautiful painting illustrating the life of Buddha, as well as many donated golden statues. Wat Chalong Chedi is built on three floors so feel free to climb all the way to the top floor terrace to get a nice bird view on the entire temple grounds. Few more steps will lead you to a glass display where the fragment of bone can be contemplated.""",
    "KB": """Karon Beach in Phuket is one of the longest beaches on the island, spanning 5 km of fine white sand overlooking the Andaman Sea. The northern end of the beach is usually deserted, making it an excellent spot for those who want the beach to themselves. The southern end, close to Kata, tends to be busier but it isn't that hard to find a nice spot for yourself."""
}

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
                                text='I am interested in Big Buddha Phuket!'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://nlp-platform.online/line_bot/static/images/CT.jpeg',
                        title='Chaithararam Temple',
                        text="""The largest of Phuket's temples.""",
                        actions=[
                            MessageAction(
                                label='Explore',
                                text='I am interested in Chaithararam Temple!'
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://nlp-platform.online/line_bot/static/images/KB.jpeg',
                        title='Karon Beach',
                        text='The longest beaches on the island.',
                        actions=[
                            MessageAction(
                                label='Explore',
                                text='I am interested in Karon Beach!'
                            )
                        ]
                    )
                ]
            )
        )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)
    elif message.startswith("I am interested in"):
        topic = re.match("^I am interested in (.*)!$", message).groups(0)[0]
        topic_manager[user_id] = topic
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Ask me anything about {topic}!"))
    else:
        session_manager[user_id] += [message]
        context = topic_manager[user_id]
        response = artquest_model.question_generation(context, session_manager[user_id][-6:])
        session_manager[user_id] += [response]

        # length control
        if len(session_manager[user_id]) > 100:
            session_manager[user_id] = session_manager[user_id][-50:]

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

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