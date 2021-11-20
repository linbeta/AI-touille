'''
用戶傳文字訊息
TextMessage ==>用戶傳來的
TexSendtMessage ==>我們傳給用戶的
'''

from models.user import User
from flask import Request
from linebot import (
    LineBotApi
)

import os
from daos.user_dao import UserDAO
from linebot.models import (
    TextSendMessage
)

from linebot.models.events import (
    FollowEvent
)

import services.image_service

class TextService:
    line_bot_api = LineBotApi(
        channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

    @classmethod
    def line_user_send_text_message(cls, event):

        # TODO：串接資料庫
        Ingredients = ("珍珠奶茶,雞排")  #必須tuple 不能list
        user_message = event.message.text
        tag_link = ("https://icook.tw/recipes/397498")

        if user_message in Ingredients:
            cls.line_bot_api.reply_message(
                event.reply_token,
                # TextSendMessage(services.image_service.result_tag)
                TextSendMessage(text=tag_link)
            )
            print(event.message.text)
        else:
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="訊息無法辨識，請輸入食材名稱或上傳食材圖片")
            )