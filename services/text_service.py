'''
用戶傳文字訊息
TextMessage ==>用戶傳來的
TexSendtMessage ==>我們傳給用戶的
'''


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

    @classmethod
    def line_user_send_text_message(cls, event):
        '''
        載入類別列表，訓練模型的labels.txt檔案使用中文需要設定編碼為"utf-8"
        '''
        user_message = event.message.text
        if user_message == "都不是喔！":
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage("我還認不得這樣的照片🤯，請給我四種食材以內的照片，或使用語音搜尋試試看😉")
            )
        # TODO: 施工區：elif裡面先用文字來顯示收藏的食譜,用user_id來搜尋
        elif user_message == "收藏的食譜":
            user_id = event.source.user_id
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(f"我收藏的食譜: https://ai-touille-6qzlayuaza-de.a.run.app/my_cookbook/{user_id}")
                # TextSendMessage(f"我收藏的食譜: https://8a57-180-218-204-111.ngrok.io/my_cookbook/{user_id}")
            )
        # TODO: 施工區:處理官網留言
        elif user_message[:3] == "###":
            print("this is a message form")
            msg = cls.manageForm(user_message)
            cls.line_bot_api.reply_message(
                event.reply_token,
                msg
            )
        else:
            ingredients = cls.get_ingredients(user_message)
            if len(ingredients) == 0:
                # TODO: 如果user傳來的文字訊息不包含可辨識的食材，回覆user一句話
                reply_message = cls.get_intent(user_message)
                cls.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(reply_message)
                )
            elif ingredients == ['這不是食材']:
                cls.line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage("請傳有食材的照片，或試試看文字、語音搜尋食譜")
                )
            else:
                # 串接資料庫->複數食材搜尋
                dishes = multiple_ingredient_search(ingredients, len(ingredients), event.source.user_id)
                new_template = cls.make_template(dishes)
                cls.line_bot_api.reply_message(
                    event.reply_token,
                    new_template
                )

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
            "不會用", "使用說明", "操作說明", "說明書", "要怎麼用", "教我用", "這是要怎麼用", "你可以幹什麼", "這是要幹嘛", "怎麼用",
            "沒有食材"
        ]
        unknown = [
            "我哪知道", "蛤?", "不知道", "誰知道", "不懂", "...", "這不是食材"
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

    @classmethod
    def make_template(cls, dishes):
        # print("dishes: " + str(dishes))
        # 2021/12/21 Charles
        for i in dishes:
            if i[4] == "Y":
                i[4] = "取消收藏"
                # i[1]="刪除最愛: "+str(i[1])
                i[0] = "D," + str(i[0])
            else:
                i[4] = "收藏食譜"
                # i[1] = "新增最愛: " + str(i[1])
                i[0] = "I," + str(i[0])

        cs = []
        # print(len(dishes))
        for j in range(len(dishes[:9])):
            cc = CarouselColumn(
                thumbnail_image_url=dishes[j][3],
                title=dishes[j][1],
                text=' ',
                actions=[
                    URITemplateAction(
                        label='食譜連結點我',
                        uri=dishes[j][2]
                    ),
                    PostbackAction(
                        label=dishes[j][4],
                        display_text=dishes[j][1],
                        data=dishes[j][0]
                    )
                ]
            )
            cs.append(cc)
        # print(cs)
        # print(str(cs))
        TipCard = CarouselColumn(
            thumbnail_image_url='https://github.com/linbeta/AI-touille/blob/main/pic/tips.jpg?raw=true',
            title='搜尋結果怪怪的？',
            text=cls.get_tip(),
            actions=[
                URITemplateAction(
                    label='沒有我要的食譜',
                    uri='https://icook.tw/'  # TODO 這邊先放icook的連結
                ),
                MessageTemplateAction(
                    label='給建議',
                    text='我要留言'
                )
            ]
        )
        cs.append(TipCard)
        # print("Finished CS")
        # 確認是否每個食材都會有>4的食譜 -> 若無, 用for迴圈把dish的變數寫入
        try:
            recipe_template_message = TemplateSendMessage(
                alt_text='Carousel template',
                template=CarouselTemplate(
                    columns=cs
                )
            )
        except Exception as e:
            print(e)

        return recipe_template_message

    @classmethod
    def get_tip(cls):
        tips = [
            "想一次搜尋多樣食材組合嗎？試試看開啟麥克風用講的吧！",
            "拍照或上傳照片時，食材種類在4種以內辨識效果會較好喔！",
            "語音和照片搜尋不到時，直接打字試試看吧！",
            "請試試語音輸入整句話：我有紅蘿蔔、番茄和馬鈴薯",
            "想看更多食譜嗎？試試看換個食材名稱或是換句話說:D"
        ]
        random.shuffle(tips)
        return tips[0]

    @classmethod
    def manageForm(cls, mtext):
        try:
            flist = mtext[3:].split('/')
            text1 = '姓名：' + flist[0] + '\n'
            text1 += '建議：' + flist[1]
            message = TextSendMessage(
                text=text1
            )
            return message
        except:
            return "發生錯誤！"
