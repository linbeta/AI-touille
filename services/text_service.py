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

from utils.search_recipe import use_result_tag_to_query, multiple_ingredient_search

class TextService:
    line_bot_api = LineBotApi(
        channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

    @classmethod
    def line_user_send_text_message(cls, event):
        '''
        載入類別列表，訓練模型的labels.txt檔案使用中文需要設定編碼為"utf-8"
        '''
        # TODO：串接資料庫
        if event.message.text == "都不是喔！":
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage("那請問這是什麼？XD")
            )
        else:
            user_message = event.message.text
            ingredients = cls.get_ingredients(user_message)
            if len(ingredients) == 0:
                # TODO: 如果user傳來的文字訊息不包含可辨識的食材，回覆user一句話
                reply_message = cls.get_intent(user_message)
                cls.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(reply_message)
                )
            else:
                # 串接資料庫->複數食材搜尋
                # print(ingredients)
                dishes = multiple_ingredient_search(ingredients, len(ingredients))
                # print(dishes)
                cls.line_bot_api.reply_message(
                    event.reply_token,
                    dishes
                )

    @classmethod
    def get_ingredients(cls, text):
        # 拿labels.txt來做食材的class_list
        class_list = []
        with open('converted_savedmodel/labels.txt', encoding="utf-8") as f:
            for line in f:
                (key, val) = line.split()
                class_list.append(val)
        result = []

        for item in class_list:
            if item in text and (item not in result):
                if "洋蔥" in result:
                    pass
                else:
                    result.append(item)
            elif item in ["豬肉片", "豬五花", "豬絞肉"] and ("豬" in text) and ("豬肉" not in result):
                result.append("豬肉")
        return result

    # 用這個方法來判斷user傳訊息的意圖
    @classmethod
    def get_intent(cls, text):
        result = ""
        say_hi = [
            "哈囉", "你好", "hello", "hi", "Hi", "hihi", "嗨"
        ]
        how_to_use = [
            "不會用", "使用說明", "操作說明", "說明書", "要怎麼用", "教我用", "這是要怎麼用", "你可以幹什麼", "這是要幹嘛", "怎麼用"
        ]
        unknown = [
            "我哪知道", "蛤?", "不知道", "誰知道", "不懂", "..."
        ]
        be_nice = [
            "好喔", "好的", "了解", "XD", "是喔"
        ]
        intent = ""
        for word in say_hi:
            if word in text:
                intent = "say_hi"

        for word in unknown:
            if word in text:
                intent = "I_don't_know"

        for word in be_nice:
            if word in text:
                intent = "be_nice"

        for word in how_to_use:
            if word in text:
                intent = "how_to_use"

        # 依照幾個基本的intent來產稱回覆user的句子
        if intent == "say_hi":
            result = "你好，你可以傳食材照片或是用打字的告訴我你家冰箱裡面有些什麼食材，開啟麥克風傳語音訊息給我也可以喔！"
        elif intent == "I_don't_know":
            result = "好喔！XD"
        elif intent == "be_nice":
            result = "試試看吧！:D"
        elif intent == "how_to_use":
            result = "你可以傳食材照片或是用打字的告訴我你家冰箱裡面有些什麼食材，我會推薦適合的食譜給你，開啟麥克風傳語音訊息也可以喔！"
        else:
            result = "阿哈！我聽不懂喔~ 更多功能開發中，敬請期待未來的AI服務"

        return result



