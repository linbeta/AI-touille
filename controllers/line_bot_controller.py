'''
當用戶關注時，必須取用照片，並存放至指定bucket位置，而後生成User物件，存回db
當用戶取消關注時，
    從資料庫提取用戶數據，修改用戶的封鎖狀態後，存回資料庫
'''

from linebot import (
    LineBotApi, WebhookHandler
)
import os

# 載入Follow事件
from linebot.models.events import (
    FollowEvent, UnfollowEvent, PostbackEvent
)

line_bot_api = LineBotApi(channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

from services.image_service import ImageService
from services.user_service import UserService
from services.video_service import VideoService
from services.audio_service import AudioService
from services.text_service import TextService

from google.cloud import bigquery as bq
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "keys/ratatouille-ai-e6daa9d44a92.json"

from urllib.parse import parse_qs

bq_client = bq.Client()

class LineBotController:

    # 將消息交給用戶服務處理
    @classmethod
    def follow_event(cls, event):
        # print(event)
        UserService.line_user_follow(event)

    @classmethod
    def unfollow_event(cls, event):
        UserService.line_user_unfollow(event)

    # 未來可能會判斷用戶快取狀態
    # 現在暫時無
    @classmethod
    def handle_text_message(cls, event):
        TextService.line_user_send_text_message(event)
        return "OK"
        # return None

    # 用戶收到照片時的處理辦法
    @classmethod
    def handle_image_message(cls, event):
        ImageService.line_user_upload_image(event)
        return "OK"

    # 用戶收到影片時的處理辦法
    @classmethod
    def handle_video_message(cls, event):
        VideoService.line_user_upload_video(event)
        return "OK"

    @classmethod
    def handle_audio_message(cls, event):
        AudioService.line_user_upload_video(event)
        return "OK"

    # ================== 施工區分隔線 ======================
    @classmethod
    def handle_postback_event(cls, event):
        user_id = event.source.user_id
        print(event.source)
        get_data = int(event.postback.data) # 這邊的data為dish list中第一個值, 也就是recipe_id

        # TODO 士恆sql語法確認:
        '''判斷邏輯
        if 資料庫中 此使用者喜歡食譜list中 已有紀錄:
            則 do nothing
        else:
            把此食譜寫入使用者喜歡的食譜list裡
        '''

        # TODO 機器人回覆文字&卡片輪播一起
        # TODO 我喜歡 xxxx 改成 斷句
        # TODO 卡片可以擴建到5~6張?

        # TODO 照片or語音認錯~~~點選都不是?? quick reply or 最後一張卡片呈現 (告訴user要怎麼弄) ???????????

        # TODO 存入喜用者喜好的LIST ~~~ 機器人回吐 "已收藏" ??? 顯示已收藏食譜  & -> beta

        Query = (
            f"INSERT INTO `ratatouille-ai.recipebot.test_user_recipe`(`id`, `user_id`, `recipe_id`,`my_like`) VALUES "
            f"((select count(id)+1 from ratatouille-ai.recipebot.test_user_recipe), '{user_id}', {get_data}, 'Y'); "
        )
        query_job = bq_client.query(Query)
        see_result = query_job.result()
        print(see_result)




