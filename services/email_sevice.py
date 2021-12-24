# 寄信程式
# 此檔名已通過經Google授權，請勿更改檔名，如要更改需重新取得Goole授權(sender_password)

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib , os
from services.user_service import UserService

from linebot import (
    LineBotApi
)

class EmailService:
    line_bot_api = LineBotApi(
        channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])

    @classmethod
    def line_user_leave_message(cls,event):

        #取個資
        user_object = cls.UserService.get_user(event.source.user_id)
        user_nickname = user_object.line_user_nickname

        # 信件主旨
        subject = "來自「愛廚易AI-touille」使用者：" + user_nickname

        # 寄件者
        sender = "AItouille.TW@gmail.com"
        sender_password = os.environ["GMAIL_PASSWORD"]

        # 收件者
        recipient = "AItouille.TW@gmail.com"

        # 信件內容
        text = app.manageForm.message

        # 附加圖片
        # pic_path = "test.jpg" # 圖片路徑+檔名+副檔名
        # 如果要附加圖片要去寄信設定 一、建立信件，把ontent.attach(MIMEImage(Path(pic_path).read_bytes())) 取消註解


        # ========================  !!!!!!!!  以下為寄信設定不要更改 (除非要開啟附加圖片功能)  !!!!!!!!  ============================================

        # 一、建立信件
        # 此區為信件組合之固定設定
        content = MIMEMultipart() # 信件組合，利用MIMEMultipart物件即可進行各欄位的資料設定
        content["subject"] = subject # 信件主旨
        content["from"] = sender # 寄件者
        content["to"] = recipient # 收件者
        content.attach(MIMEText(text)) #信件內容
        # ontent.attach(MIMEImage(Path(pic_path).read_bytes()))  #附加圖片  <<<<< 只有這裡可以動：取消註解，開啟附加圖片功能

        # 二、設定SMTP伺服器(SMTP Server)
        # 此區為採Gmail寄件之固定設定
        with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
            try:
                smtp.ehlo()  # 驗證SMTP伺服器
                smtp.starttls()  # 建立加密傳輸
                smtp.login(sender, sender_password)  # 登入寄件者gmail
                smtp.send_message(content)  # 寄送郵件
                print("Complete!")
            except Exception as e:
                print("Error message: ", e)

        # =======================================  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!   ==============================================