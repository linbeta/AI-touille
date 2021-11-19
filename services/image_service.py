'''
用戶上傳照片時，將照片從Line取回，放入CloudStorage
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


# 圖片下載與上傳專用
import urllib.request
from google.cloud import storage

# 圖像辨識
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import time

import os

from utils.reply_send_message import detect_json_array_to_new_message_array, turn_recipe_list_to_array
from utils.search_recipe import use_result_tag_to_query

model = tensorflow.keras.models.load_model(
    'converted_savedmodel/model.savedmodel')


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

        # 上傳至照片暫存檔bucket: temp_food_image_mvp，這部分可以成功運作
        storage_client = storage.Client()
        bucket_name = os.environ['USER_INFO_TEMP_BUCKET_NAME']
        destination_blob_name = f'{event.source.user_id}/image/{event.message.id}.png'
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(temp_file_path)

        # 載入模型Label
        '''
        載入類別列表，訓練模型的labels.txt檔案使用中文需要設定編碼為"utf-8"
        '''
        class_dict = {}
        with open('converted_savedmodel/labels.txt', encoding="utf-8") as f:
            for line in f:
                (key, val) = line.split()
                class_dict[int(key)] = val

        # 載入模型
        # Disable scientific notation for clarity
        np.set_printoptions(suppress=True)

        # Load the model
        # model = tensorflow.keras.models.load_model('converted_savedmodel/model.savedmodel')

        # 圖片預測，設定一個result_tag變數來存辨識結果
        result_tag = ""
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        image = Image.open(temp_file_path)
        size = (224, 224)
        image = ImageOps.fit(image, size, Image.ANTIALIAS)
        image_array = np.asarray(image)
        # Normalize the image
        normalized_image_array = (image_array.astype(np.float32) / 127.0 - 1)

        # Load the image into the array
        data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
        data[0] = normalized_image_array[0:224, 0:224, 0:3]

        # run the inference
        prediction = model.predict(data)
        # print(prediction)
        # 取得預測值
        max_probability_item_index = np.argmax(prediction[0])
        # print(max_probability_item_index)
        # 將預測值拿去尋找line_message
        # 並依照該line_message，進行消息回覆，result_message_array是回傳給user的文字訊息(來自json檔)
        # print(prediction.max())
        if prediction.max() > 0.6:
            # TODO: 3. 用選單讓讓user選他拍的是什麼東西，存到update_tag

            result_message_array = detect_json_array_to_new_message_array(
                "line_message_json/"+class_dict.get(max_probability_item_index)+".json")
            result_tag = class_dict.get(max_probability_item_index)
            print(result_tag)
            # 用result_tag來去搜尋食譜資料庫
            push_recipe = use_result_tag_to_query(result_tag)
            # 搜尋資料庫得到食譜連結，並把它轉成可以回傳給user的文字訊息格式存成push_recipe
            # print(push_recipe)

            # 把拿到的食譜資訊append到result_message_array
            result_message_array.append(push_recipe)
            # print(result_message_array)
            # 把食譜網址回傳給user
            cls.line_bot_api.reply_message(
                event.reply_token,
                result_message_array
            )

        else:
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(f"""照片目前無法辨認，已上傳雲端資料庫，敬請期待未來的AI服務！""")
            )
            # TODO: 寫一個機制讓user告訴我們她傳的照片是什麼
            result_tag = "無法辨認"


        # 存照片到訓練資料收集的Bucket裡面：food-image-mvp

        storage_client = storage.Client()
        bucket_name = os.environ['FOOD_IMAGE_BUCKET_NAME']
        # 目的地不分使用者，直接存在一起
        destination_blob_name = f'image_uploaded/{result_tag}_{event.message.id}.png'
        # 存訓練照片的桶子裡面，也依照user id來開資料夾
        # destination_blob_name = f'{event.source.user_id}/image/{result_tag}_{event.message.id}.png'
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(temp_file_path)
        # print(destination_blob_name)

        # 移除本地檔案
        os.remove(temp_file_path)

        # 回覆消息
        # cls.line_bot_api.reply_message(
        #     event.reply_token,
        #     TextSendMessage(f"""圖片已上傳，請期待未來的AI服務！""")
        # )
