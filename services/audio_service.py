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
# 處理文字
from services.text_service import TextService
# 搜尋食譜
from utils.search_recipe import multiple_ingredient_search

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
    def line_user_upload_audio(cls, event):

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

        # 從雲端取值的作法
        gcs_uri = 'gs://' + bucket_name + '/' + destination_blob_name
        audio = speech.RecognitionAudio(uri=gcs_uri)
        reply_transcript = ""
        config = speech.RecognitionConfig(
            {
                "encoding": speech.RecognitionConfig.AudioEncoding.MP3,  # 官方文件這邊有說明MP3檔要使用v1p1beta版本才行
                "sample_rate_hertz": 16000,
                "language_code": "zh-TW"
            }
        )
        response = speech_client.recognize(config=config, audio=audio)
        for result in response.results:
            # print(result.alternatives[0].transcript)
            reply_transcript = result.alternatives[0].transcript

        # 移除本地檔案
        os.remove(temp_file_path)

        # 引用utils/text_parsing.py裡面的方法來把食材切出來
        ingredients_from_audio = TextService.get_ingredients(reply_transcript)
        # print(ingredients_from_audio)
        reply_msg = [TextSendMessage(f"語音輸入： {reply_transcript}")]

        if len(ingredients_from_audio) == 0:
            # 如果user傳來的文字訊息不包含可辨識的食材，回覆user一句話
            reply_message = TextService.get_intent(reply_transcript)
            cls.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(reply_message)
            )
        else:
            # 串接資料庫->複數食材搜尋
            # 2021/12/21 Charles 新增user_id參數
            dishes = multiple_ingredient_search(ingredients_from_audio, len(ingredients_from_audio), event.source.user_id)
            new_template = TextService.make_template(dishes)
            reply_msg.append(new_template)
            cls.line_bot_api.reply_message(
                event.reply_token,
                reply_msg
            )
