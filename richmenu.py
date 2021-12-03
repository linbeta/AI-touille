## 只須設定圖片格式及檔名 (搜尋!)

## ========== 設定line_bot  ==========
import os

CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]


## ========== 新增 Rich menus，並透過line API 取得 rich_menu_link ==========
## (! 配合圖片格式修改參數)

import requests , json

headers = {"Authorization":"Bearer "+CHANNEL_ACCESS_TOKEN,"Content-Type":"application/json"}

body = {
    "size": {"width": 2500, "height": 599},
    "selected": "true",
    "name": "圖文選單richmenu",
    "chatBarText": " ▲ ▼ 選單",
    "areas":[
        {
          "bounds": {"x": 0, "y": 0, "width": 625, "height": 635},
          "action": {"type": "uri", "uri": "https://line.me/R/nv/camera/"}
        },
        {
          "bounds": {"x": 625, "y": 0, "width": 625, "height": 635},
          "action": {"type": "uri", "uri": "https://line.me/R/nv/cameraRoll/multi"},
        },
        {
          "bounds": {"x": 1250, "y": 0, "width": 625, "height": 635},
          "action": {"type": "uri", "uri": "https://line.me/R/nv/recommendOA/@096oeofl"}
        },
        {
          "bounds": {"x": 1875, "y": 0, "width": 625, "height": 635},
          "action": {"type": "uri", "uri": "https://evelynlee.github.io/AItouille/"}
        }
    ]
  }

req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
                       headers=headers,data=json.dumps(body).encode('utf-8'))#

richmenuId = json.loads(req.text).get("richMenuId")

print(richmenuId)

# ========== 在line_bot上設定 Rich menus 的圖片，透過 line-bot-sdk-python 來將圖片掛上該圖文選單 ==========

from linebot import (LineBotApi, WebhookHandler)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

## (! 配合圖片修改檔名"richmenu.jpg"及圖片形式"image/jpeg")
with open("pic/richmenu.jpg",'rb') as f:
    line_bot_api.set_rich_menu_image(richmenuId, "image/jpeg", f)


## ========== 啟用 Rich menus，透過發送 request ==========
import requests

headers = {"Authorization":"Bearer "+CHANNEL_ACCESS_TOKEN,"Content-Type":"application/json"}

req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/'+richmenuId,
                       headers=headers)
print(req.text)


# # ========== 查看所有 Rich menus(最多100組) ==========
#
# from linebot import (LineBotApi, WebhookHandler)
#
# line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
#
# rich_menu_list = line_bot_api.get_rich_menu_list()
#
# for rich_menu in rich_menu_list:
#     print(rich_menu.rich_menu_id)


# # ========== 刪除Rich menus==========
# from linebot import (LineBotApi, WebhookHandler)
# line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
# line_bot_api.delete_rich_menu('richmenu-6479255f4a62971310f0dec0fb352c54')
#
# rich_menu_list = line_bot_api.get_rich_menu_list()
# for rich_menu in rich_menu_list:
#     print(rich_menu.rich_menu_id)