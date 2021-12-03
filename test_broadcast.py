from linebot import (LineBotApi, WebhookHandler)
from linebot.models import (TextSendMessage)

# 拿user資料
from services.user_service import UserService
import os

@classmethod
def line_user_upload_image(cls, event):
    line_bot_api = LineBotApi(
            channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
        # line_bot_api = LineBotApi("nYkS9nDhile6wvYvppkxXjYQhTYsyxvbShF8uPJdJWxCqebMfySRu++zi+SdzMwAlcCGNhkxlDhjNUdkfe7gHH69ivGWWruMFZG8tlzaoWgSt/o/D8p/mnV877LWj38+3sfOC0r4Ryujtt70fziBrQdB04t89/1O/w1cDnyilFU=")

        # TODO：取ID
        # TODO：改成line_bot_api.multicast(['USERID_LIST'], TextSendMessage(text='HelloWorld!YAYA'))
        # 取get_user_id疑似失敗，若手動輸入ID，推送可成功

    # user_id = event.source.user_id

    # print(user_id)

    '''
    指定推播
    https://github.com/line/line-bot-sdk-python
    '''
    # # 單一推送
    # # line_bot_api.push_message('USER_ID', TextSendMessage(text='Hello World!'))

    # 群體推送
    # line_bot_api.multicast(['ID1', 'ID2'], TextSendMessage(text='Hello World!'))
    line_bot_api.multicast([event.source.user_id], TextSendMessage(text='Hello World!'))