import os
from time import sleep
channel_access_token = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
channel_secret = os.environ["LINE_CHANNEL_SECRET"]

import sys
import os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)

from flask import Flask, request, abort, render_template

from flask_cors import CORS

# 外部連結自動生成套件
from flask_ngrok import run_with_ngrok

from linebot.exceptions import (
    InvalidSignatureError
)

from controllers.line_bot_controller import LineBotController
from services.user_service import UserService
from utils.search_recipe import get_cookbook
from utils.favorites import remove_recipe_from_cookbook
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
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/aitouille-adam.json"

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

'''
網頁
'''

# 用line_user_id來搜尋資料庫裡面儲存的食譜
@app.route('/my_cookbook/<user_id>', methods=['GET', 'POST'])
def open_my_cookbook(user_id):
    user_object = UserService.get_user(user_id)
    user_nickname = user_object.line_user_nickname
    recipe_dict = get_cookbook(user_id)
    # print(recipe_dict)
    if request.method == 'POST':
        try:
            remove_id = request.get_data(as_text=True).split("=")[0]
            # print(remove_id)
            remove_recipe_from_cookbook(user_id, int(remove_id))
            sleep(1.0)
            recipe_dict = get_cookbook(user_id)
            # print(recipe_dict)
        except:
            pass
    return render_template('my_cookbook.html', search_result=recipe_dict, nickname=user_nickname)


'''
轉發功能列表
'''

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['x-line-signature']
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


# @app.route("/user", methods=['GET'])
# def get_user():
#     result = UserController.get_user(request)
#     return result


# =================== LIFF靜態頁面(始) ===================
liffid = os.environ["LIFF_ID"]
@app.route('/form')
def form():
    # data = request.get_data()
    # print(data)
    return render_template('form.html', myliffid=liffid)


# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     mtext = event.message.text
#     if mtext == '@彈性配置':
#         sendFlex(event)
#
#     elif mtext[:3] == '###' and len(mtext) > 3:
#          manageForm(event, mtext)




# =================== LIFF靜態頁面(終) ===================


if __name__ == "__main__":
    # 本地跑ngrok用
    app.run()
    # 上線版用
    # app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
