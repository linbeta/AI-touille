####安裝套件  pip3 install -r requirements.txt  #######

## ========== 設定line_bot  ==========
import os
channel_access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
channel_secret = os.environ["LINE_CHANNEL_SECRET"]


import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from flask import Flask, request, abort

from flask_cors import CORS


# 外部連結自動生成套件
from flask_ngrok import run_with_ngrok

from linebot.exceptions import (
    InvalidSignatureError
)


from controllers.line_bot_controller import LineBotController

from controllers.user_controller import UserController

app = Flask(__name__)
CORS(app)

from linebot import (
    LineBotApi, WebhookHandler
)
import os

line_bot_api = LineBotApi(
    channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(channel_secret=os.environ["LINE_CHANNEL_SECRET"])
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/ratatouille-ai-e6daa9d44a92.json"


# 載入Follow事件
from linebot.models.events import (
    FollowEvent, UnfollowEvent, MessageEvent, TextMessage, PostbackEvent, ImageMessage, AudioMessage, VideoMessage
)


# 建立日誌紀錄設定檔
# https://googleapis.dev/python/logging/latest/stdlib-usage.html
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler


# 生成liff套件
from flask import Flask
app = Flask(__name__)
from flask import request, abort, render_template
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage



client = google.cloud.logging.Client()

# 建立line event log，用來記錄line event
bot_event_handler = CloudLoggingHandler(client, name="AI-touille_bot_event")
bot_event_logger = logging.getLogger('AI-touille_bot_event')

bot_event_logger.setLevel(logging.INFO)
bot_event_logger.addHandler(bot_event_handler)

app = Flask(__name__)
# 底下兩行本地端跑ngrok時用
app.debug = True
run_with_ngrok(app)


@app.route('/test')
def hello_world():
    bot_event_logger.info("test")
    return 'Hello, World!'


'''
轉發功能列表
'''


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    bot_event_logger.info(body)
    # print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(FollowEvent)
def handle_line_follow(event):
    return LineBotController.follow_event(event)


@handler.add(UnfollowEvent)
def handle_line_unfollow(event):
    return LineBotController.unfollow_event(event)


@handler.add(MessageEvent, TextMessage)
def handle_line_text(event):
    return LineBotController.handle_text_message(event)


@handler.add(MessageEvent, ImageMessage)
def handle_line_image(event):
    return LineBotController.handle_image_message(event)


@handler.add(MessageEvent, VideoMessage)
def handle_line_video(event):
    return LineBotController.handle_video_message(event)


@handler.add(MessageEvent, AudioMessage)
def handle_line_audio(event):
    return LineBotController.handle_audio_message(event)


@handler.add(PostbackEvent)
def handle_postback_event(event):
    return LineBotController.handle_postback_event(event)


@app.route("/user", methods=['GET'])
def get_user():
    result = UserController.get_user(request)
    return result

# ============  LIFF 靜態頁面 (起) ============

@app.route('/form')
def page():
	return render_template('form.html', liffid = liffid)

@handler.add(MessageEvent, message=TextMessage)
def manageForm(event, mtext):
    try:
        flist = mtext[3:].split('/')
        text1 = '姓名：' + flist[0] + '\n'
        text1 += '留言內容：' + flist[1]
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
        LineBotController.handle_user_message(message)
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

    # =================== LIFF靜態頁面(始) ===================

    liffid = os.environ["LIFF_ID"]

    @app.route('/message')
    def form():
        return render_template('form.html', liffid = liffid)

    @handler.add(MessageEvent, message=TextMessage)
    def manageForm(event, mtext):
        try:
            flist = mtext[3:].split('/')
            text1 = '姓名：' + flist[0] + '\n'
            text1 += '留言內容：' + flist[1]
            message = TextSendMessage(
                text = text1
            )
            line_bot_api.reply_message(event.reply_token,message)
        except:
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))

    # =================== LIFF靜態頁面(終) ===================

if __name__ == "__main__":
    # 本地跑ngrok用
    app.run()
    # 上線版用
    # app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))