'''

用戶上傳照片時，將照片從Line取回，放入CloudStorage

瀏覽用戶目前擁有多少張照片（未）

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
from google.cloud import speech_v1p1beta1 as speech

speech_client = speech.SpeechClient()


class AudioService:
    line_bot_api = LineBotApi(channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

    '''
    用戶上傳照片
    將照片取回
    將照片存入CloudStorage內
    '''

    @classmethod
    def line_user_upload_video(cls, event):

        # 取出照片
        image_blob = cls.line_bot_api.get_message_content(event.message.id)
        temp_file_path = f"""{event.message.id}.mp3"""

        #
        with open(temp_file_path, 'wb') as fd:
            for chunk in image_blob.iter_content():
                fd.write(chunk)

        # 上傳至bucket
        storage_client = storage.Client()
        bucket_name = os.environ['USER_INFO_TEMP_BUCKET_NAME']
        destination_blob_name = f'{event.source.user_id}/audio/{event.message.id}.mp3'
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

        # 回覆消息
        cls.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(reply_transcript)
        )
