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
import random
import jieba
from daos.user_dao import UserDAO
from linebot.models import (
    TextSendMessage, CarouselTemplate, CarouselColumn, URITemplateAction, PostbackAction, TemplateSendMessage,
    MessageTemplateAction
)
# 搜尋食譜

from utils.search_recipe import multiple_ingredient_search


class TextService:
    line_bot_api = LineBotApi(
        channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

    # @classmethod
    # def line_user_send_text_message(cls, event):
    #     '''
    #     載入類別列表，訓練模型的labels.txt檔案使用中文需要設定編碼為"utf-8"
    #     '''
    #     # TODO：串接資料庫
    #     if event.message.text == "都不是喔！":
    #         cls.line_bot_api.reply_message(
    #             event.reply_token,
    #             TextSendMessage("那請問這是什麼？XD")
    #         )
    #     else:
    #         user_message = event.message.text
    #         ingredients = cls.get_ingredients(user_message)
    #         if len(ingredients) == 0:
    #             # TODO: 如果user傳來的文字訊息不包含可辨識的食材，回覆user一句話
    #             reply_message = cls.get_intent(user_message)
    #             cls.line_bot_api.reply_message(
    #                 event.reply_token,
    #                 TextSendMessage(reply_message)
    #             )
    #         else:
    #             # 串接資料庫->複數食材搜尋
    #             # print(ingredients)
    #             dishes = multiple_ingredient_search(ingredients, len(ingredients))
    #             cls.line_bot_api.reply_message(
    #                 event.reply_token,
    #                 dishes
    #             )

    # 用結巴分詞抓出資料庫中有的食材的新方法
    @classmethod
    def get_ingredients(cls, text):
        jieba.load_userdict("text_files/materials.txt")
        sentence_cut = jieba.lcut(text)
        # print("輸入句子分詞: ", sentence_cut)
        # 用result來存輸入文字切出來的可搜尋食材list
        result = []
        materials = []
        with open("text_files/materials.txt", "r", encoding="utf-8") as f:
            for item in f:
                materials.append(item.strip())
            for word in sentence_cut:
                if word in materials:
                    result.append(word)
        # print("食材列表：", result)
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
            "好喔", "好的", "了解", "XD", "是喔", "OK", "Ok", "ok"
        ]
        give_feedback = [
            "我要留言", "欸不是", "搞錯了", "抱怨"
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

        for word in give_feedback:
            if word in text:
                intent = "give_feedback"

        # 依照幾個基本的intent來產稱回覆user的句子
        if intent == "say_hi":
            result = "你好，你可以傳食材照片或是用打字的告訴我你有些什麼食材，開啟麥克風傳語音訊息給我也可以喔！"
        elif intent == "I_don't_know":
            result = "好喔！XD"
        elif intent == "be_nice":
            result = "試試看吧！:D"
        elif intent == "how_to_use":
            result = "你可以傳食材照片或是用打字的告訴我你有哪些食材，我會推薦適合的食譜給你，開啟麥克風傳語音訊息也可以喔！"
        # TODO: 可以針對Give feedback做另外的對話處理
        elif intent == "give_feedback":
            result = "好的，請說 😊"
        else:
            result = "收到~ 更多功能開發中，敬請期待未來的AI服務！"

        return result

# ================== 施工區分隔線 ======================
# TODO:開發中的程式碼=>用卡片的方式呈現食譜，可直接點喜歡收藏食譜，postback功能待研究
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
                dishes = multiple_ingredient_search(ingredients, len(ingredients))
                # print(dishes)
                new_template = cls.make_template(dishes)
                cls.line_bot_api.reply_message(
                    event.reply_token,
                    new_template
                )

    @classmethod
    def make_template(cls, dishes):
        recipe_template_message = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=[
                    # todo 確認是否每個食材都會有>4的食譜 -> 若無, 用for迴圈把dish的變數寫入
                    CarouselColumn(
                        thumbnail_image_url=dishes[0][3],
                        title=dishes[0][1],
                        text=' ',
                        actions=[
                            URITemplateAction(
                                label='食譜連結點我',
                                uri=dishes[0][2]
                            ),
                            PostbackAction(
                                label='喜歡',
                                display_text='我喜歡'+dishes[0][1],
                                data=dishes[0][0]
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=dishes[1][3],
                        title=dishes[1][1],
                        text=' ',
                        actions=[
                            URITemplateAction(
                                label='食譜連結點我',
                                uri=dishes[1][2]
                            ),
                            PostbackAction(
                                label='喜歡',
                                display_text='我喜歡'+dishes[1][1],
                                data=dishes[1][0]
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=dishes[2][3],
                        title=dishes[2][1],
                        text=' ',
                        actions=[
                            URITemplateAction(
                                label='食譜連結點我',
                                uri=dishes[2][2]
                            ),
                            PostbackAction(
                                label='喜歡',
                                display_text='我喜歡'+dishes[2][1],
                                data=dishes[2][0]
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url=dishes[3][3],
                        title=dishes[3][1],
                        text=' ',
                        actions=[
                            URITemplateAction(
                                label='連結點這邊',
                                uri=dishes[3][2]
                            ),
                            PostbackAction(
                                label='喜歡',
                                display_text='我喜歡'+dishes[3][1],
                                data=dishes[3][0]
                            )
                        ]
                    ),
                    CarouselColumn(
                        thumbnail_image_url='https://github.com/linbeta/AI-touille/blob/main/pic/background.jpeg?raw=true',
                        title='小密技',
                        text="想一次搜尋多樣食材組合嗎？試試看開啟麥克風用講的吧！",
                        actions=[
                            URITemplateAction(
                                label='沒有我要的食譜',
                                uri='https://icook.tw/'  #TODO 這邊要修改~看要放哭哭網站圖?
                            ),
                            MessageTemplateAction(
                                label='給建議',
                                text='我要留言'
                            )
                        ]
                    ),
                ]
            )
        )
        return recipe_template_message
