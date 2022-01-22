import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os

# use json file to login email
with open("keys/email.json", "r", encoding="utf-8") as f:
    email_login = json.load(f)


def send_email(msg, user_nickname):

    # 信件主旨
    subject = "來自「愛廚易AI-touille」使用者：" + user_nickname

    # 寄件者
    sender = email_login['email']
    sender_password = email_login['password']

    # 收件者
    recipient = email_login['email']

    # 信件內容存在msg這個變數裡面使用

    # 附加圖片
    # pic_path = "test.jpg" # 圖片路徑+檔名+副檔名
    # 如果要附加圖片要去寄信設定 一、建立信件，把content.attach(MIMEImage(Path(pic_path).read_bytes())) 取消註解

    # ========================  !!!!!!!!  以下為寄信設定不要更改 (除非要開啟附加圖片功能)  !!!!!!!!  ============================================
    # 一、建立信件
    # 此區為信件組合之固定設定
    content = MIMEMultipart()  # 信件組合，利用MIMEMultipart物件即可進行各欄位的資料設定
    content["Subject"] = subject  # 信件主旨
    content["From"] = sender  # 寄件者
    content["To"] = recipient  # 收件者
    content.attach(MIMEText(msg))  # 信件內容
    # content.attach(MIMEImage(Path(pic_path).read_bytes()))  #附加圖片  <<<<< 只有這裡可以動：取消註解，開啟附加圖片功能

    # 二、設定SMTP伺服器(SMTP Server)
    # 此區為採Gmail寄件之固定設定
    with smtplib.SMTP(host="smtp.gmail.com", port=587) as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(user=sender, password=sender_password)  # 登入寄件者gmail
            smtp.send_message(msg=content, from_addr=sender, to_addrs=recipient)  # 寄送郵件
            # print("Complete!")
        except Exception as e:
            print("Error message: ", e)

# send_email("TEST text: user message, this is Beta testing email service", "Beta Lin")
