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
# 搜尋食譜
from utils.search_recipe import use_result_tag_to_query
from utils.text_parsing import get_ingredients

class TextService:
    line_bot_api = LineBotApi(
        channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

    @classmethod
    def line_user_send_text_message(cls, event):
        '''
        載入類別列表，訓練模型的labels.txt檔案使用中文需要設定編碼為"utf-8"
        '''
        # TODO：串接資料庫
        user_message = event.message.text
        # 引用utils/text_parsing.py裡面的方法來把食材切出來
        ingredients = get_ingredients(user_message)
        reply = []
        for item in ingredients:
            dish = use_result_tag_to_query(item)
            reply.append(dish)

        cls.line_bot_api.reply_message(
            event.reply_token,
            reply
        )

# =====================================  以下先保留(參考用)  =============================================

# import services.image_service
#
# class TextService:
#     line_bot_api = LineBotApi(
#         channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
#
#     @classmethod
#     def line_user_send_text_message(cls, event):
#
#         # TODO：串接資料庫
#         Ingredients = ("雞排,珍奶")  #必須tuple 不能list
#         user_message = event.message.text
#         tag_link = ("https://icook.tw/recipes/397498")
#
#         if user_message in Ingredients:
#             cls.line_bot_api.reply_message(
#                 event.reply_token,
#                 # TextSendMessage(services.image_service.result_tag)
#                 TextSendMessage(text=tag_link)
#             )
#             print(event.message.text)
#         else:
#             cls.line_bot_api.reply_message(
#                 event.reply_token,
#                 TextSendMessage(text="訊息無法辨識，請輸入食材名稱或上傳食材圖片")
#             )