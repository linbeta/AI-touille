## ========== 設定line_bot  ==========
import os

CHANNEL_ACCESS_TOKEN = os.environ["token"]
CHANNEL_SECRET = os.environ["secret"]

## ========== 新增 Rich menus，並透過line API 取得 rich_menu_link ==========

import requests , json

headers = {"Authorization":"Bearer "+CHANNEL_ACCESS_TOKEN,"Content-Type":"application/json"}

# body = {
#     "size": {"width": 2500, "height": 635},
#     "selected": "true",
#     "name": "圖文選單richmenu",
#     "chatBarText": " ↑↓ 開合選單",
#     "areas":[
#         {
#           "bounds": {"x": 0, "y": 0, "width": 625, "height": 635},
#           "action": {"type": "uri", "uri": "https://line.me/R/nv/camera/"}
#         },
#         {
#           "bounds": {"x": 625, "y": 0, "width": 625, "height": 635},
#           "action": {"type": "uri", "uri": "https://line.me/R/nv/cameraRoll/multi"}
#         },
#         {
#           "bounds": {"x": 1250, "y": 0, "width": 625, "height": 635},
#           "action": {"type": "uri", "uri": "https://docs.google.com/spreadsheets/d/1xlbx5NS3CkHv5dK9CyHWHmiRuEJgKwlRymHE_dtu5y4/edit?usp=sharing"}
#         },
#         {
#           "bounds": {"x": 1875, "y": 0, "width": 625, "height": 635},
#           "action": {"type": "uri", "uri": "https://line.me/R/nv/recommendOA/@096oeofl"}
#         }
#     ]
#   }
#
# req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
#                        headers=headers,data=json.dumps(body).encode('utf-8'))#
# print(req.text)


# ========== 在line_bot上設定 Rich menus 的圖片，透過 line-bot-sdk-python 來將圖片掛上該圖文選單 ==========

from linebot import (LineBotApi, WebhookHandler)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
with open("richmenu.jpg",'rb') as f:
    line_bot_api.set_rich_menu_image("richmenu-0def4b504ecb97f750a43476255886a3", "image/jpeg", f)


## ========== 啟用 Rich menus，透過發送 request ==========
import requests

headers = {"Authorization":"Bearer "+CHANNEL_ACCESS_TOKEN,"Content-Type":"application/json"}

req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/richmenu-0def4b504ecb97f750a43476255886a3',
                       headers=headers)

print(req.text)


# ## ========== 查看所有 Rich menus(最多100組) ==========
#
# from linebot import (LineBotApi, WebhookHandler)
#
# line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
#
# rich_menu_list = line_bot_api.get_rich_menu_list()
#
# for rich_menu in rich_menu_list:
#     print(rich_menu.rich_menu_id)


## ========== 刪除Rich menus==========
# from linebot import (LineBotApi, WebhookHandler)
# line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
# line_bot_api.delete_rich_menu('richmenu-9b9151e2110b5d616932a7bd8e18a09a')
#
# rich_menu_list = line_bot_api.get_rich_menu_list()
# for rich_menu in rich_menu_list:
#     print(rich_menu.rich_menu_id)