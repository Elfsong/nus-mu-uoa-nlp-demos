from flask import Blueprint, render_template, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

from . model import ArtQuestModel

from collections import defaultdict

# Flask handler
line_bot = Blueprint('line_bot', __name__, template_folder='./templates', static_folder='./static')

# Line config
CHANNEL_ACCESS_TOKEN = """sTnMwh05pEPnDcCghypDdTc+oYzzp3zXMsAuwV2SsxCKTa3Sa3exE30Lo4lyYdgg0ZzYQFgKc+KZ150KNcM+bWtMQ/1FHo1ClinMfcHTlcqb2Q/f+CURK5QCoea+0Sttmk599sw000zsHGqdRzREoAdB04t89/1O/w1cDnyilFU="""
CHANNEL_SECRET = """9858716024d4e091527327fc16153499"""
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Line model
artquest_model = ArtQuestModel("Elfsong/ArtQuest")

# Line session manager
session_manager = defaultdict(list)

# Line context
context = "This is a painting showing Rohani. The painting was made by Georgette Chen. Rohani was a student of Chen's at the Nanyang Academy of Fine Arts (NAFA). She was also a friend beyond the classroom. Here, she is vibrantly clothed in a matching red dress and headscarf. She is also wearing an accessory, a delicate gold pin in the shape of an R. Chen often drove Rohani home after school, as both lived around Siglap."

# Just for testing (useless)
@line_bot.route('/')
def index():
    return render_template('line_bot/index.html')

# MessageEvent handler
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message = event.message.text

    session_manager[user_id] += [message]
    response = artquest_model.question_generation(context, session_manager[user_id])
    session_manager[user_id] += [response]

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