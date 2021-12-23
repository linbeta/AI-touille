'''
辨識多樣食材的影像辨識模型(DN169_65)
'''

from models.user import User
from flask import Request
from linebot import (
    LineBotApi
)

import os
from daos.user_dao import UserDAO
from linebot.models import (
    TextSendMessage, QuickReply, QuickReplyButton, MessageAction,
)

# 圖片下載與上傳專用
import urllib.request
from google.cloud import storage

# 圖像辨識
from tensorflow.keras.models import load_model
from PIL import Image, ImageOps
from tensorflow.keras.applications.densenet import DenseNet169
from tensorflow.keras.preprocessing import image as im
from tensorflow.keras.applications.densenet import preprocess_input, decode_predictions
import numpy as np
import time

# 拿user資料
from services.text_service import TextService
from services.user_service import UserService

import os
from datetime import datetime

from utils.reply_send_message import detect_json_array_to_new_message_array
from utils.search_recipe import multiple_ingredient_search

'''
載入模型與類別列表，訓練模型的class_labels.txt檔案使用中文需要設定編碼為"utf-8"
'''
# 載入模型
model = load_model('core_model/1222_65_DN169_model.h5')
# 載入模型Label
class_dict = {}
with open('core_model/class_labels.txt', "r", encoding='utf-8') as f:
    for line in f:
        (key, value) = line.split()
        class_dict[key.zfill(2)] = value
# print(class_dict)
# 用70個編號，但因為有刪除部分，故有些數字沒有使用到，依照這個類別表來標示使用到的編號與對應名稱
class_list = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13',
              '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27',
              '28', '29', '30', '31', '32', '33', '34', '36', '40', '41', '43', '44', '45', '46',
              '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60',
              '61', '62', '63', '64', '65', '66', '67', '69', '70']
# 答案編號與中文名的對照表
trans = [class_dict[i] for i in class_list]


class ImageService:
    line_bot_api = LineBotApi(
        channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

    '''
    用戶上傳照片
    將照片取回
    將照片存入CloudStorage內
    '''

    @classmethod
    def line_user_upload_image(cls, event):

        # 取出照片，設定照片存檔名為event.message.id，檔名存在temp_file_path
        image_blob = cls.line_bot_api.get_message_content(event.message.id)
        temp_file_path = f"""{event.message.id}.png"""

        # 開啟照片準備寫入
        with open(temp_file_path, 'wb') as fd:
            for chunk in image_blob.iter_content():
                fd.write(chunk)

        user_object = UserService.get_user(event.source.user_id)
        # print(user_object)
        user_nickname = user_object.line_user_nickname

        # 上傳至照片暫存檔bucket: temp_food_image_mvp
        storage_client = storage.Client()
        bucket_name = os.environ['USER_INFO_TEMP_BUCKET_NAME']
        destination_blob_name = f'{user_nickname}/image/{event.message.id}.png'
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(temp_file_path)


        # Disable scientific notation for clarity
        # np.set_printoptions(suppress=True)

        # 圖片預測，設定一個result_tag變數來存辨識結果
        result_tag = ""

        # 載入圖片
        img = Image.open(temp_file_path)
        img = ImageOps.fit(img, (224, 224))

        # 針對整張圖做預測
        result_1, prediction = cls.predict_origin(img)
        # print("原圖預測： ", result_1)
        # 觀察機率對照表：
        # for p, val in zip(prediction[0], trans):
        #     print(val, "的機率:", round(p, 3))
        # 切成nxn的小圖做預測
        result_2 = cls.predict_dynamic_cut(img)
        # print(result_2)

        # 對話回應：
        message = "我猜78趴有這些食材，請選擇："
        if result_1 == []:
            selection_1 = "沒有食材"
        else:
            selection_1 = ",".join(result_1)
        selection_2 = ",".join(result_2)

        # 如果原圖和切小圖的辨識結果不同，用quick reply btn讓user選擇
        if result_1 != result_2:
            # 製作3個Quick Reply buttons讓使用者選擇 + 1個以上皆非Quick Reply buttons選項
            btn_1 = QuickReplyButton(
                action=MessageAction(label=selection_1, text=selection_1)
            )
            btn_2 = QuickReplyButton(
                action=MessageAction(label=selection_2, text=selection_2)
            )
            btn_4 = QuickReplyButton(
                action=MessageAction(label="以上皆非", text="都不是喔！")
            )
            # textQuickReplyButton = QuickReplyButton(
            #          action=MessageAction(label="按鈕", text="檸檬")
            #      )
            quickReplyList = QuickReply(items=[btn_1, btn_2, btn_4])

            # 回傳給user預測前三強的可能，讓user用按鈕回覆
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=message, quick_reply=quickReplyList)
            )
        elif result_1 == result_2 and result_1 != []:
            # 如果原圖和切小圖後搜尋結果一樣，直接用這個結果去搜尋
            reply_msg = [TextSendMessage(f"圖片辨識： {selection_1}")]
            # 用selection_1來去搜尋食譜資料庫
            recipes = multiple_ingredient_search(result_1, len(result_1), event.source.user_id)
            new_template = TextService.make_template(recipes)
            reply_msg.append(new_template)
            cls.line_bot_api.reply_message(
                event.reply_token,
                reply_msg
            )
        else:
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage("我怎麼看這都不像是可以吃的東西啊...😅\n"
                                "你可以傳食材照片或是用打字的告訴我你有哪些食材，我會推薦適合的食譜給你，開啟麥克風傳語音訊息也可以喔！")
            )


        # 存照片到訓練資料收集的Bucket裡面：food-image-mvp
        storage_client = storage.Client()
        bucket_name = os.environ['FOOD_IMAGE_BUCKET_NAME']
        # TODO: result_tag
        result_tag = "_".join(result_1) + "__切圖後_" + "_".join(result_2)
        # print(result_tag)
        # 寫一個判斷把團隊成員的測試照片分流出來，讓目的地都放真實使用者的照片
        team_member = ["林芝吟 Beta", "Hugo（浩宇）", "。s。t。i。n。", "謝明劭", "Evelyn Lee", "cwl", "黃金ㄤㄤ包", "Charles (洪士恆)"]
        # 存檔資料夾依照日期來分
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        if user_nickname in team_member:
            destination_blob_name = f'team_test_img/{today}/{result_tag}_{event.message.id}.png'
        else:
            destination_blob_name = f'image_uploaded_by_date/{today}/{result_tag}_{event.message.id}.png'

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(temp_file_path)
        # print(destination_blob_name)

        # 移除本地檔案
        os.remove(temp_file_path)

        # 回覆消息

    @classmethod
    def cut_image(cls, image, num=3):
        width, height = image.size
        item_width = int(width / num)
        box_list = []
        # (left, upper, right, lower)
        for i in range(0, num):
            for j in range(0, num):
                # print((i*item_width,j*item_width,(i+1)*item_width,(j+1)*item_width))
                box = (j * item_width, i * item_width, (j + 1) * item_width, (i + 1) * item_width)
                box_list.append(box)

        image_list = [image.crop(box) for box in box_list]
        # print(image_list)

        return image_list

    # 原圖直接跑預測，機率大於0.2才印出
    @classmethod
    def predict_origin(cls, img):
        # print("get image:", img)
        img = ImageOps.fit(img, (224, 224))
        img = im.img_to_array(img)
        img = preprocess_input(img)
        img_np = np.array(img).reshape(1, 224, 224, 3)
        ### 預測 ###
        pre = model.predict(img_np)
        ans = list(np.array(trans)[pre[0] > 0.3])
        return ans, pre

    # 動態切圖
    @classmethod
    def predict_dynamic_cut(cls, img, num=2):
        # 補值讓讓片變成正方形
        img_list = cls.cut_image(img, num)

        answer = []
        for i, img in enumerate(img_list):
            img = ImageOps.fit(img, (224, 224))
            img_np = np.array(img).reshape(1, 224, 224, 3)
            pp_img = preprocess_input(img_np)
            pre = model.predict(pp_img)
            ans = list(np.array(trans)[pre[0] > 0.1])
            # 印出小圖預測結果
            # print(f"小圖{i + 1} 預測結果： {ans}")
            if '這不是食材' in ans:
                ans.remove("這不是食材")
            answer += ans
            # if i == 0:
            #   for p, val in zip(pre[0], trans):
            #     print(val, "的機率:", round(p, 3))
        answer = list(set(answer))
        return answer