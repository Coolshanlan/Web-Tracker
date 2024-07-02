from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def load_email_key():
    with open('./email_key','r') as keyfile:
        return str(keyfile.read())

email_key=load_email_key()

def send_email(subject='Program Reminder',to_email=["joey0201020123@gmail.com"],content_text='remind'):
    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = subject  #郵件標題
    content["from"] = "coolshanlan@gmail.com" #寄件者
    content["to"] = ','.join(to_email) #收件者
    content.attach(MIMEText(content_text))  #郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(content["from"], email_key)  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)
