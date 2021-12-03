'''
用戶上傳音訊檔時，將音訊檔從Line取回，轉成文字訊息，
並將音訊檔放入CloudStorage
'''

from models.user import User
from flask import Request
from linebot import (
    LineBotApi
)

import os
from daos.user_dao import UserDAO
from linebot.models import (
    TextSendMessage, TextMessage
)

# 拿user資料
from services.user_service import UserService
# 搜尋食譜
from utils.search_recipe import use_result_tag_to_query, multiple_ingredient_search

# 檔案下載與上傳專用
import urllib.request
from google.cloud import storage
# 聲音轉文字的套件GCP提供的API
from google.cloud import speech_v1p1beta1 as speech

speech_client = speech.SpeechClient()


class AudioService:
    line_bot_api = LineBotApi(channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

    '''
    用戶上傳音訊檔
    將音訊檔取回
    將檔案存入CloudStorage內
    '''

    @classmethod
    def line_user_upload_video(cls, event):

        # 取出音檔
        image_blob = cls.line_bot_api.get_message_content(event.message.id)
        temp_file_path = f"""{event.message.id}.mp3"""


        with open(temp_file_path, 'wb') as fd:
            for chunk in image_blob.iter_content():
                fd.write(chunk)

        user_object = UserService.get_user(event.source.user_id)
        user_nickname = user_object.line_user_nickname

        # 上傳至bucket
        storage_client = storage.Client()
        bucket_name = os.environ['USER_INFO_TEMP_BUCKET_NAME']
        destination_blob_name = f'{user_nickname}/audio/{event.message.id}.mp3'
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(temp_file_path)

        # ----------------------------- 2021.11.24_使用GCP speech-to-text音檔 ---------------------------

        # 從雲端取值的作法
        gcs_uri = 'gs://' + bucket_name + '/' + destination_blob_name
        audio = speech.RecognitionAudio(uri=gcs_uri)

        # 直接在當前資料夾取值的做法
        # with open(temp_file_path, 'rb') as audio_file:
        #     content = audio_file.read()
        # audio = speech.RecognitionAudio(content=content)

        config = speech.RecognitionConfig(
            {
                "encoding": speech.RecognitionConfig.AudioEncoding.MP3,  # 這邊卡關超久, 官方文件這邊有說明MP3檔要使用v1p1beta版本才行
                "sample_rate_hertz": 16000,
                "language_code": "zh-TW"
            }
        )
        response = speech_client.recognize(config=config, audio=audio)
        for result in response.results:
            # print(result.alternatives[0].transcript)
            reply_transcript = result.alternatives[0].transcript

        # ----------------------------- 2021.11.24_使用GCP speech-to-text音檔 測試結束---------------------------
        # 取得語音轉文字之後~~看要做什麼功能?????????????
        # 注意喔~~這個每個月超過60分鐘就會開始計費~~~~

        # 移除本地檔案
        os.remove(temp_file_path)

        # option:1 ----- 將reply_transcript截取出食材，把每一個食材分別進資料庫做搜尋 ------ #

        # test_voice_input = "我有雞肉白蘿蔔香菇玉米洋蔥，可以煮什麼？"
        # utils.text_parsing裡面的方法，將一句話裡面有的食材切出來回傳一個list

        # 引用utils/text_parsing.py裡面的方法來把食材切出來
        ingredients_from_audio = get_ingredients(reply_transcript)

        reply_msg = [TextSendMessage(f"語音輸入： {reply_transcript}")]

        if len(ingredients_from_audio) == 0:
            # TODO: 如果user傳來的文字訊息不包含可辨識的食材，回覆user一句話
            reply_message = get_intent(reply_transcript)
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(reply_message)
            )
        else:
            # TODO: 串接資料庫->複數食材搜尋
            dishes = multiple_ingredient_search(ingredients_from_audio, len(ingredients_from_audio))
            reply_msg += dishes
            # 回覆訊息給使用者
            cls.line_bot_api.reply_message(
                event.reply_token,
                reply_msg
            )


        # option:2 ----- 將reply_transcript截取出食材，進資料庫做複數食材搜尋 ------ #

